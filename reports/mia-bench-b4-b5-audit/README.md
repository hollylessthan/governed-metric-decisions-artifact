# Retrospective B4/B5 disagreement audit

See the [assessment and scope](../../docs/mia-bench-b4-b5-audit-2026-10-24.md).

- [summary.json](summary.json): separate main/holdout, full/authority counts, frozen endpoint reconciliation and input hashes.
- [cases.jsonl](cases.jsonl): all 101 disagreement records (80 main action-only; 21 raw-replayed holdout).
- [holdout-review.md](holdout-review.md): complete human-readable review of the 21 holdout records.

Run `python scripts/mia_bench_b4_b5_audit.py --output /tmp/b4-b5-audit` from a complete checkout, using a new output directory. No provider calls occur. Frozen labels, results and gates are unchanged. These are descriptive observations, not a causal or novelty claim.
