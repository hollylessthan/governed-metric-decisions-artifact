# AGENT 2027 routing paper readiness

Updated 2026-10-24 PT after merged #224 and the user-approved positive-results framing. Controlling documents: [routing plan](agent-2027-plan.md), [outline](agent-2027-outline.md) and [prose draft](agent-2027-argument-skeleton.md).

**Conditional go for preparing an AGENT empirical short paper.** Strong method/benchmark novelty is not cleared; a useful original empirical contribution and the concrete manuscript still need skeptical review. The paper is not submission-ready merely because its results are positive. No new provider calls, release or submission occurs here.

## Progress and remaining work

| ID | Status | Deliverable / next action |
|---|---|---|
| W1: related work | Source comparison prepared; current positioning updated | [Native metric/API and agent-evaluation overlap](agent-2027-related-work.md). Complete final primary citations in the IEEE draft. |
| W2: scope/claims | Recentered | Current R-claims in [claim matrix](claim-evidence-matrix.md). B4/B5 central; B1–B3 contextual; MIA retained in the artifact with one binding-coverage sentence. No causal candidate claim or new confirmatory test. |
| W3: evidence | Prepared and checked | [Generated routing tables](agent-2027-routing-evidence.md), [hashes](agent-2027-routing-evidence.json) and merged exhaustive B4/B5 audit. Governance pairs now include verified binary/exact scores and /14 flip-subset counts. Original MIA/historical evidence and Claude's count remain retained. |
| W4: policies | Existing independent audits restored; automated cross-check complete | Expanded blind audit 57/60 (kappa 0.925); R21 targeted 17/17 with two later R22 corrections; separate R22 8/8 additivity check. Preserve round/version boundaries. The separate 600/600 implementation check is additional consistency evidence. [Audit history and optional packet](../reports/agent-2027-label-error-audit/README.md); no new annotation gate. |
| W5: contribution review | Conditional empirical go | Positive capability result and bounded operating comparison. No novel mechanism or acceptance probability established. Review whether the reusable evidence teaches enough beyond synthetic prompt performance. |
| W6: manuscript | Prose/outline recentered; IEEE composition pending | Produce and render five pages including references in an AGENT workspace. Review the manuscript's actual contribution and caveats; assess eight pages only if needed. |
| W7: artifact | Expanded source evidence retained; public packaging/reproduction pending | Include routing tables, decision contract/workload, original main/holdout provenance, all disagreements, frozen original results and offline commands. Historical public artifact-v1.0 alone is insufficient. Public release is separate. |
| W8: submission | Pending | Authors/affiliations/conflicts, citation accuracy, overlap declarations, current call, format/page limit and final user manuscript review. |
| J0/J1/J2: Jev extension | **Deferred, outside current paper** | Offline proposal/code retained, no results or execution. Conservative $20.30 reservation fails proposed $8/$10 bounds; live runner/accounting unfinished. Resolving J is not a current readiness prerequisite. |

The [earlier MIA-centered draft](agent-2027-mia-argument-skeleton-2026-10-24.md) and [legacy evidence sheet](agent-2027-evidence.md) remain available. MIA's null/mixed expanded result, original positive GPT result and lack of the same Claude benefit are not erased or silently reinterpreted as one pipeline experiment.

## Non-negotiable interpretation boundaries

- Use 101 authority representatives per holdout model (37 ALLOW/64 non-ALLOW) for the new descriptive focus; keep feasibility/duplicate and original 23-unit MIA-specific analyses separate.
- B4/B5 prompts were frozen before holdout unlock and original outputs collected prospectively, with bounded repairs and no prompt changes based on holdout outputs. Paper recentering and additional pair/disagreement analyses are retrospective. No untouched new validation or repurposed MIA-versus-B5 p-values.
- Fifteen authority pairs preserve the request while changing governed facts; only 14 require execute/stop flips. Both binary decisions correct is different from both exact actions correct. Native metric semantics and pairs are a concrete scope, not firstness proof.
- AEC is action-only. Do not claim numerical answers, exact intent, production safety, calibrated uncertainty or full-agent reliability.
- B1–B3 were assigned interpretation, not the same authority task. B4/B5 change instructions and candidate visibility together. No causal input ablation, anchoring mechanism or proven router-selection rule.
- Retain B5-only correct cases, wrong-stop distinctions and dependency failures. Reference field matching is not proof that a request is executable.
- No new MIA patch, model sweep, Jev run or spending is part of this manuscript path.

## Immediate next steps

1. Review the recentered draft and source-bound tables in #223; preserve merged #224's audit and all historical evidence.
2. Retain the existing independent-audit evidence and its correction/version boundaries in the manuscript; the new packet is optional supplementary work.
3. Compose/render the five-page IEEE manuscript, complete primary citations and assess the actual paper against AGENT's empirical contribution category.
4. Finish artifact packaging/reproduction and paper-to-artifact consistency, then author/conflict/overlap checks and user review before submission.

Targets (PT): Oct 25–28 IEEE drafting; Oct 29–Nov 4 artifact/review; Nov 5–11 revisions; aim Nov 12 submission. Official submission deadline November 13, 2026 AoE and notification December 11, per [the call](https://conf.researchr.org/track/icse-2027/agent-2027-papers); recheck before submission.

## Offline checks

```bash
python scripts/agent_2027_routing_evidence.py --check
PYTHONPATH=src python scripts/agent_2027_label_error_audit.py --check
PYTHONPATH=src python -m unittest discover -s tests -p test_b4_b5_audit.py -v
python scripts/mia_bench_b4_b5_audit.py --output /tmp/b4-b5-audit
python scripts/agent_2027_candidate_loss_count.py
```

The evidence generator/check and focused audit checks are part of this preparation. Full public-artifact reproduction remains W7. The old Jev preparation tests can still run offline but do not enable or require collection. Never regenerate missing provider evidence with fresh calls or change frozen values to make a paper check pass.
