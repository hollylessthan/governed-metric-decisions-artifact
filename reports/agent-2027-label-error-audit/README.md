# Expanded-label cross-check and exhaustive B4 error census

Post-hoc offline analysis. Authority errors use all 101 representatives per model, including B4/B5 agreements. Counts are model/scenario observations, not independent samples.

Separate implementation agreement: **600/600** frozen decisions (480 main and 120 holdout). This checks implementation consistency; it does not validate author-set policy conventions or the natural-language-to-canonical mapping. Existing independent expanded-benchmark audits were already completed before provider inference; this analysis collects no new annotations.

| Model | Errors /101 | Unsafe execution | ALLOW stopped | Wrong stop type | B5 also wrong | Same wrong action |
|---|---:|---:|---:|---:|---:|---:|
| qwen | 19/101 | 7 | 3 | 9 | 19 | 17 |
| openai | 3/101 | 3 | 0 | 0 | 3 | 3 |
| anthropic | 6/101 | 2 | 0 | 4 | 5 | 5 |

The 28 errors cover 22 distinct scenarios. Full error records, confusion matrices and category denominators are in summary.json. Categories below are full gold-reason sets and partition each model's population; they describe violated/missing requirements, not a demonstrated model reasoning mechanism.

| Gold reason set | Category n | Qwen errors | OpenAI errors | Anthropic errors |
|---|---:|---:|---:|---:|
| ALLOW | 37 | 3 | 0 | 0 |
| certification_required | 2 | 0 | 0 | 0 |
| dimension_not_supported | 4 | 2 | 0 | 0 |
| dimension_path_fanout_unsafe | 6 | 2 | 0 | 0 |
| fanout_unsafe | 2 | 1 | 0 | 0 |
| fx_context_missing | 2 | 2 | 0 | 2 |
| metric_not_permitted | 3 | 0 | 0 | 0 |
| principal_not_authorized | 7 | 3 | 0 | 0 |
| reference_ambiguous | 3 | 0 | 0 | 0 |
| row_scope_missing | 1 | 1 | 0 | 1 |
| row_scope_not_permitted | 1 | 0 | 0 | 0 |
| semi_additive_time_violation | 3 | 0 | 0 | 0 |
| snapshot_point_missing | 4 | 2 | 0 | 0 |
| time_scope_future | 3 | 3 | 3 | 0 |
| time_scope_incomplete | 6 | 0 | 0 | 0 |
| time_scope_invalid | 2 | 0 | 0 | 2 |
| version_ambiguous | 5 | 0 | 0 | 1 |
| version_ambiguous_all_time | 4 | 0 | 0 | 0 |
| version_missing | 3 | 0 | 0 | 0 |
| version_not_applicable | 3 | 0 | 0 | 0 |

## Existing independent validation

The expanded benchmark already had an independent non-author blind audit: **57/60 agreement, Cohen’s kappa 0.925**. The separate R21 targeted correction audit reached **17/17**, with two labels subsequently corrected by R22; the R22 additivity check reached **8/8**, all CLARIFY. These are separate rounds, not a composite success rate or validation of every current label. Original return bytes and row counts are verified by this script.

See [original 60-case audit](../../docs/audits/final_blind_audit_adjudication_2026-10-05.md), [R21 targeted evidence](../../docs/audits/final_targeted_correction_audit_evidence_2026-10-05.md), and [R22 closeout](../../docs/audits/mia-bench-r22-additivity-audit-closeout.md). The earlier 48-case developmental audit and historical 72-case four-action study are distinct.

## Contract-sensitive interpretation

- End-only additive requests may inherit the earliest governed definition boundary. Nonadditive requests still require a start. This asymmetric convention explains some stops; it is not a universal analytics policy.
- Snapshot requests without an explicit timing operation require clarification even when a year is supplied. FX context and row scope omissions also require clarification rather than rejection.
- Future and reversed intervals are hard rejections in these worlds. Execution is an authority error even if a production system might permit forecasts.
- Hard violations override clarification; compiler support never overrides authority. These choices must remain visible in the manuscript and reviewer instructions.

## Optional supplementary annotation packet

review-packet.json contains 30 cases, selected without model outputs: first sorted case per taxonomy, additional world/gold strata, then sorted fill. It omits gold labels, reason codes, canonical requests, taxonomy names and model outputs. This is label-blinded, not guarantee of reviewer independence; some worlds and requests may be recognizable.

An external reviewer should read REVIEWER-CONTRACT.md, infer the request from surface plus principal, choose execute/clarify/reject, cite world facts and flag ambiguities. Freeze completed annotations before comparing with labels. Report three-way agreement, disagreements and adjudication separately; do not edit frozen labels silently. The new packet is unannotated and optional; it is not a missing-review or submission gate. Same-assistant checking does not replace the existing independent audits.
