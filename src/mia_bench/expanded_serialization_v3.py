from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from .expanded_worlds_v3 import (
    EntitySpecV3,
    ExpandedWorldV3,
    MetricSpecV3,
    MetricVersionV3,
    PolicyV3,
    RelationshipV3,
)


EXPANDED_WORLD_SCHEMA_VERSION = "mia-bench-expanded-world-v3.2"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def world_to_dict(world: ExpandedWorldV3) -> dict:
    return {
        "schema_version": EXPANDED_WORLD_SCHEMA_VERSION,
        "name": world.name,
        "metrics": {
            name: {
                "name": metric.name,
                "aliases": list(metric.aliases),
                "base_entity": metric.base_entity,
                "direct_dimensions": list(metric.direct_dimensions),
                "versions": [asdict(version) for version in metric.versions],
                "aggregation": metric.aggregation,
            }
            for name, metric in sorted(world.metrics.items())
        },
        "entities": {
            name: {"name": entity.name, "dimensions": list(entity.dimensions)}
            for name, entity in sorted(world.entities.items())
        },
        "aliases": {name: list(targets) for name, targets in sorted(world.aliases.items())},
        "relationships": [asdict(rel) for rel in world.relationships],
        "policies": [asdict(policy) for policy in world.policies],
        "compiler_capabilities": list(world.compiler_capabilities),
        "clock_year": world.clock_year,
        "fiscal_year_start_month": world.fiscal_year_start_month,
        "fx_context_available": world.fx_context_available,
        "authorized_roles": list(world.authorized_roles),
        "unsupported_by_mia": list(world.unsupported_by_mia),
    }


def world_from_dict(value: dict) -> ExpandedWorldV3:
    if value.get("schema_version") != EXPANDED_WORLD_SCHEMA_VERSION:
        raise ValueError("unsupported expanded-world schema version")
    metrics = {
        name: MetricSpecV3(
            metric["name"],
            tuple(metric.get("aliases", ())),
            metric["base_entity"],
            tuple(metric.get("direct_dimensions", ())),
            tuple(MetricVersionV3(**version) for version in metric["versions"]),
            metric["aggregation"],
        )
        for name, metric in value["metrics"].items()
    }
    entities = {
        name: EntitySpecV3(entity["name"], tuple(entity.get("dimensions", ())))
        for name, entity in value["entities"].items()
    }
    relationships = tuple(RelationshipV3(**rel) for rel in value.get("relationships", ()))
    policies = tuple(
        PolicyV3(
            policy["role"],
            tuple(policy.get("denied_metrics", ())),
            tuple(policy.get("denied_dimensions", ())),
            policy.get("required_row_scope"),
            tuple(policy.get("scoped_metrics", ())),
        )
        for policy in value.get("policies", ())
    )
    return ExpandedWorldV3(
        value["name"],
        metrics,
        entities,
        {name: tuple(targets) for name, targets in value.get("aliases", {}).items()},
        relationships,
        policies,
        tuple(value.get("compiler_capabilities", ())),
        value["clock_year"],
        value.get("fiscal_year_start_month", 1),
        bool(value.get("fx_context_available", False)),
        tuple(value.get("authorized_roles", ("analyst",))),
        tuple(value.get("unsupported_by_mia", ())),
    )


def serialize_world(world: ExpandedWorldV3) -> str:
    return _canonical_json(world_to_dict(world))


def deserialize_world(payload: str) -> ExpandedWorldV3:
    return world_from_dict(json.loads(payload))


def world_sha256(world: ExpandedWorldV3) -> str:
    return hashlib.sha256(serialize_world(world).encode("utf-8")).hexdigest()


def worlds_manifest(worlds: dict[str, ExpandedWorldV3]) -> dict:
    return {
        "schema_version": EXPANDED_WORLD_SCHEMA_VERSION,
        "world_hashes": {name: world_sha256(world) for name, world in sorted(worlds.items())},
    }
