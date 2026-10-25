# Governed Metric Decisions — AGENT 2027 Artifact (Draft)

This is an **in-progress, unverified** evidence package for the empirical study of execute, clarify, and reject decisions on governed metric requests. It is not yet a complete reproducibility package.

## Included initial evidence
- `paper/agent-2027-routing-evidence.md` and `.json`: generated tables and source metadata.
- `reports/mia-bench-b4-b5-audit/`: frozen B4/B5 disagreement audit and cases.
- `reports/mia-bench-holdout-synthesis/summary.json`: model-level holdout evidence.
- `scripts/agent_2027_routing_evidence.py`: original evidence calculation.
- `docs/mia-bench-b4-b5-audit-2026-10-24.md`: audit interpretation.

Files are copied without rewriting from `hollylessthan/metric-intent-assurance` main as inspected on 2026-10-25.

## Study scope
B4 direct and B5 candidate-assisted routing are central. B1–B3 are interpretation-stage context, not same-task authorization baselines. MIA is retained as historical/contextual evidence, not presented as a newly proposed architecture.

The paper's action evaluation is not a test of numerical answer accuracy, full intent recovery or production safety. Results use frozen outputs and include descriptive analyses performed after the original study; they are not newly confirmatory experiments.

## Reproduction TODO
The original source data, runner dependencies, model metadata, precise source commit manifests, public-distribution audit, and clean offline reproduction checks still need to be added. **Do not treat this first import as a successful reproduction.** No new API calls should be made to replace frozen evidence.

After verification, freeze a public release and optionally archive the release on Zenodo.
