# MIA-Bench 17-Case Targeted Correction Audit — Evidence Record

Date: 2026-10-05 PT

Auditor: senior data engineer, 10+ years in semantic-layer design, metric governance, and BI/analytics engineering; non-author; no prior involvement in case construction; blind pass.

Result: 17/17 exact agreement with zero convention disagreements **against the R21 labels that were frozen for that targeted re-audit**. This is a targeted post-correction re-audit and is reported separately from the original 60-case blind audit (57/60, Cohen's kappa 0.925). It must not be combined into a synthetic post-hoc kappa.

## Lossless evidence

The exact returned 17-row CSV is preserved as deterministic gzip bytes encoded in:

`final_targeted_correction_audit_returned_2026-10-05.csv.gz.b64`

After base64 decode and gzip decompress, its SHA-256 must be:

`854b3835e39b3f75e6b3da96fd6874245cf83b1fb8035c4aed1b879d1b1267cf`

The exact 17-row blind packet sent to the auditor is preserved similarly as:

`final_targeted_correction_audit_packet_2026-10-05.csv.gz.b64`

After decode/decompress, its SHA-256 must be:

`d9a1a7519d8dbb637d69bffc58db2361950a878c4b9299b1403ec440c78c8c8b`

Both files contain 17 rows with audit IDs spanning `FAUD-00B1209A8452` through `FAUD-F248A7B5F150` in the preserved ordering.

## R22 supersession note

Two of the 17 R21-agreement rows were subsequently corrected by R22 after the independent Round 9b additivity defect was identified:

- `FAUD-075BEF315EDE` — AOV through 2024: R21 ALLOW → R22 CLARIFY;
- `FAUD-C1A47016E5CD` — forecast delta through 2025: R21 ALLOW → R22 CLARIFY.

Both R21 auditor reasons relied on the then-displayed `additive_over_time=yes` world fact. R22 corrected ratio/average additivity at the world-contract level before provider inference. Of these two historical rows, **forecast delta through 2025 is present in the separate 8-case R22 additivity audit and was re-checked there**. AOV through 2024 is not in that regenerated 8-case main-split packet; its R22 label follows the corrected world-contract/oracle invariant and is not claimed as separately re-audited.

Therefore `17/17` must be described as agreement with the **R21 labels**, not as validation of the current R22 manifest.

## Reporting rule

Paper/report wording should remain:

- original blind audit: 57/60 exact agreement, Cohen's kappa 0.925;
- R21 post-correction targeted re-audit: 17/17 exact agreement, zero convention disagreements, with the explicit note that two of those labels were subsequently corrected by R22;
- R22 additivity-specific targeted check: reported separately from the 17-case result.

Do not report a composite `60/60, kappa=1.000` statistic because the latter 17 judgments were collected after benchmark corrections.
