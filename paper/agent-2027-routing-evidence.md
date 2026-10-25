# AGENT routing evidence: generated tables

Recentered paper inputs, 2026-10-24 PT. Descriptive selection from completed evidence; the original frozen primary test concerned MIA, not this new paper question. No new inference or statistical tests.

## R1: Decision quality on the 101 authority units

Each row uses 37 ALLOW and 64 non-ALLOW units. AEC is action-only. Three-way correctness requires the exact execute/clarify/reject action. Models are reported separately; these are not repeated independent estimates.

| Model | Route | ALLOW executes /37 | Unsafe executes /64 | Three-way correct /101 | Terminal failures /101 |
|---|---|---:|---:|---:|---:|
| Qwen | B4 | 34/37 | 7/64 | 82/101 | 0/101 |
| Qwen | B5 | 30/37 | 9/64 | 75/101 | 0/101 |
| OpenAI | B4 | 37/37 | 3/64 | 98/101 | 0/101 |
| OpenAI | B5 | 37/37 | 4/64 | 96/101 | 0/101 |
| Anthropic | B4 | 37/37 | 2/64 | 95/101 | 0/101 |
| Anthropic | B5 | 36/37 | 6/64 | 87/101 | 5/101 |

## R2: Interpretation-stage context, not same-task authorization baselines

B1 forms candidates; B2 adds interpretation confidence; B3 thresholds that confidence at 0.70. They were not assigned the same final authority task as B4/B5. These action consequences do not establish that authorization confidence or SQL generation fails.

| Stage | Qwen: ALLOW /37; unsafe /64 | OpenAI: ALLOW /37; unsafe /64 | Anthropic: ALLOW /37; unsafe /64 |
|---|---|---|---|
| B1 | 37/37; 26/64 | 37/37; 22/64 | 37/37; 22/64 |
| B2 | 37/37; 52/64 | 37/37; 32/64 | 36/37; 25/64 |
| B3 | 37/37; 51/64 | 37/37; 32/64 | 36/37; 21/64 |

## R3: Exhaustive holdout disagreement outcomes

All 21 disagreements are authority units. B4-only counts include five B5 dependency failures. Totals across models are audit record counts, not independent-task sample sizes.

| Model | Disagreements | B4 only correct | B5 only correct | Neither correct | Unsafe executes prevented by B5 | Unsafe executes introduced with B5 |
|---|---:|---:|---:|---:|---:|---:|
| Qwen | 9 | 7 | 0 | 2 | 1 | 3 |
| OpenAI | 2 | 2 | 0 | 0 | 0 | 1 |
| Anthropic | 10 | 9 | 1 | 0 | 0 | 4 |

Candidate diagnostics: added_row_scope_still_unauthorized: 1; additional_oracle_valid_entity_path: 3; candidate_dependency_failure: 5; no_normalized_candidate_field_difference: 12.

## R4: Separate main-set action supplement

Full-scenario counts preserve favorable and unfavorable B5 observations. Qwen uses all 480 main scenarios; proprietary replications use the same 120-case subset. Authority-only denominators are 369 and 92 respectively. This is action-only evidence, not raw-main candidate diagnosis.

| Model | Scenarios | Disagreements | B4 only correct | B5 only correct | Neither correct |
|---|---:|---:|---:|---:|---:|
| Qwen | 480 | 64 | 43 | 11 | 10 |
| OpenAI | 120 | 2 | 1 | 1 | 0 |
| Anthropic | 120 | 14 | 14 | 0 | 0 |

## R5: Governance pairs under identical requests

Fifteen authority pairs preserve the request surface and canonical request while changing governed worlds. Fourteen require an execute/stop change; the remaining pair requires REJECT in both worlds. Binary correctness requires both execute-versus-non-execute decisions to be correct, not merely a change. It can credit a wrong refusal type or technical stop. Exact correctness requires both three-way actions.

| Model | Route | Binary correct /15 | Exact correct /15 | Binary correct, flip subset /14 | Exact correct, flip subset /14 |
|---|---|---:|---:|---:|---:|
| Qwen | B4 | 11/15 | 8/15 | 10/14 | 8/14 |
| Qwen | B5 | 9/15 | 6/15 | 8/14 | 6/14 |
| OpenAI | B4 | 15/15 | 15/15 | 14/14 | 14/14 |
| OpenAI | B5 | 15/15 | 15/15 | 14/14 | 14/14 |
| Anthropic | B4 | 15/15 | 14/15 | 14/14 | 13/14 |
| Anthropic | B5 | 12/15 | 11/15 | 11/14 | 10/14 |

These are descriptive responsiveness checks on supplied facts, not a novel causal mechanism, a new confirmatory test or evidence that every pair changes its gold action. The nine feasibility pairs are excluded.

## R6: Residual execution on requests requiring different stop types

The /64 non-ALLOW denominator combines CLARIFY and REJECT. It is not a denominator of 64 prohibited requests.

| Model | Route | Execute on CLARIFY | Execute on REJECT | Total unsafe /64 |
|---|---|---:|---:|---:|
| Qwen | B4 | 3 | 4 | 7/64 |
| Qwen | B5 | 4 | 5 | 9/64 |
| OpenAI | B4 | 0 | 3 | 3/64 |
| OpenAI | B5 | 1 | 3 | 4/64 |
| Anthropic | B4 | 2 | 0 | 2/64 |
| Anthropic | B5 | 3 | 3 | 6/64 |

## Sources and boundaries

Input base: `f4cfd26d5fb1a2770a527ae31d25f8afebbc928f`. Values come from the [holdout synthesis](../reports/mia-bench-holdout-synthesis/summary.json) and [merged B4/B5 audit](../reports/mia-bench-b4-b5-audit/summary.json); paired actions are checked against the [original pair report](../reports/mia-bench-contribution-assessment/summary.json) and committed scenario outputs. Full case review is in the [audit assessment](../docs/mia-bench-b4-b5-audit-2026-10-24.md). Input hashes are in [the companion JSON](agent-2027-routing-evidence.json).

The old 23-unit MIA-representability subset does not define this descriptive paper population. Original MIA tests, results and historical exact-intent CEC remain in [the retained legacy evidence sheet](agent-2027-evidence.md). No statistical superiority, equivalence, causal candidate effect, numerical correctness or production safety claim follows.
