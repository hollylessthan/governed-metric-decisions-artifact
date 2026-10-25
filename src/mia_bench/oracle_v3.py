from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .worlds_v2 import MetricSpec, MetricVersion, Policy, World


@dataclass(frozen=True)
class CanonicalRequestV3:
    """Gold-side semantic request for MIA-Bench v3.

    Fields describe what the requester actually asked for. They intentionally do
    not contain label-bearing switches such as `required_capability`,
    `aggregate_over_time`, or `fiscal_period`.
    """

    metric_ref: str
    dimensions: Tuple[str, ...] = ()
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    version_hint: Optional[str] = None
    role: str = "analyst"
    entity_path: Tuple[str, ...] = ()
    temporal_operation: Optional[str] = None  # point | sum | average
    calendar_kind: str = "calendar"  # calendar | fiscal
    target_currency: Optional[str] = None
    row_scope: Optional[str] = None
    certification_requirement: Optional[str] = None  # certified | None


@dataclass(frozen=True)
class OracleResultV3:
    decision: str
    authority_valid: bool
    platform_executable: Optional[bool]
    reasons: Tuple[str, ...]
    required_platform_capabilities: Tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "authority_valid": self.authority_valid,
            "platform_executable": self.platform_executable,
            "reasons": list(self.reasons),
            "required_platform_capabilities": list(self.required_platform_capabilities),
        }


def _resolve_metric(world: World, ref: str) -> Tuple[str, ...]:
    if ref in world.metrics:
        return (ref,)
    direct = [name for name, metric in world.metrics.items() if ref in metric.aliases]
    aliased = list(world.aliases.get(ref, ()))
    return tuple(dict.fromkeys(direct + aliased))


def _versions_over_interval(metric: MetricSpec, start: int, end: int) -> Tuple[MetricVersion, ...]:
    return tuple(
        version
        for version in metric.versions
        if version.valid_from <= end and (version.valid_to is None or start <= version.valid_to)
    )


def _version_covers_interval(version: MetricVersion, start: int, end: int) -> bool:
    return version.valid_from <= start and (version.valid_to is None or end <= version.valid_to)


def _path_status(world: World, entities: Tuple[str, ...]) -> Tuple[bool, bool]:
    """Return (exists, fanout_safe) for the entire requested path."""
    if len(entities) < 2:
        return True, True
    for left, right in zip(entities, entities[1:]):
        rel = next(
            (
                candidate
                for candidate in world.relationships
                if (candidate.left_entity, candidate.right_entity) == (left, right)
                or (candidate.right_entity, candidate.left_entity) == (left, right)
            ),
            None,
        )
        if rel is None:
            return False, False
        if not rel.fanout_safe:
            return True, False
    return True, True


def _required_capabilities(request: CanonicalRequestV3, metric: MetricSpec) -> Tuple[str, ...]:
    caps: List[str] = ["single_metric"]
    if request.dimensions:
        caps.append("group_by")
    if metric.aggregation == "ratio":
        caps.append("ratio")
    if metric.aggregation.startswith("snapshot"):
        caps.append("snapshot")
    if request.calendar_kind == "fiscal":
        caps.append("fiscal_period")
    if request.target_currency is not None and metric.versions and any(v.currency for v in metric.versions):
        caps.append("currency_conversion")
    return tuple(dict.fromkeys(caps))


def _policy_applies(policy: Policy, metric_name: str) -> bool:
    return not policy.scoped_metrics or metric_name in policy.scoped_metrics


def evaluate_v3(world: World, request: CanonicalRequestV3) -> OracleResultV3:
    """Independent reference semantics for the redesigned benchmark.

    `decision` reflects semantic/governance authority. Backend feasibility is
    reported separately in `platform_executable`; a semantically valid request
    does not become invalid merely because the current compiler lacks a feature.

    If an explicit governed version is requested without a time interval, that
    request is interpreted over the chosen version's own validity interval
    (clipped at the world clock when the version is open-ended). It is not an
    implicit request to apply that definition across all historical versions.
    """

    hard: List[str] = []
    clarify: List[str] = []

    if request.role not in world.authorized_roles:
        return OracleResultV3("REJECT", False, None, ("principal_not_authorized",), ())

    candidates = _resolve_metric(world, request.metric_ref)
    if not candidates:
        return OracleResultV3("REJECT", False, None, ("reference_missing",), ())
    if len(candidates) > 1:
        return OracleResultV3("CLARIFY", False, None, ("reference_ambiguous",), ())

    metric = world.metrics[candidates[0]]

    for dimension in request.dimensions:
        if dimension not in metric.dimensions:
            hard.append("dimension_not_supported")

    explicit_version: Optional[MetricVersion] = None
    if request.version_hint:
        explicit_version = next((v for v in metric.versions if v.version == request.version_hint), None)
        if explicit_version is None:
            hard.append("version_missing")

    if (request.start_year is None) != (request.end_year is None):
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
            elif explicit_version is not None and not _version_covers_interval(
                explicit_version, request.start_year, request.end_year
            ):
                hard.append("version_not_applicable")
            elif request.version_hint is None and len(applicable) > 1:
                clarify.append("version_ambiguous")
    elif explicit_version is not None:
        # The version itself supplies the governed interval. An open-ended
        # validity range ends at the world's current clock for this evaluation.
        if explicit_version.valid_from > world.clock_year:
            hard.append("version_not_applicable")
    elif request.version_hint is None and len(metric.versions) > 1:
        clarify.append("version_ambiguous_all_time")

    chosen: Optional[MetricVersion] = None
    if explicit_version is not None:
        chosen = explicit_version
    elif request.start_year is not None and request.end_year is not None:
        applicable = _versions_over_interval(metric, request.start_year, request.end_year)
        if len(applicable) == 1:
            chosen = applicable[0]
    elif len(metric.versions) == 1:
        chosen = metric.versions[0]

    if request.certification_requirement == "certified" and chosen is not None and not chosen.certified:
        hard.append("certification_required")

    if request.temporal_operation == "sum" and chosen is not None and not chosen.additive_over_time:
        hard.append("semi_additive_time_violation")

    # A coarse interval such as "for 2025" does not identify which snapshot of
    # a snapshot metric is intended. The blind non-author audit surfaced this as
    # a material ambiguity. An explicit point operation may authorize a snapshot;
    # an explicit sum remains a hard semi-additivity violation above.
    if (
        metric.aggregation.startswith("snapshot")
        and request.start_year is not None
        and request.end_year is not None
        and request.temporal_operation is None
    ):
        clarify.append("snapshot_point_missing")

    if request.target_currency is not None and chosen is not None and chosen.currency:
        if request.target_currency != chosen.currency and not world.fx_context_available:
            clarify.append("fx_context_missing")

    path_exists, fanout_safe = _path_status(world, request.entity_path)
    if not path_exists:
        hard.append("entity_path_unavailable")
    elif not fanout_safe:
        hard.append("fanout_unsafe")

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
        decision = "REJECT"
        authority_valid = False
    elif clarify:
        decision = "CLARIFY"
        authority_valid = False
    else:
        decision = "ALLOW"
        authority_valid = True

    return OracleResultV3(
        decision=decision,
        authority_valid=authority_valid,
        platform_executable=platform_executable,
        reasons=tuple(dict.fromkeys(hard + clarify)),
        required_platform_capabilities=required_caps,
    )
