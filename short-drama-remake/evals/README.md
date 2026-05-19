# short-drama-remake evals

This directory documents smoke tests for the public skill package. Do not place
real scripts, user source material, generated ingest output, or Downloads files
here.

## Smoke Tests

1. Run `python3 scripts/split_short_drama_source.py --self-test`.
2. Verify partial input is labeled as a sample/opening skeleton and does not make full-series claims.
3. Verify complete input still requires progressive reading before full-series skeleton claims.
4. Verify PDF duplicate heading-run warnings remain documented in `references/ingest-and-file-management.md`.

## Managed Gate Release Checks

Run from the skill root:

```bash
python3 scripts/remake_gate_checker.py --self-test
find references/fixtures -name fixture.yaml -print0 | xargs -0 -n1 python3 scripts/remake_gate_checker.py --fixture
PYTHONPYCACHEPREFIX=/private/tmp/short-drama-remake-pycache python3 -m py_compile scripts/remake_gate_checker.py
```

Expected coverage:

- blocked `script_draft.preflight` sets `body_generated=false`
- no forbidden `short-drama` or raw source reads in remake script nodes
- P10 consumes `resume_packet`, FGR, SIR, and RMR instead of rerunning full P9/P11/P12 nodes
- transaction atomicity prevents half-confirmed state
- stale/dirty/needs_sync reports block downstream script generation
- target-market adaptation blocks overseas/cross-market project planning and script drafting when missing or stale
- `/仿写 出海` without a selected concept generates overseas-adapted concept directions first
- `/仿写 出海` produces/refreshes `market-adaptation-report.md` only, without generating project plans, episode scripts, or reading `short-drama/references/overseas/*`
