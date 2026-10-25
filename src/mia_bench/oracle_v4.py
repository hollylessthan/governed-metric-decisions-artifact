from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .expanded_worlds_v3 import ExpandedWorldV3, MetricSpecV3, MetricVersionV3, PolicyV3, RelationshipV3
from .oracle_v3 import CanonicalRequestV3


@dataclass(frozen=True)
class OracleResultV4:
    decision: str
    authority_valid: bool
    platform_executable: Optional[bool]
    reasons: Tuple[str, ...]
    required_platform_capabilities: Tuple[str, ...]
    resolved_dimension_paths: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()


def _resolve_metric(world: ExpandedWorldV3, ref: str) -> Tuple[str, ...]:
    if ref in world.metrics:
        return (ref,)
    direct = [name for name, metric in world.metrics.items() if ref in metric.aliases]
    aliased = list(world.aliases.get(ref, ()))
    return tuple(dict.fromkeys(direct + aliased))


def _versions_over_interval(metric: MetricSpecV3, start: int, end: int) -> Tuple[MetricVersionV3, ...]:
    return tuple(v for v in metric.versions if v.valid_from <= end and (v.valid_to is None or start <= v.valid_to))


def _version_covers_interval(version: MetricVersionV3, start: int, end: int) -> bool:
    return version.valid_from <= start and (version.valid_to is None or end <= version.valid_to)


def _direction_safe(rel: RelationshipV3, source: str, target: str) -> bool:
    """Return whether traversing this relationship preserves source-side measure grain."""
    if not rel.fanout_safe:
        return False
    if rel.left_entity == source and rel.right_entity == target:
        cardinality = rel.cardinality
    elif rel.right_entity == source and rel.left_entity == target:
        cardinality = {
            "many_to_one": "one_to_many",
            "one_to_many": "many_to_one",
            "one_to_one": "one_to_one",
            "many_to_many": "many_to_many",
        }.get(rel.cardinality, rel.cardinality)
    else:
        raise ValueError("relationship does not connect requested entities")
    return cardinality in {"many_to_one", "one_to_one"}


def _neighbors(world: ExpandedWorldV3, entity: str):
    for rel in world.relationships:
        if rel.left_entity == entity:
            yield rel.right_entity, _direction_safe(rel, entity, rel.right_entity)
        elif rel.right_entity == entity:
            yield rel.left_entity, _direction_safe(rel, entity, rel.left_entity)


def _find_dimension_path(world: ExpandedWorldV3, metric: MetricSpecV3, dimension: str) -> Tuple[str, Tuple[str, ...]]:
    if dimension in metric.direct_dimensions:
        return "direct", (metric.base_entity,)

    owners = {name for name, entity in world.entities.items() if dimension in entity.dimensions}
    if not owners:
        return "unavailable", ()

    queue = deque([(metric.base_entity, (metric.base_entity,), True)])
    seen = {(metric.base_entity, True)}
    unsafe_path: Tuple[str, ...] = ()
    while queue:
        entity, path, safe_so_far = queue.popleft()
        if entity in owners and entity != metric.base_entity:
            if safe_so_far:
                return "reachable_safe", path
            if not unsafe_path:
                unsafe_path = path
        for nxt, hop_safe in _neighbors(world, entity):
            new_safe = safe_so_far and hop_safe
            state = (nxt, new_safe)
            if nxt in path or state in seen:
                continue
            seen.add(state)
            queue.append((nxt, path + (nxt,), new_safe))
    if unsafe_path:
        return "reachable_unsafe", unsafe_path
    return "unavailable", ()


def _explicit_path_status(world: ExpandedWorldV3, path: Tuple[str, ...]) -> Tuple[bool, bool]:
    if len(path) < 2:
        return True, True
    for left, right in zip(path, path[1:]):
        rel = next((r for r in world.relationships if {r.left_entity, r.right_entity} == {left, right}), None)
        if rel is None:
            return False, False
        if not _direction_safe(rel, left, right):
            return True, False
    return True, True


def _required_capabilities(request: CanonicalRequestV3, metric: MetricSpecV3) -> Tuple[str, ...]:
    caps: List[str] = ["single_metric"]
    if request.dimensions:
        caps.append("group_by")
    if metric.aggregation == "ratio":
        caps.append("ratio")
    if metric.aggregation.startswith("snapshot"):
        caps.append("snapshot")
    if request.calendar_kind == "fiscal":
        caps.append("fiscal_period")
    if request.target_currency is not None and any(v.currency for v in metric.versions):
        caps.append("currency_conversion")
    return tuple(dict.fromkeys(caps))


def _policy_applies(policy: PolicyV3, metric_name: str) -> bool:
    return not policy.scoped_metrics or metric_name in policy.scoped_metrics


def evaluate_v4(world: ExpandedWorldV3, request: CanonicalRequestV3) -> OracleResultV4:
    hard: List[str] = []
    clarify: List[str] = []
    resolved_paths: List[Tuple[str, Tuple[str, ...]]] = []

    if request.role not in world.authorized_roles:
        return OracleResultV4("REJECT", False, None, ("principal_not_authorized",), ())

    candidates = _resolve_metric(world, request.metric_ref)
    if not candidates:
        return OracleResultV4("REJECT", False, None, ("reference_missing",), ())
    if len(candidates) > 1:
        return OracleResultV4("CLARIFY", False, None, ("reference_ambiguous",), ())
    metric = world.metrics[candidates[0]]

    for dimension in request.dimensions:
        status, path = _find_dimension_path(world, metric, dimension)
        if status in {"direct", "reachable_safe"}:
            resolved_paths.append((dimension, path))
        elif status == "reachable_unsafe":
            hard.append("dimension_path_fanout_unsafe")
            resolved_paths.append((dimension, path))
        else:
            hard.append("dimension_not_supported")

    if request.entity_path:
        exists, safe = _explicit_path_status(world, request.entity_path)
        if not exists:
            hard.append("entity_path_unavailable")
        elif not safe:
            hard.append("fanout_unsafe")

    explicit_version: Optional[MetricVersionV3] = None
    if request.version_hint:
        explicit_version = next((v for v in metric.versions if v.version == request.version_hint), None)
        if explicit_version is None:
            hard.append("version_missing")

    chosen: Optional[MetricVersionV3] = None

    # A start-only interval stays unresolved: the benchmark explicitly forbids
    # silently inventing a present/current end bound. An end-only interval is
    # different: the governed metric validity provides a documented lower bound.
    # It can therefore resolve when exactly one additive-over-time definition
    # covers the entire governed interval. Non-additive metrics still need a
    # start because the window itself is material to their meaning.
    if request.start_year is not None and request.end_year is None:
        clarify.append("time_scope_incomplete")
    elif request.start_year is None and request.end_year is not None:
        if request.end_year > world.clock_year:
            hard.append("time_scope_future")
        else:
            governed_start = min(v.valid_from for v in metric.versions)
            applicable = _versions_over_interval(metric, governed_start, request.end_year)
            if not applicable:
                hard.append("no_applicable_version")
            elif explicit_version is not None and not _version_covers_interval(explicit_version, governed_start, request.end_year):
                hard.append("version_not_applicable")
            elif request.version_hint is None and len(applicable) > 1:
                clarify.append("version_ambiguous")
            elif len(applicable) == 1:
                chosen = applicable[0]
                if not chosen.additive_over_time:
                    clarify.append("time_scope_incomplete")
    elif request.start_year is not None and request.end_year is not None:
        if request.start_year > request.end_year:
            hard.append("time_scope_invalid")
        elif request.end_year > world.clock_year:
            hard.append("time_scope_future")
        else:
            applicable = _versions_over_interval(metric, request.start_year, request.end_year)
            if not applicable:
                hard.append("no_applicable_version")
            elif explicit_version is not None and not _version_covers_interval(explicit_version, request.start_year, request.end_year):
                hard.append("version_not_applicable")
            elif request.version_hint is None and len(applicable) > 1:
                clarify.append("version_ambiguous")
            elif len(applicable) == 1:
                chosen = applicable[0]
    elif explicit_version is not None:
        if explicit_version.valid_from > world.clock_year:
            hard.append("version_not_applicable")
    elif len(metric.versions) > 1:
        clarify.append("version_ambiguous_all_time")

    if chosen is None:
        if explicit_version is not None:
            chosen = explicit_version
        elif request.start_year is not None and request.end_year is not None:
            applicable = _versions_over_interval(metric, request.start_year, request.end_year)
            if len(applicable) == 1:
                chosen = applicable[0]
        elif request.start_year is None and request.end_year is not None:
            governed_start = min(v.valid_from for v in metric.versions)
            applicable = _versions_over_interval(metric, governed_start, request.end_year)
            if len(applicable) == 1:
                chosen = applicable[0]
        elif len(metric.versions) == 1:
            chosen = metric.versions[0]

    if request.certification_requirement == "certified" and chosen is not None and not chosen.certified:
        hard.append("certification_required")

    if request.temporal_operation == "sum" and chosen is not None and not chosen.additive_over_time:
        hard.append("semi_additive_time_violation")

    if metric.aggregation.startswith("snapshot") and request.start_year is not None and request.end_year is not None:
        if request.temporal_operation is None:
            clarify.append("snapshot_point_missing")

    if request.target_currency is not None and chosen is not None and chosen.currency:
        if request.target_currency != chosen.currency and not world.fx_context_available:
            clarify.append("fx_context_missing")

    for policy in world.policies:
        if policy.role != request.role or not _policy_applies(policy, metric.name):
            continue
        if metric.name in policy.denied_metrics:
            hard.append("metric_not_permitted")
        for dimension in request.dimensions:
            if dimension in policy.denied_dimensions:
                hard.append("dimension_not_permitted")
        if policy.required_row_scope:
            if request.row_scope is None:
                clarify.append("row_scope_missing")
            elif request.row_scope != policy.required_row_scope:
                hard.append("row_scope_not_permitted")

    if request.calendar_kind not in {"calendar", "fiscal"}:
        hard.append("calendar_kind_invalid")

    required_caps = _required_capabilities(request, metric)
    platform_executable = all(cap in world.compiler_capabilities for cap in required_caps)

    if hard:
        decision, authority_valid = "REJECT", False
    elif clarify:
        decision, authority_valid = "CLARIFY", False
    else:
        decision, authority_valid = "ALLOW", True

    return OracleResultV4(
        decision,
        authority_valid,
        platform_executable,
        tuple(dict.fromkeys(hard + clarify)),
        required_caps,
        tuple(resolved_paths),
    )
