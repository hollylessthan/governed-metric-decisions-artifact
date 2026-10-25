# Governed Metric Decisions — Reproduction Artifact

[![Offline artifact reproduction](https://github.com/hollylessthan/governed-metric-decisions-artifact/actions/workflows/reproduce.yml/badge.svg)](https://github.com/hollylessthan/governed-metric-decisions-artifact/actions/workflows/reproduce.yml)

This repository packages the frozen experimental evidence and offline verification code for a study of **pre-execution decisions for governed metric requests**. It supports inspection and recalculation of reported results without new language-model API calls.

**Research question.** When an analytics agent receives a metric request alongside governed definitions and access rules, can it correctly decide to **execute**, **clarify**, or **reject** before execution? How does a direct decision route compare with a route that additionally reviews an upstream structured candidate?

This is a *decision-component* study on synthetic governed worlds, not an evaluation of numerical answers, a production authorization system, or a new assurance mechanism.

## Study at a glance

- **Decision task:** choose *execute* for an allowed and sufficiently specified request, *clarify* for missing or ambiguous information, or *reject* for a hard policy conflict.
- **B4 — direct route:** decides from the request, governed world, and principal context.
- **B5 — candidate-assisted route:** receives those facts plus a frozen upstream B2 candidate and additional fidelity-check instructions. Candidate visibility **and instructions** differ, so B4/B5 differences do not isolate a causal candidate effect.
- **Workload:** 600 synthetic scenarios in commerce, finance, SaaS, and support (480 main, 120 originally sealed holdout). Qwen used the full main set; OpenAI and Anthropic used the same 120-scenario main replication subset. All three evaluated the 120-scenario holdout.
- **Primary descriptive cohort in this package:** 101 holdout authority representatives *per model*: 37 ALLOW and 64 non-ALLOW. The other holdout scenarios include feasibility cases and a duplicate.
- **Governance-pair analysis:** 15 identical-request authority pairs change governed-world facts; 14 require a binary execute/stop flip. Nine separate feasibility pairs are outside that analysis.

The original source study also includes B1–B3 interpretation stages and Metric Intent Assurance (MIA). These are preserved as historical context; B1–B3 are **not** same-task authorization controls, and this artifact does not claim MIA as a new method.

## Key holdout results

These values are descriptive results on the same 101 authority representatives for each model. “Unsafe executes” means execution on a request whose required action is **clarify or reject**; not all 64 non-ALLOW cases are prohibited requests.

| Model | Route | ALLOW executed | Unsafe executes | Exact three-way decisions | Technical failures |
|---|---|---:|---:|---:|---:|
| Qwen | B4 direct | 34/37 | 7/64 | 82/101 | 0/101 |
| Qwen | B5 candidate-assisted | 30/37 | 9/64 | 75/101 | 0/101 |
| OpenAI | B4 direct | 37/37 | 3/64 | 98/101 | 0/101 |
| OpenAI | B5 candidate-assisted | 37/37 | 4/64 | 96/101 | 0/101 |
| Anthropic | B4 direct | 37/37 | 2/64 | 95/101 | 0/101 |
| Anthropic | B5 candidate-assisted | 36/37 | 6/64 | 87/101 | 5/101 |

The direct route achieved useful ALLOW coverage in these controlled scenarios, but still executed some requests that required clarification or rejection. Candidate assistance showed **no consistent observed improvement** in these runs; five recorded B5 dependency failures are included in its outcomes. This does not prove general superiority of B4 or attribute differences causally to candidate content.

The full count reconciliation, different refusal types, 21 holdout disagreements, main-set supplement, and governance-pair outcomes are in [generated routing evidence](paper/agent-2027-routing-evidence.md) and the [exhaustive B4/B5 audit](docs/mia-bench-b4-b5-audit-2026-10-24.md).

## Reproduce the reported tables offline

**Requirements:** Python 3.10 or newer; the main routing-evidence check uses only the Python standard library and committed repository files.

```bash
git clone https://github.com/hollylessthan/governed-metric-decisions-artifact.git
cd governed-metric-decisions-artifact
python scripts/agent_2027_routing_evidence.py --check
```

This command reads the committed holdout synthesis, B4/B5 audit, provider scenario actions (Qwen, OpenAI, Anthropic), governance-pair source, and frozen manifest generator. It reconstructs the routing-evidence JSON and Markdown, checks recorded SHA-256 input hashes, and fails if checked outputs or paper tables differ.

For the separate label-error audit check:

```bash
PYTHONPATH=src python scripts/agent_2027_label_error_audit.py --check
```

The [GitHub Actions reproduction workflow](.github/workflows/reproduce.yml) runs these checks and verifies checksums for the original frozen holdout evidence archives. Check the linked workflow run for the status of a particular commit. The commands are designed to verify committed evidence **without provider credentials, API cost, or fresh model calls**.

**What is reproduced:** saved-record integrity, deterministic analysis, audit reconciliation, and reported summary tables. **What is not reproduced:** live model sampling, numerical query execution, or deployment behavior. Do not replace frozen provider outputs with new inference when checking these published records; provider versions and stochastic outputs can change.

## Artifact guide

| Location | Contents |
|---|---|
| [`paper/agent-2027-routing-evidence.md`](paper/agent-2027-routing-evidence.md) | Generated result tables and interpretation boundaries |
| [`paper/agent-2027-routing-evidence.json`](paper/agent-2027-routing-evidence.json) | Machine-readable derived evidence and input hashes |
| [`docs/mia-bench-b4-b5-audit-2026-10-24.md`](docs/mia-bench-b4-b5-audit-2026-10-24.md) | Exhaustive offline disagreement audit and scope |
| [`reports/`](reports/) | Source summaries, detailed case records, and audit outputs |
| [`docs/`](docs/) | Frozen original evidence and analysis snapshots |
| [`config/`](config/), [`prompts/`](prompts/), [`src/`](src/) | Original settings, prompt material, and supporting code |
| [`scripts/`](scripts/) | Offline verification and analysis scripts |
| [`.github/workflows/reproduce.yml`](.github/workflows/reproduce.yml) | Automated, no-model-call reproduction |

## Provenance and interpretation

The imported source is [`hollylessthan/metric-intent-assurance`](https://github.com/hollylessthan/metric-intent-assurance), source revision [`f4cfd26d5fb1a2770a527ae31d25f8afebbc928f`](https://github.com/hollylessthan/metric-intent-assurance/commit/f4cfd26d5fb1a2770a527ae31d25f8afebbc928f). Generated evidence records file-level hashes so the copied inputs can be checked independently.

Original model prompts were frozen before holdout unlock, and their holdout outputs were collected under that protocol. **The selection of the present B4/B5 paper question and its additional audits was retrospective.** Results are descriptive, not a preregistered test of this particular comparison. The synthetic worlds and shared scenarios constrain generalizability. Action accuracy alone does not establish exact metric interpretation, numerical correctness, authorization enforcement, or production safety.

## Citation, licensing, and releases

The repository includes an [Apache-2.0 license](LICENSE). For a fixed research reference, cite a tagged GitHub release (and its corresponding commit) once one has been published; a Zenodo DOI can then archive that immutable snapshot. **At this writing no GitHub release or DOI is asserted here.** Avoid citing the moving `main` branch as though it were a frozen release.

This archive contains evidence and verification scripts, not an accepted-paper claim.
