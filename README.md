# Governed Metric Decisions — AGENT 2027 Reproduction Artifact (candidate)

**Draft / private until publication review.** This package contains the frozen source evidence and calculation script for the empirical study of governed-metric execution decisions. It is not yet an independently validated public release.

## Offline reproduce and check (no model API calls)

Requires Python 3.10+ and only the standard library:

```bash
python scripts/agent_2027_routing_evidence.py --check
```

The command reconstructs the published routing-evidence JSON and Markdown from:
- original holdout synthesis and B4/B5 case audit
- committed provider scenario actions (Qwen, OpenAI, Anthropic)
- the original governance-pair summary and frozen generated-manifest code
- exactly the original AGENT argument-skeleton tables

It validates SHA-256 hashes recorded in `paper/agent-2027-routing-evidence.json` and fails if any derived output or table differs. **Do not rerun the providers**: historic model outputs are frozen and live calls are neither deterministic nor required for this verification.

## Evidence scope

B4 (direct) versus B5 (candidate-assisted) is the central same-task descriptive comparison. B1–B3 are interpretation-stage context and not same-task authorization controls. MIA is retained in the original study history, not introduced here as a novel method. The population here is 101 authority units per model (37 ALLOW, 64 non-ALLOW); action correctness does not establish complete metric correctness or production safety. Retrospective descriptive selection is not a new confirmatory study.

## Current status and remaining review

Original source: `hollylessthan/metric-intent-assurance`, source revision `f4cfd26d5fb1a2770a527ae31d25f8afebbc928f` (as recorded by the generator). File-level hashes are in the generated JSON. Initial import also includes audit interpretation.

Before public release: run the command in a clean checkout, inspect differences if any, validate licensing/privacy/secrets, reconcile final camera-ready tables, add provider run snapshots/metadata where missing, and tag an immutable release. Public Zenodo DOI is optional and comes afterward. **A passing clean-room reproduction has not yet been recorded.**
