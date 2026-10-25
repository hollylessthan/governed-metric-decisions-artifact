# Evaluating Pre-Execution Decisions for Governed Metric Requests

Recentered prose draft; strengthening review, 2026-10-25 PT. Current scope: [routing plan](agent-2027-plan.md). Counts come from [generated routing evidence](agent-2027-routing-evidence.md) and the [exhaustive B4/B5 audit](../docs/mia-bench-b4-b5-audit-2026-10-24.md). This is a manuscript argument before IEEE composition, final citations and page fitting. It supersedes the [retained MIA-centered draft](agent-2027-mia-argument-skeleton-2026-10-24.md). No new inference was performed.

## Abstract draft

Before an analytics agent issues a governed metric request, it must decide whether the request is authorized and sufficiently specified. We evaluate direct and candidate-assisted execute/clarify/reject routing over native metric-request semantics in four controlled worlds and three model families. The original prompts were frozen before holdout unlock and outputs collected prospectively; the present paper framing and additional analyses are retrospective. On 101 authority units per model, direct routing permits 34/37, 37/37 and 37/37 ALLOW requests while executing 7/64, 3/64 and 2/64 requests that require clarification or rejection. Across 15 identical-request governance pairs, its two execute/stop decisions are both correct on 11, 15 and 15 pairs, while both exact three-way actions are correct on eight, 15 and 14; lost pairs concentrate in principal-access changes. Decisions stay unchanged on nine pairs that alter only platform capability. Candidate-assisted review provides no consistent observed incremental advantage and introduces five dependency failures. The findings establish useful observed coverage and responsiveness to supplied governance changes, alongside residual execution risk even with complete facts. Synthetic policies and simultaneous changes to candidate visibility and review instructions limit generalization and causal interpretation. This is a decision-component study, not numerical-answer evaluation or certification of a safe enforcement boundary.

## 1. The decision before execution

An analytics agent may recognize the requested metric and still need to stop. A guest requesting a restricted metric should receive a rejection. An analyst requesting an ambiguous metric or omitting a required row scope may instead need clarification. Generating a plausible metric/API payload does not resolve these different obligations. Conversely, a permitted request should not be refused merely because the current backend lacks an implementation capability.

We study this decision component: given a request, governed world and principal, choose execute, clarify or reject under an explicit policy. A direct router makes the decision from those facts. A candidate-assisted router also reviews a structured interpretation produced upstream. The practical question is whether the additional candidate-review path improves the observed decisions while preserving useful execution.

The central finding has two sides: direct routing preserves substantial execution coverage and responds to many controlled governance changes, yet still executes some requests that should stop even when all governed facts are supplied. We retain every direction of disagreement with candidate review. The empirical contribution has a concrete scope: pre-execution decisions over native structured metric semantics, and identical-request pairs that test whether decisions track changed governed worlds. It does not introduce a new assurance algorithm or first governed-analytics benchmark. Native metric/API systems and broader policy-aware agent evaluation already exist; the [related-work comparison](agent-2027-related-work.md) sets out that overlap.

## 2. Contract, implementations and evidence

Execute means the request is authorized and sufficiently specified under the supplied governed facts. Clarify means material semantics or required information remain unresolved. Reject means a governed conflict exists; rejection takes precedence when a hard violation coexists with ambiguity. Authority is separate from backend feasibility. We score actions, without running numerical queries or evaluating complete agent planning/tool workflows.

B4 directly receives the natural-language request, world and principal context. B5 receives the same facts plus B2's frozen candidate and additional instructions to check fidelity between request and candidate. A material mismatch should cause clarification unless it creates a hard governed violation. Consequently, candidate presence and decision instructions change together. Request-only gold actions do not necessarily resolve every stricter request/candidate contract question.

Candidates represent governed metric names, dimensions, time and version directly in the study's fixed schema; this is not a claim of production semantic-layer API compatibility.

For context, B1 forms a semantic candidate or abstains; B2 also reports interpretation confidence; B3 applies a fixed 0.70 threshold to that confidence. These stages were not assigned final execution authorization. Their resulting execute/stop consequences are retained in the artifact, without treating them as equal-task authorization baselines or Text-to-SQL systems.

The workload contains 600 synthetic scenarios across commerce, finance, SaaS and support: 480 main scenarios and 120 originally sealed holdout scenarios. Qwen used all main scenarios; OpenAI and Anthropic used the same 120-case main replication subset. All three evaluated the 120 holdout scenarios. Excluding 18 feasibility scenarios and one duplicate leaves 101 holdout authority representatives per model: 37 ALLOW and 64 non-ALLOW.

B4 and B5 prompts were frozen before holdout unlock, and their original holdout outputs were collected prospectively under that frozen protocol, with bounded format-only repairs. They were not revised in response to holdout outputs. The original primary hypothesis concerned a different assurance comparison, whose results and MIA-specific subset remain in the artifact. The choice of this paper question, disagreement audit and additional pair analyses are retrospective/descriptive. We reuse the prospective outputs, preserve main/holdout separation and do not repurpose the original primary tests. This distinction preserves the strength of prospective collection without presenting the new analyses as preregistered hypotheses.

## 3. Decision quality and observed tradeoffs

Table 1 uses the full 101-unit authority population. ALLOW execution coverage measures permission to proceed, not exact-intent or numerical correctness. Unsafe execution means execute on a non-ALLOW request. Three-way correctness additionally requires the right refusal type. Technical failures remain failures and cannot earn correct clarification or rejection.

| Model | Route | ALLOW executes /37 | Unsafe executes /64 | Three-way correct /101 | Technical failures /101 |
|---|---|---:|---:|---:|---:|
| Qwen | Direct B4 | 34/37 | 7/64 | 82/101 | 0/101 |
| Qwen | Candidate B5 | 30/37 | 9/64 | 75/101 | 0/101 |
| OpenAI | Direct B4 | 37/37 | 3/64 | 98/101 | 0/101 |
| OpenAI | Candidate B5 | 37/37 | 4/64 | 96/101 | 0/101 |
| Anthropic | Direct B4 | 37/37 | 2/64 | 95/101 | 0/101 |
| Anthropic | Candidate B5 | 36/37 | 6/64 | 87/101 | 5/101 |

The proprietary direct routes permit all 37 ALLOW requests and stop 61/64 and 62/64 non-ALLOW requests respectively, so their coverage is useful. Nevertheless, every direct route still executes requests that require a stop, despite receiving complete governed facts. The 64 non-ALLOW units combine unresolved CLARIFY requests and prohibited REJECT requests; calling all 64 prohibited would misstate the task. The artifact separates those error types. Wrong clarification/rejection also remains visible in the three-way scores. These observations motivate retaining explicit, fail-closed enforcement for checkable policies rather than treating the LLM router as the sole enforcement boundary; the study does not validate a complete downstream enforcement design or a safe deployment threshold.

### Governance changes under identical requests

Fifteen authority pairs preserve the natural-language surface and canonical metric request while changing governed-world facts. Nine additional pairs concern backend feasibility and are excluded here. Table 2 measures whether both decisions within each authority pair are correct. The binary score concerns execute versus non-execute; exact scoring requires both execute/clarify/reject actions to match gold.

| Model | B4 binary /15 | B5 binary /15 | B4 exact /15 | B5 exact /15 |
|---|---:|---:|---:|---:|
| Qwen | 11/15 | 9/15 | 8/15 | 6/15 |
| OpenAI | 15/15 | 15/15 | 15/15 | 15/15 |
| Anthropic | 15/15 | 12/15 | 14/15 | 11/15 |

Only 14 pairs require an execute/stop change. The remaining pair requires rejection in both worlds, for different governed reasons; a correct pair therefore does not necessarily change action. On the 14-change subset, both exact actions are correct for B4/B5 on 8/14 versus 6/14 Qwen, 14/14 versus 14/14 OpenAI, and 13/14 versus 10/14 Anthropic pairs. Complete pair IDs and counts are retained in the artifact.

These checks provide evidence of observed responsiveness to changed supplied facts beyond aggregate accuracy. They do not establish a new causal mechanism or production robustness. The small, shared pairs are descriptive, and binary correctness can conceal a wrong refusal type; Anthropic B4's 15/15 binary result is 14/15 under exact scoring.

Grouping pairs by the governed fact that changed shows where failures concentrate ([differentiation evidence](agent-2027-differentiation-evidence.md)). Cells give pairs with both exact actions correct, B4 / B5.

| Governance change | Pairs | Qwen | OpenAI | Anthropic |
|---|---:|---|---|---|
| Principal access | 5 | 2 / 1 | 5 / 5 | 5 / 2 |
| Certification status | 2 | 2 / 2 | 2 / 2 | 2 / 2 |
| Relationship path | 4 | 2 / 1 | 4 / 4 | 4 / 4 |
| Aggregation safety | 3 | 2 / 2 | 3 / 3 | 3 / 3 |
| Required FX context | 1 | 0 / 0 | 1 / 1 | 0 / 0 |

Principal access is the largest single source of lost pairs: three of seven for Qwen B4, four of nine for Qwen B5 and three of four for Anthropic B5. Four pairs remove only the requester's role membership. Qwen executes three of the four role-revoked requests under B4 and all four under B5. Anthropic B4 rejects all four, while Anthropic B5 executes three, although the upstream candidate on each remains unauthorized under the oracle; the review stage did not inherit an authorized misinterpretation. On the FX pair, Qwen and Anthropic reject where missing context requires clarification: safe under binary scoring, wrong under exact scoring. Categories contain one to five pairs, so this locates errors in this workload rather than estimating prevalence.

### Invariance to platform capability

The nine excluded feasibility pairs test the opposite property. Each changes only the platform compiler's capability (group-by, ratio or snapshot support); both members are authorized, so the correct action is execute in both worlds. B4 and B5 execute both members of all nine pairs in every model, with no clarify or reject on any of the 54 scenario outputs per route. The routes therefore keep authorization separate from implementation capability, as their prompts instruct. This is a small instruction-following check under explicit facts, not evidence of robustness when capability and policy information are mixed or incomplete.

### All direct-router errors, including shared failures

A separate census covers every B4 error on the 101 authority representatives, rather than only B4/B5 disagreements: 19 Qwen, three OpenAI and six Anthropic model/scenario errors, covering 22 distinct scenarios. B5 is also wrong on 27 of these 28 records, with the same wrong action on 25. These overlapping observations are descriptive, not independent samples or evidence of a common causal mechanism.

The categories qualify the access-pair finding. Principal-access changes account for the largest absolute pair losses in the affected routes, but the full error census reveals other weaknesses. All three OpenAI errors execute the three future-dated requests that these worlds require rejecting. Anthropic clarifies both reversed intervals, executes a version-ambiguous and a missing-row-scope request, and rejects both missing-FX-context requests that require clarification. Qwen errors span access, time, relationship grain, snapshot timing and missing context; it also stops three ALLOW requests. Thus neither governance-pair scores nor low unsafe execution alone capture correct refusal behavior. The [complete census](../reports/agent-2027-label-error-audit/README.md) supplies all error IDs and category denominators, including categories with no observed errors.

### Exhaustive disagreement review

All 21 holdout disagreements belong to authority representatives and cover 18 distinct scenario IDs. Table 3 describes model/scenario records; overlapping workloads and counterfactual relationships prevent treating the total as an independent new sample.

| Model | Disagreements | B4 only correct | B5 only correct | Neither correct |
|---|---:|---:|---:|---:|
| Qwen | 9 | 7 | 0 | 2 |
| OpenAI | 2 | 2 | 0 | 0 |
| Anthropic | 10 | 9 | 1 | 0 |

Five Anthropic B4-only observations are B5 dependency failures: B2 did not produce a valid candidate and B5 was not called. Among the other 16 records, 12 have no candidate-field difference after metric-alias and dimension-order normalization. Reference matching includes candidates that preserve ambiguity or missing information; it does not mean those requests should execute. Three Qwen candidates add entity paths that remain ALLOW under the oracle. These cases leave an unresolved question about B5's stricter fidelity contract. The remaining Anthropic candidate adds row scope but remains unauthorized, so stricter refusal instructions do not justify B5's execute action.

Candidate review does sometimes help. On the reversed-interval case `MB3-E4E42C483E9B96F6`, Anthropic B5 changes clarify to the required reject while its candidate matches the reference fields. A different distinction appears on Qwen's fanout-unsafe case `MB3-4665298BEC0D77E3`: B5 changes execute to clarify, preventing execution but still missing the required reject. The latter is a binary safety improvement and a three-way error, not a correct refusal.

The separate main-set action supplement preserves favorable B5 observations: B5 alone is correct in 11 Qwen and one OpenAI full-scenario disagreements. It also retains 43 Qwen, one OpenAI and 14 Anthropic B4-only correct observations. These use different main sample sizes and are not pooled with holdout. Main coverage is action-only rather than raw-main candidate diagnosis.

The audit therefore supports an observed operating comparison but does not explain the difference as candidate corruption or anchoring. Prompt framing, stricter task obligations and single-run variability remain confounded. No reliable rule identifying when candidate review helps is established.

## 4. Engineering observations

First, retain a strong direct governed-router baseline before adding assurance/review stages. In these explicit worlds, its observed coverage and error profile are useful reference points. An additional component needs evidence of incremental value; direct routing still has errors and is not a universal replacement for enforcement. The artifact's additional deterministic candidate-assurance binding (MIA) permits only 8/37, 12/37 and 7/37 ALLOW requests and has 75–81 coverage gaps per 101 units, including both task constructs outside this binding's support and candidate-induced support gaps. Candidate-field differences alone do not prove semantic error. It also returns gaps on 6–11 of the 18 capability-pair scenarios that both routers execute. Its non-execution must be interpreted together with support and coverage, not as verified policy refusal.

Second, evaluate the assignment a component actually receives. Interpretation confidence does not assess authorization, and a request-only decision is not identical to reviewing the fidelity of an existing candidate. Score differences across those assignments require contract-aware interpretation.

Third, report exact refusal type and stage failures alongside unsafe execution and coverage. A wrong clarification can prevent execution without correctly enforcing a prohibition. An unavailable upstream candidate can prevent the review stage from running. Counting either as a successful policy refusal obscures behavior that engineers need to inspect.

## 5. Validity and positioning

These are controlled synthetic worlds with author-set policies. A separately implemented dictionary-based rule checker agrees with all 600 frozen labels, including all 120 holdout labels; it consumes requests and worlds without label/reason fields or oracle helper calls. This same-assistant implementation cross-check does not independently establish natural-language interpretation or policy validity. Independent expanded-benchmark review was completed before provider inference: the [original blind audit](../docs/audits/final_blind_audit_adjudication_2026-10-05.md) reached 57/60 agreement (kappa 0.925); a [targeted R21 check](../docs/audits/final_targeted_correction_audit_evidence_2026-10-05.md) reached 17/17, with two labels subsequently corrected by R22; the separate [R22 additivity check](../docs/audits/mia-bench-r22-additivity-audit-closeout.md) reached 8/8. These samples and correction rounds do not validate every current label and must not be pooled. The newly prepared 30-case packet is optional supplementary review, not a missing independent-validation gate. End-only additive intervals inheriting the governed lower bound, snapshot timing requirements, and future dates being prohibited are explicit benchmark conventions rather than universal analytics rules. Full governed facts are supplied; real context retrieval, incomplete registries and changing production policies are not tested. Related scenarios and small denominators limit generalization. The outputs were collected prospectively under frozen prompts, while the new framing and additional analyses are retrospective; prompts differ and neither action counts nor field diagnostics identify a causal candidate effect. Agreement between B4/B5 does not imply correctness; the artifact retains shared errors as well as disagreements.

Closest work includes native semantic-layer and governed analytics API systems, policy-grounded analytics and agent assessment beyond task completion. Our concrete evaluation focus is native structured metric-request semantics without SQL generation and fixed-request governance pairs. GROUND evaluates governed Text-to-SQL, including undefined-metric and clarification traps, and finds model judgment fallible where code-level enforcement is deterministic; we cite rather than claim that lesson. Decision-SQL scores answerable, authority-blocked, ambiguous and policy-blocked decisions; its documented counterfactual executions assess candidate SQL under changed database fixtures. Our paired decisions hold the request fixed while changing model-visible governed worlds, and capability pairs test invariance when only platform support changes. This distinguishes the inspected evaluation setup without claiming that prior systems cannot support related tests. These provide a domain-specific characterization of pre-execution decisions; they do not by themselves prove a first benchmark or that prior governed systems lack these capabilities. A final manuscript must substantiate that value against these primary sources. We make no numerical-answer, complete-agent reliability, calibrated-risk, contemporaneous cost/latency or production-safety claim.

Direct routing preserves useful observed coverage and often tracks controlled governance changes, yet residual execution errors remain even with complete facts. Candidate review adds isolated benefits and dependency failures without a consistent observed incremental advantage here. The engineering implication is to evaluate decision quality, exact refusal semantics and support together, and retain explicit enforcement of checkable policies rather than assuming high model coverage is sufficient.
