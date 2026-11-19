# Tests

Manual verification checklist:

1. **Install succeeds**: `python -m pip install -e .` completes inside the venv and `python -c "import agentquant"` does not error (Python 3.10+).
2. **Demo artifact exists**: after `python run_app.py`, `results/demo_run.json` exists and contains trace records for three search iterations (analyze/propose/backtest/reflect/store steps present).
3. **Benchmark is paired and seeded**: `results/fair_search_benchmark.json` exists after step 5; all arms report on identical episode IDs and seeds. Re-running with the same seeds on fixture data reproduces identical scores (determinism check).
4. **Mutation arms collapse offline**: in the benchmark JSON, offline mutation-arm scores equal the random/fixed control (FallbackPlanner ignores prompt mutations). The report or your summary must state this; do not claim learning.
5. **Memory cutoffs enforced**: insert a trial dated after `AS_OF`, then run `agentquant memory beliefs --prompt "PROMPT" --as-of AS_OF`; the post-cutoff trial must not appear in the recall pack.
6. **Evidence tiers labeled**: every exported result (benchmark JSON, memo) carries a tier tag of `fixture`, `measured_historical`, `prospective`, or `unverified`; a fixture-only run must not produce a `measured_historical` label. Sharpe-based gate results show `insufficient_evidence`, not a forced pass.