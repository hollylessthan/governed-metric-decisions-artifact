"""Post-hoc descriptive count for the AGENT 2027 draft; no provider calls.

Counts authority units whose gold decision is non-ALLOW while the shared B2
candidate is itself ALLOW under the oracle. This is a request/candidate
authority-decision discrepancy, not by itself proof of information loss,
semantic fidelity or a causal model mechanism. Retained outside the current
routing paper's main narrative; the counting rule and results are unchanged.
Reads only the committed failure-decomposition case files.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'reports/mia-bench-failure-decomposition'
SYSTEMS = ('B4', 'B5', 'MIA', 'MIA_v21')


def summarize(model):
    path = CASES / f'{model}-cases.jsonl'
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    authority = [r for r in rows if r.get('authority_unit')]
    non_allow = [r for r in authority if r['gold_decision'] != 'ALLOW']
    lost = [r for r in non_allow if r['candidate_oracle_decision'] == 'ALLOW']
    return {
        'source': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'authority_units': len(authority),
        'non_allow_units': len(non_allow),
        'no_candidate_units': sum(r['candidate_oracle_decision'] is None for r in authority),
        'valid_candidate_over_non_allow': len(lost),
        'in_matched_subset': sum(bool(r['matched']) for r in lost),
        'executed': {s: sum(r['actions'][s] == 'execute' for r in lost) for s in SYSTEMS},
        'mia_coverage_gap': sum(r['actions']['MIA'] == 'coverage_gap' for r in lost),
        'cases': [{'scenario_id': r['scenario_id'], 'gold': r['gold_decision'],
                   'reasons': r['gold_reasons'],
                   'actions': {s: r['actions'][s] for s in SYSTEMS}} for r in lost],
    }


def main():
    print(json.dumps({m: summarize(m) for m in ('qwen', 'openai', 'anthropic')}, indent=2))


if __name__ == '__main__':
    main()
