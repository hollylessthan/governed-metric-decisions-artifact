from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class MetricVersion:
    version: str
    valid_from: int
    valid_to: Optional[int]
    certified: bool
    additive_over_time: bool
    currency: Optional[str] = None


@dataclass(frozen=True)
class MetricSpec:
    name: str
    aliases: Tuple[str, ...]
    dimensions: Tuple[str, ...]
    entities: Tuple[str, ...]
    versions: Tuple[MetricVersion, ...]
    aggregation: str
    row_scope: Optional[str] = None


@dataclass(frozen=True)
class Relationship:
    left_entity: str
    right_entity: str
    cardinality: str
    fanout_safe: bool


@dataclass(frozen=True)
class Policy:
    role: str
    denied_metrics: Tuple[str, ...] = ()
    denied_dimensions: Tuple[str, ...] = ()
    required_row_scope: Optional[str] = None
    scoped_metrics: Tuple[str, ...] = ()


@dataclass(frozen=True)
class World:
    name: str
    metrics: Dict[str, MetricSpec]
    aliases: Dict[str, Tuple[str, ...]]
    relationships: Tuple[Relationship, ...]
    policies: Tuple[Policy, ...]
    compiler_capabilities: Tuple[str, ...]
    clock_year: int
    fiscal_year_start_month: int = 1
    fx_context_available: bool = False
    authorized_roles: Tuple[str, ...] = ("analyst",)

    def to_dict(self) -> dict:
        return asdict(self)


def _mv(version: str, start: int, end: Optional[int], *, certified: bool = True,
        additive_over_time: bool = True, currency: Optional[str] = None) -> MetricVersion:
    return MetricVersion(version, start, end, certified, additive_over_time, currency)


def build_worlds() -> Dict[str, World]:
    saas_metrics = {
        "mrr": MetricSpec("mrr", ("monthly recurring revenue",), ("segment", "region"),
                          ("account",), (_mv("v1", 2023, None, additive_over_time=False, currency="USD"),),
                          "snapshot_sum"),
        "nrr": MetricSpec("nrr", ("net revenue retention", "retention"), ("segment", "region"),
                          ("account",), (_mv("v1", 2023, 2024), _mv("v2", 2025, None)), "ratio"),
    }
    commerce_metrics = {
        "gmv": MetricSpec("gmv", ("gross merchandise value",), ("market", "channel", "promotion"),
                           ("order", "seller"), (_mv("v1", 2023, None, currency="USD"),), "sum"),
        "orders": MetricSpec("orders", ("order count",), ("market", "channel"),
                              ("order",), (_mv("v1", 2023, None),), "count"),
    }
    support_metrics = {
        "resolution_rate": MetricSpec("resolution_rate", ("case resolution rate",), ("queue", "priority"),
                                      ("ticket",), (_mv("v1", 2023, None),), "ratio"),
        "backlog": MetricSpec("backlog", ("open backlog",), ("queue", "priority"),
                              ("ticket",), (_mv("v1", 2023, None, additive_over_time=False),), "snapshot_sum"),
    }
    finance_metrics = {
        "revenue": MetricSpec("revenue", ("recognized revenue",), ("region", "business_unit"),
                              ("invoice",), (_mv("v1", 2023, None, currency="USD"),), "sum"),
        # Row-scope authority is governed by Policy, not by duplicate metric metadata.
        # Margin is a ratio and therefore not additive over time.
        "margin": MetricSpec("margin", ("gross margin",), ("region", "business_unit"),
                             ("invoice",), (_mv("v1", 2023, None, additive_over_time=False),), "ratio"),
    }

    return {
        "saas": World("saas", saas_metrics, {"retention": ("nrr",)},
                      (Relationship("account", "segment", "many_to_one", True),),
                      (Policy("contractor", denied_metrics=("mrr",)),),
                      ("single_metric", "group_by", "ratio", "snapshot"), 2026,
                      authorized_roles=("analyst", "finance", "contractor")),
        "commerce": World("commerce", commerce_metrics, {},
                          (Relationship("order", "seller", "many_to_one", True),
                           Relationship("order", "promotion", "many_to_many", False)),
                          (Policy("external", denied_dimensions=("seller",)),),
                          ("single_metric", "group_by", "currency_conversion"), 2026, fx_context_available=False,
                          authorized_roles=("analyst", "external")),
        "support": World("support", support_metrics, {},
                         (Relationship("ticket", "queue", "many_to_one", True),),
                         (Policy("vendor", denied_metrics=("backlog",)),),
                         ("single_metric", "group_by", "snapshot", "ratio"), 2026,
                         authorized_roles=("analyst", "vendor")),
        "finance": World("finance", finance_metrics, {},
                         (Relationship("invoice", "business_unit", "many_to_one", True),),
                         (Policy("analyst", required_row_scope="finance_approved", scoped_metrics=("margin",)),),
                         ("single_metric", "group_by", "fiscal_period", "ratio", "currency_conversion"), 2026,
                         fiscal_year_start_month=2, fx_context_available=True,
                         authorized_roles=("analyst", "finance")),
    }
