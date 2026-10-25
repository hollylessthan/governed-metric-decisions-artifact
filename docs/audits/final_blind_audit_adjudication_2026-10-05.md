# MIA-Bench Final 60-Case Blind Audit — Original Result and Adjudication

Date of blind pass: 2026-10-05
Auditor profile: senior data engineer; 10+ years in semantic-layer design, metric governance, and BI/analytics engineering; non-author; no prior involvement in case construction; no author contact during the blind pass.

## Original blind result

- Cases: 60
- Auditor decisions: 22 ALLOW / 19 REJECT / 19 CLARIFY
- Gold decisions: 20 ALLOW / 20 REJECT / 20 CLARIFY
- Exact agreement: 57/60 = 95.0%
- Cohen's kappa: 0.925
- Convention disagreements recorded: 0
- Original returned CSV SHA-256: `4a37e13d3c2c72d457effbbd62b2ea3321f4b0df48526be7c0fbe51aa6ef1a63`

The original returned CSV is preserved losslessly as deterministic gzip bytes encoded in `final_blind_audit_returned_2026-10-05.csv.gz.b64`. After base64 decode and gzip decompress, the SHA-256 above must match. Any corrected descriptive alignment after adjudication must not be called blind agreement.

## Three disagreements

### FAUD-1E43A18D9802 — SaaS NRR through 2024

Gold: CLARIFY (`time_scope_incomplete`)
Auditor: ALLOW

R21 adjudication initially treated this as oracle over-strictness because the displayed world facts marked NRR v1 as `additive_over_time=yes`. Round 9b subsequently identified that world fact itself as erroneous: NRR is a ratio and must be non-additive over time. Therefore the auditor's ALLOW judgment was induced by an incorrect governed fact shown in the audit packet, not by a valid additive-ratio convention.

R22 correction: ratio/average metric versions derive `additive_over_time=False` from aggregation. Under the corrected world contract, an end-only NRR interval remains CLARIFY because the missing start is material to the ratio's meaning. The general end-only rule remains valid for truly additive metrics.

### FAUD-BEB56A5E0663 — Commerce units up to 2025

Gold: CLARIFY (`time_scope_incomplete`)
Auditor: ALLOW

Adjudication: **oracle over-strictness**. `units_sold` has one governed version from 2023 onward and is additive-over-time. The open start can be bounded by governed validity without creating version ambiguity.

Correction: for end-only intervals, use the earliest governed validity as the lower bound when exactly one applicable definition covers that interval and the metric is additive-over-time. Non-additive metrics still require clarification.

### FAUD-179CCF495BE1 — Commerce total seller count in 2025

Gold: REJECT (`semi_additive_time_violation`)
Auditor: CLARIFY

Adjudication: **surface-fidelity defect, not an oracle-label defect**. The canonical request encoded an explicit sum-over-time operation, but the surface phrase `total seller count in 2025` does not unambiguously convey that operation. A reader can reasonably interpret it as a coarse snapshot request, for which CLARIFY is correct.

Correction: snapshot sum-over-time surfaces must use explicit language such as `summed seller count` or `time-summed seller count`; do not use the ambiguous prefix `total`.

## Consequence for evidence status

The 57/60, kappa=0.925 result remains the immutable blind result for the pre-correction manifest. The three findings are treated as audit-discovered benchmark defects. The later targeted correction audit is reported separately and must not be combined into a post-hoc composite kappa.

Round 9b further corrects the ratio/average additivity defect before provider inference. Any affected final-audit rows must receive a targeted re-check after the R22 manifest is regenerated; this does not alter the original blind result.
