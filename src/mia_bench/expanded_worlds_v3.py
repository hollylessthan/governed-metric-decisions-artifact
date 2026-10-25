from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class MetricVersionV3:
    version: str
    valid_from: int
    valid_to: Optional[int]
    certified: bool = True
    additive_over_time: bool = True
    currency: Optional[str] = None


@dataclass(frozen=True)
class EntitySpecV3:
    name: str
    dimensions: Tuple[str, ...]


@dataclass(frozen=True)
class MetricSpecV3:
    name: str
    aliases: Tuple[str, ...]
    base_entity: str
    direct_dimensions: Tuple[str, ...]
    versions: Tuple[MetricVersionV3, ...]
    aggregation: str

    def __post_init__(self) -> None:
        # Ratio/average values are derived measures and are never additive over
        # time as raw values. Derive this invariant from aggregation so new
        # worlds cannot accidentally inherit MetricVersionV3's additive default.
        if self.aggregation in {"ratio", "average"}:
            normalized = tuple(
                MetricVersionV3(
                    version=v.version,
                    valid_from=v.valid_from,
                    valid_to=v.valid_to,
                    certified=v.certified,
                    additive_over_time=False,
                    currency=v.currency,
                )
                for v in self.versions
            )
            object.__setattr__(self, "versions", normalized)


@dataclass(frozen=True)
class RelationshipV3:
    left_entity: str
    right_entity: str
    cardinality: str
    fanout_safe: bool


@dataclass(frozen=True)
class PolicyV3:
    role: str
    denied_metrics: Tuple[str, ...] = ()
    denied_dimensions: Tuple[str, ...] = ()
    required_row_scope: Optional[str] = None
    scoped_metrics: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ExpandedWorldV3:
    name: str
    metrics: Dict[str, MetricSpecV3]
    entities: Dict[str, EntitySpecV3]
    aliases: Dict[str, Tuple[str, ...]]
    relationships: Tuple[RelationshipV3, ...]
    policies: Tuple[PolicyV3, ...]
    compiler_capabilities: Tuple[str, ...]
    clock_year: int
    fiscal_year_start_month: int = 1
    fx_context_available: bool = False
    authorized_roles: Tuple[str, ...] = ("analyst",)
    unsupported_by_mia: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


def _mv(version: str, start: int, end: Optional[int] = None, *, certified: bool = True,
        additive: bool = True, currency: Optional[str] = None) -> MetricVersionV3:
    return MetricVersionV3(version, start, end, certified, additive, currency)


def build_expanded_worlds() -> Dict[str, ExpandedWorldV3]:
    saas_entities = {
        "account": EntitySpecV3("account", ("account", "segment", "region", "industry")),
        "subscription": EntitySpecV3("subscription", ("subscription", "plan", "billing_term")),
        "plan": EntitySpecV3("plan", ("plan", "plan_family")),
    }
    saas_metrics = {
        "mrr": MetricSpecV3("mrr", ("monthly recurring revenue",), "subscription", ("plan", "billing_term"),
                            (_mv("v1", 2023, 2024, additive=False, currency="USD"), _mv("v2", 2025, additive=False, currency="USD")), "snapshot_sum"),
        "arr": MetricSpecV3("arr", ("annual recurring revenue",), "subscription", ("plan",),
                            (_mv("v1", 2023, 2024, additive=False, currency="USD"), _mv("v2", 2025, additive=False, currency="USD")), "snapshot_sum"),
        "nrr": MetricSpecV3("nrr", ("net revenue retention", "retention"), "account", ("segment", "region"),
                            (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "grr": MetricSpecV3("grr", ("gross revenue retention",), "account", ("segment", "region"),
                            (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "churn_rate": MetricSpecV3("churn_rate", ("logo churn rate",), "account", ("segment", "region"),
                                   (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "active_subscriptions": MetricSpecV3("active_subscriptions", ("active subs",), "subscription", ("plan", "billing_term"),
                                             (_mv("v1", 2023, additive=False),), "snapshot_count"),
        "expansion_revenue": MetricSpecV3("expansion_revenue", ("expansion",), "account", ("segment", "region"),
                                           (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
    }
    saas = ExpandedWorldV3(
        "saas", saas_metrics, saas_entities,
        {"retention": ("nrr", "grr"), "recurring value": ("mrr", "arr")},
        (
            RelationshipV3("subscription", "account", "many_to_one", True),
            RelationshipV3("subscription", "plan", "many_to_one", True),
        ),
        (PolicyV3("contractor", denied_metrics=("mrr", "arr")),),
        ("single_metric", "group_by", "ratio", "snapshot", "currency_conversion"), 2026,
        fx_context_available=True, authorized_roles=("analyst", "finance", "contractor"),
        unsupported_by_mia=("relationship_reachable_dimension_ownership",),
    )

    commerce_entities = {
        "order": EntitySpecV3("order", ("order", "market", "channel")),
        "order_line": EntitySpecV3("order_line", ("order_line", "product")),
        "seller": EntitySpecV3("seller", ("seller", "seller_tier")),
        "product": EntitySpecV3("product", ("product", "category", "brand")),
        "promotion": EntitySpecV3("promotion", ("promotion", "campaign")),
        "promotion_attribution": EntitySpecV3("promotion_attribution", ("promotion", "campaign")),
    }
    commerce_metrics = {
        "gmv": MetricSpecV3("gmv", ("gross merchandise value",), "order", ("market", "channel"),
                            (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
        "net_sales": MetricSpecV3("net_sales", ("net sales",), "order", ("market", "channel"),
                                  (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
        "orders": MetricSpecV3("orders", ("order count",), "order", ("market", "channel"),
                               (_mv("v1", 2023, 2024), _mv("v2", 2025)), "count"),
        "units_sold": MetricSpecV3("units_sold", ("units",), "order_line", ("product",),
                                   (_mv("v1", 2023),), "sum"),
        "aov": MetricSpecV3("aov", ("average order value",), "order", ("market", "channel"),
                            (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "ratio"),
        "refund_rate": MetricSpecV3("refund_rate", ("refund percentage",), "order", ("market", "channel"),
                                    (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "promotion_attributed_sales": MetricSpecV3("promotion_attributed_sales", ("attributed sales",), "promotion_attribution", ("promotion", "campaign"),
                                                    (_mv("v1", 2023, currency="USD"),), "sum"),
        "active_sellers": MetricSpecV3("active_sellers", ("seller count",), "seller", ("seller_tier",),
                                       (_mv("v1", 2023, additive=False),), "snapshot_count"),
    }
    commerce = ExpandedWorldV3(
        "commerce", commerce_metrics, commerce_entities,
        {"sales value": ("gmv", "net_sales"), "order volume": ("orders", "units_sold")},
        (
            RelationshipV3("order_line", "order", "many_to_one", True),
            RelationshipV3("order_line", "product", "many_to_one", True),
            RelationshipV3("order", "seller", "many_to_one", True),
            RelationshipV3("order", "promotion", "many_to_many", False),
            RelationshipV3("promotion_attribution", "promotion", "many_to_one", True),
            RelationshipV3("promotion_attribution", "order", "many_to_one", True),
        ),
        (PolicyV3("external", denied_dimensions=("seller", "seller_tier")),),
        ("single_metric", "group_by", "ratio", "snapshot", "currency_conversion"), 2026,
        fx_context_available=False, authorized_roles=("analyst", "external"),
        unsupported_by_mia=("bridge_attribution_semantics",),
    )

    support_entities = {
        "ticket": EntitySpecV3("ticket", ("ticket", "priority", "channel")),
        "queue": EntitySpecV3("queue", ("queue", "queue_group")),
        "agent": EntitySpecV3("agent", ("agent", "team")),
        "customer": EntitySpecV3("customer", ("customer", "customer_tier", "region")),
    }
    support_metrics = {
        "backlog": MetricSpecV3("backlog", ("open backlog",), "ticket", ("priority", "channel"),
                                (_mv("v1", 2023, additive=False),), "snapshot_sum"),
        "active_escalations": MetricSpecV3("active_escalations", ("open escalations",), "ticket", ("priority", "channel"),
                                           (_mv("v1", 2023, additive=False),), "snapshot_count"),
        "opened_cases": MetricSpecV3("opened_cases", ("new cases",), "ticket", ("priority", "channel"),
                                     (_mv("v1", 2023, 2024), _mv("v2", 2025)), "count"),
        "closed_cases": MetricSpecV3("closed_cases", ("resolved cases",), "ticket", ("priority", "channel"),
                                     (_mv("v1", 2023, 2024), _mv("v2", 2025)), "count"),
        "resolution_rate": MetricSpecV3("resolution_rate", ("case resolution rate",), "ticket", ("priority", "channel"),
                                        (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "first_response_time": MetricSpecV3("first_response_time", ("response time",), "ticket", ("priority", "channel"),
                                            (_mv("v1", 2023),), "average"),
        "sla_attainment": MetricSpecV3("sla_attainment", ("sla rate",), "ticket", ("priority", "channel"),
                                       (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "reopen_rate": MetricSpecV3("reopen_rate", ("reopen percentage",), "ticket", ("priority", "channel"),
                                    (_mv("v1", 2023, 2024), _mv("v2", 2025)), "ratio"),
        "csat": MetricSpecV3("csat", ("customer satisfaction",), "ticket", ("priority", "channel"),
                             (_mv("v1", 2023),), "average"),
    }
    support = ExpandedWorldV3(
        "support", support_metrics, support_entities,
        {"resolution": ("closed_cases", "resolution_rate"), "case flow": ("opened_cases", "closed_cases")},
        (
            RelationshipV3("ticket", "queue", "many_to_one", True),
            RelationshipV3("ticket", "agent", "many_to_one", True),
            RelationshipV3("ticket", "customer", "many_to_one", True),
        ),
        (PolicyV3("vendor", denied_metrics=("backlog",), denied_dimensions=("customer", "customer_tier")),),
        ("single_metric", "group_by", "ratio", "snapshot"), 2026,
        authorized_roles=("analyst", "vendor"),
        unsupported_by_mia=("reachable_dimension_policy_after_path_resolution",),
    )

    finance_entities = {
        "invoice": EntitySpecV3("invoice", ("invoice", "region")),
        "business_unit": EntitySpecV3("business_unit", ("business_unit", "division")),
        "legal_entity": EntitySpecV3("legal_entity", ("legal_entity", "country")),
        "account": EntitySpecV3("account", ("account", "account_class")),
        "cost_center": EntitySpecV3("cost_center", ("cost_center", "department")),
        "cash_account": EntitySpecV3("cash_account", ("cash_account", "bank_region")),
    }
    finance_metrics = {
        "revenue": MetricSpecV3("revenue", ("recognized revenue",), "invoice", ("region",),
                                (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
        "margin": MetricSpecV3("margin", ("gross margin",), "invoice", ("region",),
                               (_mv("v1", 2023, 2024, additive=False), _mv("v2", 2025, additive=False)), "ratio"),
        "opex": MetricSpecV3("opex", ("operating expense",), "cost_center", ("cost_center", "department"),
                             (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
        "bookings": MetricSpecV3("bookings", ("booked value",), "invoice", ("region",),
                                 (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
        "cash_balance": MetricSpecV3("cash_balance", ("cash",), "cash_account", ("cash_account", "bank_region"),
                                     (_mv("v1", 2023, additive=False, currency="USD"),), "snapshot_sum"),
        "dso": MetricSpecV3("dso", ("days sales outstanding",), "invoice", ("region",),
                            (_mv("v1", 2023, additive=False),), "ratio"),
        "forecast_variance": MetricSpecV3("forecast_variance", ("forecast delta",), "business_unit", ("business_unit", "division"),
                                          (_mv("v1", 2023),), "ratio"),
        "fx_adjusted_revenue": MetricSpecV3("fx_adjusted_revenue", ("constant currency revenue",), "invoice", ("region",),
                                            (_mv("v1", 2023, 2024, currency="USD"), _mv("v2", 2025, currency="USD")), "sum"),
    }
    finance = ExpandedWorldV3(
        "finance", finance_metrics, finance_entities,
        {"reported top line": ("revenue", "fx_adjusted_revenue"), "reported value": ("revenue", "bookings")},
        (
            RelationshipV3("invoice", "business_unit", "many_to_one", True),
            RelationshipV3("invoice", "legal_entity", "many_to_one", True),
            RelationshipV3("business_unit", "cost_center", "one_to_many", False),
        ),
        (PolicyV3("analyst", required_row_scope="finance_approved", scoped_metrics=("margin", "dso")),),
        ("single_metric", "group_by", "fiscal_period", "ratio", "snapshot", "currency_conversion"), 2026,
        fiscal_year_start_month=2, fx_context_available=True,
        authorized_roles=("analyst", "finance"),
        unsupported_by_mia=("entity_owned_reachable_dimensions",),
    )

    return {"saas": saas, "commerce": commerce, "support": support, "finance": finance}
