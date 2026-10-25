# Retrospective B4/B5 disagreement audit

See the [assessment and scope](../../docs/mia-bench-b4-b5-audit-2026-10-24.md).

- [summary.json](summary.json): separate main/holdout, full/authority counts, frozen endpoint reconciliation and input hashes.
- [cases.jsonl](cases.jsonl): all 101 disagreement records (80 main action-only; 21 raw-replayed holdout).
- The 21 holdout disagreement records are available in [cases.jsonl](cases.jsonl); a separate narrative review is not bundled.

For the curated artifact, run `python scripts/agent_2027_routing_evidence.py --check` to verify the exported results without provider calls. The original full-study audit utility is not part of this curated release. Frozen labels, results and gates are unchanged. These are descriptive observations, not a causal or novelty claim.
