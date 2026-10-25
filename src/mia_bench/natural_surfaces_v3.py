from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Tuple

from .expanded_worlds_v3 import ExpandedWorldV3
from .oracle_v3 import CanonicalRequestV3


@dataclass(frozen=True)
class SurfaceRealization:
    style: str
    text: str
    semantic_markers: Tuple[str, ...]


_STYLE_ORDER = ("direct", "analyst", "compact")


def _request_seed(request: CanonicalRequestV3, salt: str) -> int:
    payload = "|".join([request.metric_ref, ",".join(request.dimensions), salt])
    return int(hashlib.sha256(payload.encode()).hexdigest()[:16], 16)


def _pick(request: CanonicalRequestV3, salt: str, options: Tuple[str, ...]) -> str:
    return options[_request_seed(request, salt) % len(options)]


def _metric_phrase(world: ExpandedWorldV3, request: CanonicalRequestV3) -> str:
    if request.metric_ref in world.metrics:
        metric = world.metrics[request.metric_ref]
        return metric.aliases[0] if metric.aliases else metric.name.replace("_", " ")
    return request.metric_ref.replace("_", " ")


def _dimension_phrase(dimension: str) -> str:
    return dimension.replace("_", " ")


def _time_phrase(request: CanonicalRequestV3) -> str:
    start, end = request.start_year, request.end_year
    if request.temporal_operation == "point":
        if start is not None and end is not None and start == end:
            return _pick(request, "point-complete", (f"as of year-end {start}", f"at the end of {start}", f"at year-end {start}"))
        if start is None and end is not None:
            return _pick(request, "point-missing-start", (f"with point timing through {end}, start date unspecified", f"as a point-in-time request ending in {end}, with no start date", f"for a point ending in {end}, without a specified start"))
        if start is not None and end is None:
            return _pick(request, "point-missing-end", (f"with point timing starting in {start}, end date unspecified", f"as a point-in-time request starting in {start}, with no end date", f"for a point starting in {start}, without a specified end"))
    if start is not None and end is not None:
        if start == end:
            return _pick(request, "year-single", (f"in {start}", f"for {start}", f"during {start}"))
        return _pick(request, "year-range", (f"from {start} through {end}", f"across {start} to {end}", f"for the {start}-{end} period"))
    if start is not None:
        return _pick(request, "start-only", (f"starting in {start}", f"from {start} onward", f"beginning in {start}, with no end specified"))
    if end is not None:
        return _pick(request, "end-only", (f"through {end}", f"up to {end}, with no start specified", f"ending in {end}, start unspecified"))
    return ""


def _operation_prefix(request: CanonicalRequestV3) -> str:
    if request.temporal_operation == "sum":
        # The blind audit showed that "total <snapshot metric>" is ambiguous:
        # it can mean a point total rather than a sum over time. Preserve the
        # canonical operation explicitly in every realization.
        return _pick(request, "op-sum", ("summed ", "time-summed ", "period-summed "))
    if request.temporal_operation == "average":
        return _pick(request, "op-average", ("average ", "mean ", "averaged "))
    return ""


def _qualifiers(request: CanonicalRequestV3) -> list[str]:
    q: list[str] = []
    if request.version_hint:
        q.append(_pick(request, "version", (f"using definition {request.version_hint}", f"under metric definition {request.version_hint}", f"with version {request.version_hint}")))
    if request.calendar_kind == "fiscal":
        q.append(_pick(request, "fiscal", ("on the fiscal calendar", "using fiscal-year timing", "on a fiscal-year basis")))
    if request.target_currency:
        q.append(_pick(request, "currency", (f"reported in {request.target_currency}", f"expressed in {request.target_currency}", f"converted to {request.target_currency}")))
    if request.row_scope:
        scope = request.row_scope.replace("_", " ")
        q.append(_pick(request, "row-scope", (f"with {scope} row scope", f"restricted to {scope} rows", f"under the {scope} row filter")))
    if request.certification_requirement == "certified":
        q.append(_pick(request, "certification", ("using only certified definitions", "with a certified metric definition", "restricted to certified definitions")))
    if request.entity_path:
        path = "-to-".join(entity.replace("_", " ") for entity in request.entity_path)
        q.append(_pick(request, "entity-path", (f"using the {path} relationship path", f"through the {path} relationship path", f"via the {path} relationship path")))
    return q


def semantic_markers(request: CanonicalRequestV3) -> Tuple[str, ...]:
    markers = [f"metric:{request.metric_ref}", f"role:{request.role}"]
    markers.extend(f"dimension:{d}" for d in request.dimensions)
    if request.start_year is not None:
        markers.append(f"start_year:{request.start_year}")
    if request.end_year is not None:
        markers.append(f"end_year:{request.end_year}")
    if request.version_hint:
        markers.append(f"version:{request.version_hint}")
    if request.temporal_operation:
        markers.append(f"temporal_operation:{request.temporal_operation}")
    if request.calendar_kind != "calendar":
        markers.append(f"calendar:{request.calendar_kind}")
    if request.target_currency:
        markers.append(f"currency:{request.target_currency}")
    if request.row_scope:
        markers.append(f"row_scope:{request.row_scope}")
    if request.certification_requirement:
        markers.append(f"certification:{request.certification_requirement}")
    if request.entity_path:
        markers.append("entity_path:" + "->".join(request.entity_path))
    return tuple(markers)


def realize(world: ExpandedWorldV3, request: CanonicalRequestV3, *, style: str) -> SurfaceRealization:
    if style not in _STYLE_ORDER:
        raise ValueError(f"unknown realization style: {style}")

    metric = _metric_phrase(world, request)
    operation = _operation_prefix(request)
    dims = [_dimension_phrase(d) for d in request.dimensions]
    time = _time_phrase(request)
    qualifiers = _qualifiers(request)
    discourse = _pick(request, "discourse", ("", "For analysis, ", "For the report, ", "Quick check: ", "For review, ", "For this cut, "))

    if style == "direct":
        lead = _pick(request, "direct-lead", ("Show", "Report", "Give me", "Pull", "Provide"))
        text = f"{discourse}{lead} {operation}{metric}"
        if dims:
            text += " by " + " and ".join(dims)
        if time:
            text += " " + time
        if qualifiers:
            text += ", " + ", ".join(qualifiers)
        text += "."
    elif style == "analyst":
        lead = _pick(request, "analyst-lead", ("Can you give me", "Could you pull", "I need", "Can you report", "Please provide"))
        text = f"{discourse}{lead} {operation}{metric}"
        if dims:
            breakdown = _pick(request, "breakdown", (" broken down by ", " grouped by ", " split by ", " segmented by ", " organized by "))
            text += breakdown + " and ".join(dims)
        if time:
            text += " " + time
        if qualifiers:
            text += ", " + ", ".join(qualifiers)
        text += "?" if lead.startswith(("Can", "Could")) else "."
    else:
        parts = [f"{operation}{metric}".strip()]
        if dims:
            parts.append("by " + " / ".join(dims))
        if time:
            parts.append(time)
        parts.extend(qualifiers)
        text = discourse + "; ".join(parts) + "."

    return SurfaceRealization(style, text[0].upper() + text[1:], semantic_markers(request))


def realize_all(world: ExpandedWorldV3, request: CanonicalRequestV3) -> Tuple[SurfaceRealization, ...]:
    return tuple(realize(world, request, style=style) for style in _STYLE_ORDER)


def stable_style_order(scenario_id: str) -> Tuple[str, ...]:
    scored = []
    for style in _STYLE_ORDER:
        digest = hashlib.sha256(f"mia-bench-v3|{scenario_id}|{style}".encode()).hexdigest()
        scored.append((digest, style))
    return tuple(style for _, style in sorted(scored))


def validate_no_conflicting_surfaces(rows: Iterable[dict]) -> None:
    seen: dict[tuple[str, str, str], object] = {}
    for row in rows:
        key = (row["world_hash"], row["principal"], row["surface"])
        signature = row["gold_signature"]
        if key in seen and seen[key] != signature:
            raise ValueError(f"conflicting gold for identical visible input: {key}")
        seen[key] = signature


def validate_no_label_leakage(text: str) -> None:
    lowered = text.lower()
    forbidden = (
        "gold_decision", "authority_valid", "platform_executable", "coverage_gap",
        "principal_not_authorized", "fanout_unsafe", "version_ambiguous",
        "row_scope_missing", "snapshot_point_missing",
    )
    leaked = [token for token in forbidden if token in lowered]
    if leaked:
        raise ValueError(f"surface contains benchmark-only leakage token(s): {leaked}")
