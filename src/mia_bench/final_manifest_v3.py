from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from typing import Dict, Iterable, List, Tuple

from .expanded_serialization_v3 import world_sha256, world_to_dict
from .expanded_worlds_v3 import ExpandedWorldV3, MetricSpecV3, build_expanded_worlds
from .natural_surfaces_v3 import (
    realize,
    stable_style_order,
    validate_no_conflicting_surfaces,
    validate_no_label_leakage,
)
from .oracle_v3 import CanonicalRequestV3
from .oracle_v4 import OracleResultV4, evaluate_v4


FINAL_SCENARIOS = 600
SCENARIOS_PER_WORLD = 150
COUNTERFACTUAL_ROWS_PER_WORLD = 60
COUNTERFACTUAL_PAIRS_PER_WORLD = 30
BASE_ROWS_PER_DECISION_PER_WORLD = 30
HOLDOUT_ROWS_PER_WORLD = 30
HOLDOUT_CF_PAIRS_PER_WORLD = 6
HOLDOUT_BASE_PER_DECISION_PER_WORLD = 6
MAX_BASE_PER_MECHANISM = 5
MAX_CF_PAIRS_PER_MUTATION = 5
MAX_REQUEST_ONLY_RULE_ACCURATE_COVERAGE = 0.30
MAX_REQUEST_ONLY_NB_ACCURACY = 0.70


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _request_dict(request: CanonicalRequestV3) -> dict:
    value = asdict(request)
    value["dimensions"] = list(request.dimensions)
    value["entity_path"] = list(request.entity_path)
    return value


def _request_hash(request: CanonicalRequestV3) -> str:
    return hashlib.sha256(_canonical_json(_request_dict(request)).encode()).hexdigest()


def _expected_action(oracle: OracleResultV4) -> str:
    """Primary endpoint is semantic/governance authority, not compiler support."""
    return "EXECUTE" if oracle.decision == "ALLOW" else "NON_EXECUTE_AUTHORITY"


def _platform_target(oracle: OracleResultV4) -> str:
    if oracle.platform_executable is None:
        return "NOT_APPLICABLE"
    return "EXECUTABLE" if oracle.platform_executable else "NON_EXECUTABLE"


def _gold_signature(oracle: OracleResultV4) -> Tuple[object, ...]:
    return (
        oracle.decision,
        tuple(oracle.reasons),
        oracle.authority_valid,
        oracle.platform_executable,
        tuple(oracle.required_platform_capabilities),
        _expected_action(oracle),
        _platform_target(oracle),
    )


def _scenario_id(world: ExpandedWorldV3, request: CanonicalRequestV3, *, namespace: str, side: str = "") -> str:
    raw = f"mia-bench-final-v3|{world.name}|{namespace}|{side}|{_request_hash(request)}|{world_sha256(world)}"
    return "MB3-" + hashlib.sha256(raw.encode()).hexdigest()[:16].upper()


def _row(
    world: ExpandedWorldV3,
    request: CanonicalRequestV3,
    *,
    family: str,
    namespace: str,
    counterfactual_group: str | None = None,
    mutation: str | None = None,
    side: str = "",
) -> dict:
    oracle = evaluate_v4(world, request)
    scenario_id = _scenario_id(world, request, namespace=namespace, side=side)
    style_seed = counterfactual_group or scenario_id
    style = stable_style_order(style_seed)[0]
    surface = realize(world, request, style=style)
    validate_no_label_leakage(surface.text)
    return {
        "schema_version": "mia-bench-final-v3.1",
        "scenario_id": scenario_id,
        "world": world.name,
        "world_hash": world_sha256(world),
        "world_payload": world_to_dict(world),
        "principal": request.role,
        "taxonomy_family": family,
        "canonical_request": _request_dict(request),
        "request_hash": _request_hash(request),
        "surface_style": style,
        "surface": surface.text,
        "semantic_markers": list(surface.semantic_markers),
        "gold_decision": oracle.decision,
        "gold_reasons": list(oracle.reasons),
        "authority_valid": oracle.authority_valid,
        "platform_executable": oracle.platform_executable,
        "platform_target": _platform_target(oracle),
        "required_platform_capabilities": list(oracle.required_platform_capabilities),
        "expected_system_action": _expected_action(oracle),
        "gold_signature": list(_gold_signature(oracle)),
        "counterfactual_group": counterfactual_group,
        "counterfactual_mutation": mutation,
        "split": None,
    }


def _default_role(world: ExpandedWorldV3) -> str:
    return "finance" if world.name == "finance" else "analyst"


def _direct_request(world: ExpandedWorldV3, metric_name: str, year: int, dimension: str | None = None) -> CanonicalRequestV3:
    metric = world.metrics[metric_name]
    temporal_operation = "point" if metric.aggregation.startswith("snapshot") else None
    return CanonicalRequestV3(
        metric_name,
        dimensions=(dimension,) if dimension else (),
        start_year=year,
        end_year=year,
        role=_default_role(world),
        temporal_operation=temporal_operation,
    )


def _matching_version(metric: MetricSpecV3, year: int):
    matches = [v for v in metric.versions if v.valid_from <= year and (v.valid_to is None or year <= v.valid_to)]
    return matches[0] if len(matches) == 1 else None


def _base_candidate_pool(world: ExpandedWorldV3) -> List[Tuple[str, CanonicalRequestV3]]:
    """Construct base scenarios from the full governed-mechanism inventory.

    Selection happens later with a per-mechanism cap, so this pool can be broad.
    Gold is always assigned by the independent oracle.
    """
    pool: List[Tuple[str, CanonicalRequestV3]] = []
    role = _default_role(world)

    for metric_name, metric in sorted(world.metrics.items()):
        for year in (2023, 2024, 2025):
            ordinary = _direct_request(world, metric_name, year)
            pool.append(("ordinary", ordinary))

            for dimension in metric.direct_dimensions[:2]:
                pool.append(("ordinary_grouping", replace(ordinary, dimensions=(dimension,))))

            for alias in metric.aliases[:1]:
                pool.append(("unique_alias_resolution", replace(ordinary, metric_ref=alias)))

            version = _matching_version(metric, year)
            if version is not None:
                pool.append(("explicit_valid_version", replace(ordinary, version_hint=version.version)))
                pool.append(("certification_satisfied", replace(ordinary, certification_requirement="certified")))

            pool.append(("fiscal_semantics", replace(ordinary, calendar_kind="fiscal")))
            pool.append(("principal_not_authorized", replace(ordinary, role="guest")))
            pool.append(("version_missing", replace(ordinary, version_hint="v99")))
            pool.append(("time_scope_future", replace(ordinary, start_year=2027, end_year=2027)))
            pool.append(("time_scope_invalid", replace(ordinary, start_year=2025, end_year=2024)))
            pool.append(("time_scope_missing_end", replace(ordinary, end_year=None)))
            pool.append(("time_scope_missing_start", replace(ordinary, start_year=None)))

            if metric.aggregation.startswith("snapshot"):
                pool.append(("snapshot_point_missing", replace(ordinary, temporal_operation=None)))
                pool.append(("snapshot_invalid_sum", replace(ordinary, temporal_operation="sum")))

            if version is not None and version.currency:
                fx_request = replace(ordinary, target_currency="EUR")
                family = "fx_context_present" if world.fx_context_available else "fx_context_missing"
                pool.append((family, fx_request))

        if len(metric.versions) > 1:
            pool.append(("version_ambiguous_all_time", CanonicalRequestV3(metric_name, role=role)))
            boundaries = sorted({v.valid_from for v in metric.versions})
            if len(boundaries) >= 2:
                transition = boundaries[-1]
                pool.append((
                    "version_ambiguous_interval",
                    CanonicalRequestV3(metric_name, start_year=transition - 1, end_year=transition, role=role),
                ))
                old = metric.versions[0]
                pool.append((
                    "version_not_applicable",
                    CanonicalRequestV3(metric_name, start_year=transition, end_year=transition, role=role, version_hint=old.version),
                ))

    # Explicitly ambiguous world aliases.
    for alias, targets in sorted(world.aliases.items()):
        if len(targets) > 1:
            for year in (2023, 2024, 2025):
                pool.append(("reference_ambiguous", CanonicalRequestV3(alias, start_year=year, end_year=year, role=role)))

    # Reachable dimensions and explicit relationship paths.
    for metric in world.metrics.values():
        for entity_name, entity in world.entities.items():
            if entity_name == metric.base_entity:
                continue
            for dimension in entity.dimensions[:2]:
                request = _direct_request(world, metric.name, 2025)
                request = replace(request, dimensions=(dimension,))
                result = evaluate_v4(world, request)
                if result.decision == "ALLOW":
                    pool.append(("reachable_dimension_safe", request))
                elif "dimension_path_fanout_unsafe" in result.reasons:
                    pool.append(("reachable_dimension_unsafe", request))

        for rel in world.relationships:
            if metric.base_entity == rel.left_entity:
                other = rel.right_entity
            elif metric.base_entity == rel.right_entity:
                other = rel.left_entity
            else:
                continue
            request = replace(_direct_request(world, metric.name, 2025), entity_path=(metric.base_entity, other))
            result = evaluate_v4(world, request)
            family = "explicit_path_safe" if result.decision == "ALLOW" else "explicit_path_unsafe"
            pool.append((family, request))

    # Policy-specific requests exercise deny, row-scope clarify/reject, and satisfied scope.
    for policy in world.policies:
        metric_names = policy.scoped_metrics or tuple(world.metrics)
        for metric_name in metric_names:
            if metric_name not in world.metrics:
                continue
            metric = world.metrics[metric_name]
            base = CanonicalRequestV3(
                metric_name,
                start_year=2025,
                end_year=2025,
                role=policy.role,
                temporal_operation="point" if metric.aggregation.startswith("snapshot") else None,
            )
            if metric_name in policy.denied_metrics:
                pool.append(("policy_denied_metric", base))
            for dimension in policy.denied_dimensions:
                pool.append(("policy_denied_dimension", replace(base, dimensions=(dimension,))))
            if policy.required_row_scope:
                pool.append(("row_scope_missing", base))
                pool.append(("row_scope_wrong", replace(base, row_scope="wrong_scope")))
                pool.append(("row_scope_satisfied", replace(base, row_scope=policy.required_row_scope)))

    return pool


def _select_balanced_base(world: ExpandedWorldV3) -> List[dict]:
    by_decision_family: Dict[str, Dict[str, List[CanonicalRequestV3]]] = defaultdict(lambda: defaultdict(list))
    seen = set()
    for family, request in _base_candidate_pool(world):
        key = _request_hash(request)
        if key in seen:
            continue
        seen.add(key)
        decision = evaluate_v4(world, request).decision
        by_decision_family[decision][family].append(request)

    rows: List[dict] = []
    for decision in ("ALLOW", "REJECT", "CLARIFY"):
        families = by_decision_family[decision]
        eligible = [name for name, candidates in families.items() if candidates]
        if len(eligible) < 6:
            raise ValueError(f"insufficient mechanism diversity for {world.name}/{decision}: {sorted(eligible)}")
        ranked_families = sorted(
            eligible,
            key=lambda name: hashlib.sha256(f"base-family|{world.name}|{decision}|{name}".encode()).hexdigest(),
        )
        ranked_candidates = {
            name: sorted(
                families[name],
                key=lambda request: hashlib.sha256(f"base-case|{world.name}|{decision}|{name}|{_request_hash(request)}".encode()).hexdigest(),
            )
            for name in ranked_families
        }
        taken = Counter()
        cursor = Counter()
        selected: List[Tuple[str, CanonicalRequestV3]] = []
        while len(selected) < BASE_ROWS_PER_DECISION_PER_WORLD:
            progressed = False
            for family in ranked_families:
                if taken[family] >= MAX_BASE_PER_MECHANISM:
                    continue
                candidates = ranked_candidates[family]
                if cursor[family] >= len(candidates):
                    continue
                selected.append((family, candidates[cursor[family]]))
                cursor[family] += 1
                taken[family] += 1
                progressed = True
                if len(selected) == BASE_ROWS_PER_DECISION_PER_WORLD:
                    break
            if not progressed:
                raise ValueError(
                    f"cannot fill {world.name}/{decision} under mechanism cap {MAX_BASE_PER_MECHANISM}; counts={dict(taken)}"
                )
        for index, (family, request) in enumerate(selected):
            rows.append(_row(world, request, family=family, namespace=f"base-{decision}-{index:02d}"))
    return rows


def _without_matching_policy(world: ExpandedWorldV3, policy_index: int) -> ExpandedWorldV3:
    return replace(world, policies=tuple(p for i, p in enumerate(world.policies) if i != policy_index))


def _remove_relationship(world: ExpandedWorldV3, rel_index: int) -> ExpandedWorldV3:
    return replace(world, relationships=tuple(r for i, r in enumerate(world.relationships) if i != rel_index))


def _mark_relationship_unsafe(world: ExpandedWorldV3, rel_index: int) -> ExpandedWorldV3:
    rels = list(world.relationships)
    rels[rel_index] = replace(rels[rel_index], fanout_safe=False)
    return replace(world, relationships=tuple(rels))


def _remove_authorized_role(world: ExpandedWorldV3, role: str) -> ExpandedWorldV3:
    return replace(world, authorized_roles=tuple(r for r in world.authorized_roles if r != role))


def _set_version_certified(world: ExpandedWorldV3, metric_name: str, version_name: str, certified: bool) -> ExpandedWorldV3:
    metrics = dict(world.metrics)
    metric = metrics[metric_name]
    versions = tuple(replace(v, certified=certified) if v.version == version_name else v for v in metric.versions)
    metrics[metric_name] = replace(metric, versions=versions)
    return replace(world, metrics=metrics)


def _entity_dimensions(world: ExpandedWorldV3, entity_name: str) -> Tuple[str, ...]:
    entity = world.entities.get(entity_name)
    return entity.dimensions if entity else ()


def _authority_pair_candidates(world: ExpandedWorldV3) -> List[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]]:
    candidates: List[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]] = []
    role = _default_role(world)

    # Authorization membership changes are plausible access-control changes.
    if role in world.authorized_roles and len(world.authorized_roles) > 1:
        revoked = _remove_authorized_role(world, role)
        for metric in list(world.metrics.values())[:5]:
            for year in (2024, 2025):
                candidates.append(("authorized_role_membership", world, revoked, _direct_request(world, metric.name, year)))

    # Governed FX context changes without changing the request.
    currency_metrics = [m for m in world.metrics.values() if any(v.currency for v in m.versions)]
    if currency_metrics:
        fx_true = replace(world, fx_context_available=True)
        fx_false = replace(world, fx_context_available=False)
        for metric in currency_metrics:
            for year in (2023, 2024, 2025):
                request = replace(_direct_request(world, metric.name, year), target_currency="EUR")
                candidates.append(("fx_context_available", fx_true, fx_false, request))

    # Policy presence/absence.
    for policy_index, policy in enumerate(world.policies):
        ungoverned = _without_matching_policy(world, policy_index)
        metric_names = policy.scoped_metrics or tuple(world.metrics)
        for metric_name in metric_names:
            if metric_name not in world.metrics:
                continue
            metric = world.metrics[metric_name]
            base = CanonicalRequestV3(
                metric_name,
                start_year=2025,
                end_year=2025,
                role=policy.role,
                temporal_operation="point" if metric.aggregation.startswith("snapshot") else None,
            )
            candidates.append(("policy_presence", ungoverned, world, base))
            for dimension in policy.denied_dimensions:
                candidates.append(("policy_presence", ungoverned, world, replace(base, dimensions=(dimension,))))

    # Certification status is a realistic governance-state change.
    for metric in world.metrics.values():
        for version in metric.versions:
            year = max(2023, version.valid_from)
            if version.valid_to is not None:
                year = min(year, version.valid_to)
            request = replace(
                _direct_request(world, metric.name, year),
                version_hint=version.version,
                certification_requirement="certified",
            )
            uncertified = _set_version_certified(world, metric.name, version.version, False)
            candidates.append(("certification_status", world, uncertified, request))

    # Relationship changes preserve plausible worlds: remove a governed path or
    # mark it unsafe due to duplicate/fanout risk. Never invent impossible cardinalities.
    for rel_index, rel in enumerate(world.relationships):
        if not rel.fanout_safe:
            continue
        removed = _remove_relationship(world, rel_index)
        unsafe = _mark_relationship_unsafe(world, rel_index)
        for metric in world.metrics.values():
            if metric.base_entity == rel.left_entity:
                other = rel.right_entity
            elif metric.base_entity == rel.right_entity:
                other = rel.left_entity
            else:
                continue
            for dimension in _entity_dimensions(world, other)[:2]:
                request = replace(_direct_request(world, metric.name, 2025), dimensions=(dimension,))
                candidates.append(("relationship_path_presence", world, removed, request))
                candidates.append(("relationship_fanout_guard", world, unsafe, request))
    return candidates


def _capability_pair_candidates(world: ExpandedWorldV3) -> List[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]]:
    candidates: List[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]] = []
    for metric in world.metrics.values():
        dim_options = (None,) + tuple(metric.direct_dimensions[:2])
        for year in (2023, 2024, 2025):
            for dimension in dim_options:
                request = _direct_request(world, metric.name, year, dimension)
                oracle = evaluate_v4(world, request)
                if oracle.decision != "ALLOW" or oracle.platform_executable is not True:
                    continue
                for capability in oracle.required_platform_capabilities:
                    if capability == "single_metric" or capability not in world.compiler_capabilities:
                        continue
                    reduced = replace(world, compiler_capabilities=tuple(c for c in world.compiler_capabilities if c != capability))
                    candidates.append((f"compiler_capability:{capability}", world, reduced, request))
    return candidates


def _pair_signature(world_a: ExpandedWorldV3, world_b: ExpandedWorldV3, request: CanonicalRequestV3) -> Tuple[Tuple[object, ...], Tuple[object, ...]]:
    return _gold_signature(evaluate_v4(world_a, request)), _gold_signature(evaluate_v4(world_b, request))


def _select_pairs(
    world: ExpandedWorldV3,
    candidates: Iterable[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]],
    *,
    kind: str,
    count: int,
) -> List[dict]:
    by_mutation: Dict[str, List[Tuple[str, ExpandedWorldV3, ExpandedWorldV3, CanonicalRequestV3]]] = defaultdict(list)
    seen = set()
    for mutation, world_a, world_b, request in candidates:
        sig_a, sig_b = _pair_signature(world_a, world_b, request)
        if sig_a == sig_b:
            continue
        key = (mutation, _request_hash(request), world_sha256(world_a), world_sha256(world_b))
        if key in seen:
            continue
        seen.add(key)
        score = hashlib.sha256(f"cf|{world.name}|{kind}|{mutation}|{_request_hash(request)}".encode()).hexdigest()
        by_mutation[mutation].append((score, world_a, world_b, request))

    mutations = [m for m, values in by_mutation.items() if values]
    mutations.sort(key=lambda m: hashlib.sha256(f"cf-family|{world.name}|{kind}|{m}".encode()).hexdigest())
    for mutation in mutations:
        by_mutation[mutation].sort(key=lambda item: item[0])

    selected = []
    cursor = Counter()
    taken = Counter()
    while len(selected) < count:
        progressed = False
        for mutation in mutations:
            if taken[mutation] >= MAX_CF_PAIRS_PER_MUTATION:
                continue
            values = by_mutation[mutation]
            if cursor[mutation] >= len(values):
                continue
            _, world_a, world_b, request = values[cursor[mutation]]
            cursor[mutation] += 1
            taken[mutation] += 1
            selected.append((mutation, world_a, world_b, request))
            progressed = True
            if len(selected) == count:
                break
        if not progressed:
            raise ValueError(f"insufficient diverse {kind} counterfactual pairs for {world.name}: {dict(taken)}")

    rows: List[dict] = []
    for pair_index, (mutation, world_a, world_b, request) in enumerate(selected):
        group = f"CF-{world.name.upper()}-{kind.upper()}-{pair_index:02d}"
        family = "execution_feasibility" if kind == "capability" else "authority_counterfactual"
        rows.append(_row(world_a, request, family=family, namespace=group, counterfactual_group=group, mutation=mutation, side="A"))
        rows.append(_row(world_b, request, family=family, namespace=group, counterfactual_group=group, mutation=mutation, side="B"))
    return rows


def _diverse_holdout_groups(world_name: str, cf_groups: Dict[str, List[dict]]) -> List[str]:
    by_mutation: Dict[str, List[str]] = defaultdict(list)
    for group, pair in cf_groups.items():
        by_mutation[pair[0]["counterfactual_mutation"]].append(group)
    for mutation in by_mutation:
        by_mutation[mutation].sort(key=lambda g: hashlib.sha256(f"holdout-cf|{world_name}|{g}".encode()).hexdigest())
    mutations = sorted(by_mutation, key=lambda m: hashlib.sha256(f"holdout-cf-family|{world_name}|{m}".encode()).hexdigest())
    chosen: List[str] = []
    cursor = Counter()
    while len(chosen) < HOLDOUT_CF_PAIRS_PER_WORLD:
        for mutation in mutations:
            groups = by_mutation[mutation]
            if cursor[mutation] >= len(groups):
                continue
            chosen.append(groups[cursor[mutation]])
            cursor[mutation] += 1
            if len(chosen) == HOLDOUT_CF_PAIRS_PER_WORLD:
                break
    return chosen


def _diverse_holdout_base(world_name: str, rows: List[dict], decision: str) -> List[dict]:
    candidates = [row for row in rows if row["gold_decision"] == decision]
    by_family: Dict[str, List[dict]] = defaultdict(list)
    for row in candidates:
        by_family[row["taxonomy_family"]].append(row)
    for family in by_family:
        by_family[family].sort(key=lambda r: hashlib.sha256(f"holdout-base|{world_name}|{r['scenario_id']}".encode()).hexdigest())
    families = sorted(by_family, key=lambda f: hashlib.sha256(f"holdout-base-family|{world_name}|{decision}|{f}".encode()).hexdigest())
    if len(families) < HOLDOUT_BASE_PER_DECISION_PER_WORLD:
        raise ValueError(f"holdout lacks mechanism diversity for {world_name}/{decision}")
    return [by_family[family][0] for family in families[:HOLDOUT_BASE_PER_DECISION_PER_WORLD]]


def _assign_splits(rows: List[dict]) -> None:
    by_world: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        by_world[row["world"]].append(row)

    for world_name, world_rows in by_world.items():
        cf_groups: Dict[str, List[dict]] = defaultdict(list)
        base = []
        for row in world_rows:
            if row["counterfactual_group"]:
                cf_groups[row["counterfactual_group"]].append(row)
            else:
                base.append(row)

        selected_cf = _diverse_holdout_groups(world_name, cf_groups)
        holdout_ids = {row["scenario_id"] for group in selected_cf for row in cf_groups[group]}
        for decision in ("ALLOW", "REJECT", "CLARIFY"):
            holdout_ids.update(row["scenario_id"] for row in _diverse_holdout_base(world_name, base, decision))
        for row in world_rows:
            row["split"] = "sealed_holdout" if row["scenario_id"] in holdout_ids else "main"


def generate_final_manifest() -> List[dict]:
    rows: List[dict] = []
    for world in build_expanded_worlds().values():
        rows.extend(_select_balanced_base(world))
        rows.extend(_select_pairs(world, _authority_pair_candidates(world), kind="authority", count=15))
        rows.extend(_select_pairs(world, _capability_pair_candidates(world), kind="capability", count=15))
    _assign_splits(rows)
    rows.sort(key=lambda row: row["scenario_id"])
    return rows


def provider_input_rows(rows: Iterable[dict], *, split: str) -> List[dict]:
    output = []
    for row in rows:
        if row["split"] != split:
            continue
        output.append({
            "scenario_id": row["scenario_id"],
            "world": row["world"],
            "principal": row["principal"],
            "surface": row["surface"],
            "surface_style": row["surface_style"],
        })
    return output


def _request_only_rule_prediction(row: dict) -> str | None:
    text = row["surface"].lower()
    if row["principal"] == "guest":
        return "REJECT"
    if "v99" in text:
        return "REJECT"
    if "2027" in text:
        return "REJECT"
    if "starting in" in text:
        return "CLARIFY"
    return None


def _tokenize(row: dict) -> List[str]:
    tokens = re.findall(r"[a-z0-9_]+", row["surface"].lower())
    tokens.append(f"role_{row['principal'].lower()}")
    return tokens


def _naive_bayes_request_only_accuracy(base_rows: List[dict]) -> float:
    """Leave-one-world-out multinomial NB leakage diagnostic, no extra dependency."""
    labels = ("ALLOW", "REJECT", "CLARIFY")
    correct = total = 0
    worlds = sorted({row["world"] for row in base_rows})
    for held_world in worlds:
        train = [row for row in base_rows if row["world"] != held_world]
        test = [row for row in base_rows if row["world"] == held_world]
        label_docs = Counter(row["gold_decision"] for row in train)
        token_counts: Dict[str, Counter] = {label: Counter() for label in labels}
        totals = Counter()
        vocabulary = set()
        for row in train:
            label = row["gold_decision"]
            for token in _tokenize(row):
                token_counts[label][token] += 1
                totals[label] += 1
                vocabulary.add(token)
        v = max(1, len(vocabulary))
        for row in test:
            scores = {}
            tokens = _tokenize(row)
            for label in labels:
                prior = (label_docs[label] + 1) / (len(train) + len(labels))
                score = math.log(prior)
                denom = totals[label] + v
                for token in tokens:
                    score += math.log((token_counts[label][token] + 1) / denom)
                scores[label] = score
            prediction = max(labels, key=lambda label: (scores[label], label))
            correct += int(prediction == row["gold_decision"])
            total += 1
    return correct / total if total else 0.0


def request_only_leakage_report(rows: List[dict]) -> dict:
    base = [row for row in rows if not row["counterfactual_group"]]
    rule_hits = [row for row in base if _request_only_rule_prediction(row) == row["gold_decision"]]
    return {
        "base_rows": len(base),
        "four_rule_accurate_coverage": len(rule_hits) / len(base),
        "leave_one_world_out_nb_accuracy": _naive_bayes_request_only_accuracy(base),
    }


def preflight_manifest(rows: List[dict]) -> dict:
    if len(rows) != FINAL_SCENARIOS:
        raise ValueError(f"expected {FINAL_SCENARIOS} scenarios, found {len(rows)}")
    if len({row["scenario_id"] for row in rows}) != len(rows):
        raise ValueError("scenario IDs are not unique")

    validate_no_conflicting_surfaces(rows)
    for row in rows:
        validate_no_label_leakage(row["surface"])
        if row["world_payload"]["name"] != row["world"]:
            raise ValueError("world payload/name mismatch")
        if row["gold_decision"] == "ALLOW" and row["expected_system_action"] != "EXECUTE":
            raise ValueError("platform capability must not change the primary authority action")

    counts_by_world = Counter(row["world"] for row in rows)
    if set(counts_by_world.values()) != {SCENARIOS_PER_WORLD}:
        raise ValueError(f"world imbalance: {counts_by_world}")

    cf_rows = [row for row in rows if row["counterfactual_group"]]
    if len(cf_rows) != 4 * COUNTERFACTUAL_ROWS_PER_WORLD:
        raise ValueError(f"counterfactual row count mismatch: {len(cf_rows)}")
    groups: Dict[str, List[dict]] = defaultdict(list)
    for row in cf_rows:
        groups[row["counterfactual_group"]].append(row)
    if len(groups) != 4 * COUNTERFACTUAL_PAIRS_PER_WORLD or any(len(group) != 2 for group in groups.values()):
        raise ValueError("counterfactual groups are not exactly 120 pairs")
    for group_id, pair in groups.items():
        if pair[0]["request_hash"] != pair[1]["request_hash"]:
            raise ValueError(f"counterfactual request changed: {group_id}")
        if pair[0]["surface"] != pair[1]["surface"]:
            raise ValueError(f"counterfactual visible request changed: {group_id}")
        if pair[0]["world_hash"] == pair[1]["world_hash"]:
            raise ValueError(f"counterfactual world did not change: {group_id}")
        if pair[0]["gold_signature"] == pair[1]["gold_signature"]:
            raise ValueError(f"counterfactual did not change governed target: {group_id}")
        if pair[0]["split"] != pair[1]["split"]:
            raise ValueError(f"counterfactual pair split across partitions: {group_id}")

    for world_name in counts_by_world:
        world_rows = [row for row in rows if row["world"] == world_name]
        base = [row for row in world_rows if not row["counterfactual_group"]]
        base_counts = Counter(row["gold_decision"] for row in base)
        if base_counts != Counter({"ALLOW": 30, "REJECT": 30, "CLARIFY": 30}):
            raise ValueError(f"base decision imbalance for {world_name}: {base_counts}")
        for decision in ("ALLOW", "REJECT", "CLARIFY"):
            mechanism_counts = Counter(
                row["taxonomy_family"] for row in base if row["gold_decision"] == decision
            )
            if len(mechanism_counts) < 6 or max(mechanism_counts.values()) > MAX_BASE_PER_MECHANISM:
                raise ValueError(f"base mechanism concentration for {world_name}/{decision}: {mechanism_counts}")

        authority_groups = [pair for pair in groups.values() if pair[0]["world"] == world_name and "-AUTHORITY-" in pair[0]["counterfactual_group"]]
        authority_mutations = Counter(pair[0]["counterfactual_mutation"] for pair in authority_groups)
        if authority_mutations and max(authority_mutations.values()) > MAX_CF_PAIRS_PER_MUTATION:
            raise ValueError(f"authority counterfactual concentration for {world_name}: {authority_mutations}")

        holdout = [row for row in world_rows if row["split"] == "sealed_holdout"]
        if len(holdout) != HOLDOUT_ROWS_PER_WORLD:
            raise ValueError(f"holdout count mismatch for {world_name}: {len(holdout)}")
        holdout_cf = [row for row in holdout if row["counterfactual_group"]]
        if len(holdout_cf) != 2 * HOLDOUT_CF_PAIRS_PER_WORLD:
            raise ValueError(f"holdout counterfactual mismatch for {world_name}")
        holdout_base = [row for row in holdout if not row["counterfactual_group"]]
        hb = Counter(row["gold_decision"] for row in holdout_base)
        if hb != Counter({"ALLOW": 6, "REJECT": 6, "CLARIFY": 6}):
            raise ValueError(f"holdout base decision imbalance for {world_name}: {hb}")

    leakage = request_only_leakage_report(rows)
    if leakage["four_rule_accurate_coverage"] > MAX_REQUEST_ONLY_RULE_ACCURATE_COVERAGE:
        raise ValueError(f"request-only rule leakage too high: {leakage}")
    if leakage["leave_one_world_out_nb_accuracy"] > MAX_REQUEST_ONLY_NB_ACCURACY:
        raise ValueError(f"request-only classifier leakage too high: {leakage}")

    commitment_payload = [
        {
            "scenario_id": row["scenario_id"],
            "world_hash": row["world_hash"],
            "request_hash": row["request_hash"],
            "gold_signature": row["gold_signature"],
            "split": row["split"],
        }
        for row in rows
    ]
    commitment = hashlib.sha256(_canonical_json(commitment_payload).encode()).hexdigest()
    return {
        "scenario_count": len(rows),
        "main_count": sum(row["split"] == "main" for row in rows),
        "sealed_holdout_count": sum(row["split"] == "sealed_holdout" for row in rows),
        "counterfactual_rows": len(cf_rows),
        "counterfactual_fraction": len(cf_rows) / len(rows),
        "world_counts": dict(sorted(counts_by_world.items())),
        "decision_counts": dict(sorted(Counter(row["gold_decision"] for row in rows).items())),
        "base_mechanism_counts": dict(sorted(Counter(row["taxonomy_family"] for row in rows if not row["counterfactual_group"]).items())),
        "counterfactual_mutation_counts": dict(sorted(Counter(row["counterfactual_mutation"] for row in cf_rows).items())),
        "request_only_leakage": leakage,
        "manifest_commitment_sha256": commitment,
    }
