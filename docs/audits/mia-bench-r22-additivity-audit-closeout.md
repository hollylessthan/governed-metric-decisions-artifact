# MIA-Bench R22 additivity targeted audit closeout

Date: 2026-10-05 PT
Branch: `mia-bench-g3-r22-r9b-closeout`

## Purpose

Round 9b identified an erroneous world-contract default: ratio/average metrics could inherit `additive_over_time=yes`. R22 corrected that contract so ratio/average versions are non-additive over time and regenerated the benchmark before provider inference.

Because this changes gold labels for end-only ratio/average requests, an independent targeted blind re-check was frozen before review and sent to the same class of non-author auditor used for the prior audit.

## Frozen packet

- blind packet rows: 8
- blind packet SHA-256: `faabea6aad432ab2ab561bf2457607ef4a103ee2418ae5c3780d07ab9734218f`
- private key SHA-256: `391c31f39eab9e6ca38a12dbdb0a250cecf458bc25f0dfc27aba16aef61738d7`
- selection rule: every main-split end-only ratio/average row affected by the corrected additivity invariant

## Auditor record

Senior data engineer, 10+ years relevant experience; not an author; no prior involvement in benchmark construction; blind pass completed 2026-10-05.

Returned raw CSV SHA-256: `f54f013e8602ac07a3e1a5b67ba1b74e62c1e6defd4fb59445c22d4833f249c3`.

The auditor-returned bytes are now preserved losslessly as deterministic gzip bytes encoded in:

`docs/audits/mia-bench-r22-additivity-blind-completed.csv.gz.b64`

After base64 decode and gzip decompress, the SHA-256 of the recovered CSV must equal the returned raw hash above. The recovered file has 8 rows and matches the frozen blind packet row-for-row on `audit_id`, `world_summary`, `principal`, and `surface`.

## Result

- 8 / 8 exact agreement with frozen gold
- auditor decisions: 8 CLARIFY / 0 ALLOW / 0 REJECT
- convention disagreements: 0

The auditor independently applied the corrected rule: for an end-only request, governed `valid_from` can supply the omitted lower bound only when exactly one definition covers the bounded interval **and** the metric is additive over time. Each of these eight cases uses a ratio/average metric with `additive_over_time=no`, so the missing start remains material and the correct action is CLARIFY.

The auditor explicitly noted that several metrics had changed additivity flags relative to earlier rounds. This was intentional: R22 corrects the erroneous ratio/average world facts identified in Round 9b; it is not a post-hoc change based on MIA/provider outputs. No prospective provider inference had occurred.

## Interpretation boundary

This is a **scoped correction check**, not a broad label-validation sample. All eight rows have the same expected label and the auditor instructions state the governing end-only rule. Its purpose is to verify that the corrected R22 world facts and rule are internally coherent and independently applied to every affected main-split end-only ratio/average row.

## Reporting boundary

This 8-case pass is a targeted validation of the R22 additivity correction, not a replacement for the original 60-case blind audit. Paper reporting should state:

- original blind audit: `57/60, Cohen's kappa = 0.925`;
- R21 post-correction targeted audit: `17/17`, while explicitly noting that two of those R21 labels (AOV through 2024 and forecast delta through 2025) were subsequently corrected by R22;
- R22 additivity-specific targeted check: `8/8`, described as a scoped correction check rather than a new general audit.

Do not report a composite `60/60` or composite kappa.

## Gate decision

**R22 audit gate: PASS.** E1-E3 from the external Round 9b review are now closed. Provider inference remains disabled. E4-E6 must be implemented and reviewed on a separate execution branch after the evidence-repair PR is merged to `main`, before the first benchmark provider call.
