# Label-blinded expanded-request review

Status: optional new packet prepared; no new annotations collected for this packet. Existing expanded-benchmark independent audits are documented in README.md. This packet is not a missing-review gate. Do not describe the automated cross-check as independent human validation.

Use only this contract and review-packet.json before freezing your annotations. Do not inspect summary.json, the generator, existing gold labels, model outputs or the manuscript results. Record your identity/role, relationship to workload authors, date and any prior exposure; report partial blinding if appropriate. This is a purposive coverage sample, not a random estimate of label accuracy. It contains 30 cases spanning all 28 holdout taxonomy families; do not extrapolate agreement to all scenarios.

For every case, infer the semantic request from its surface and separately supplied principal. Set review.decision to ALLOW, CLARIFY or REJECT, record the interpreted metric, grouping, interval/version, temporal operation, currency, calendar, path and scope in review.request_interpretation, cite concrete world facts in review.evidence, and flag ambiguities in review.contract_ambiguities. Do not assume an upstream candidate or silently add missing scope/versions. Leave unresolved interpretations visible rather than forcing agreement.

## Decision contract

- ALLOW means semantically authorized and sufficiently specified. It is permission to execute, not a guarantee of backend feasibility or correct numerical output.
- CLARIFY means material interpretation or required context is unresolved. REJECT means a hard governed conflict. A hard conflict takes precedence over unresolved context.
- The supplied principal must belong to authorized_roles. Resolve metric names and aliases from the world: no resolution is a rejection, multiple resolutions require clarification.
- A dimension must be direct to the metric or owned by a reachable entity. Each relationship traversal must preserve measure grain. A fanout_safe edge allows forward many_to_one or one_to_one, and reverse one_to_many or one_to_one. Missing paths and unsafe-only paths are hard conflicts. An explicitly requested path must exist and preserve grain.
- Metric versions have inclusive valid_from/valid_to bounds (null end is open). Reject a missing explicit version, an explicit version not covering the requested interval, a reversed interval, an interval beyond clock_year, or one with no overlapping definition. Multiple overlapping definitions without an explicit version require clarification.
- Start-only requests need an end. Under this benchmark's author-set convention, end-only requests inherit the earliest metric definition's lower bound when a single additive definition covers the governed interval. Multiple definitions or nonadditive metrics leave ambiguity. Flag whether the surface supports this convention. No-date requests without an explicit version require clarification if multiple definitions exist; an explicit version supplies its own governed interval, provided it has begun by clock_year.
- If certification is requested, the selected definition must be certified. Summing across time is prohibited for a definition that is not additive_over_time. Snapshot requests supplying a year/range but no temporal operation require clarification about snapshot timing; year alone does not select an operation in this contract.
- When a requested currency differs from the chosen definition's currency, missing fx_context_available requires clarification. No conversion is needed for currency-less metrics.
- Apply policies whose role matches the principal and whose scoped_metrics is empty or includes the resolved metric. Denied metrics/dimensions require rejection. Missing required_row_scope needs clarification; an explicitly incompatible scope requires rejection.
- Calendar kind must be calendar or fiscal. A fiscal request uses the supplied fiscal calendar; an unusual start month alone does not prohibit it.
- compiler_capabilities describe implementation support. They do not change the authority decision. A valid request remains ALLOW if a backend feature is missing. Do not convert this distinction into a numerical-execution claim.

## Freeze and adjudication

Save completed annotations separately, preserving all 30 scenario IDs. Freeze the file and record its SHA-256 before opening labels or running comparisons. Compare exact three-way actions; report agreement and all disagreements, then adjudicate each with request/world evidence. Keep pre-adjudication annotations, rationale and any proposed label/contract changes. Do not silently change frozen benchmark labels or recompute original model outputs. No reviewer has been contacted or assigned by this change.
