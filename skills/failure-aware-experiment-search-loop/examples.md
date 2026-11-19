# Examples

## Example 1: Offline wiring check (no API keys)

Task input:
> "Set up AgentQuant and confirm the research loop runs. No API keys available."

Execution:
1. Clone, create venv, `python -m pip install -e .`.
2. `python run_app.py` → writes `results/demo_run.json` with three iterations and trace.
3. `python scripts/fair_search_benchmark.py --episodes 3 --seeds 7 11 19 --output results/fair_search_benchmark.json`.

Expected outcome: demo trace generated; benchmark JSON produced with all arms reporting. All results are tagged `fixture` tier. Because the FallbackPlanner does not consume prompt mutations, matching mutation-vs-random scores are reported as wiring evidence only, not learning.

## Example 2: Live-data agent run with memory recall

Task input:
> "Run the AgentQuant agent on SPY with tracing, then show me what memory says about momentum regime failures as of 2024-01-31."

Execution:
1. `agentquant run --ticker SPY --trace` → OHLCV fetch, agent loop, regime card, comparison table.
2. `agentquant memory trials --ticker SPY` and `agentquant memory beliefs --prompt "momentum regime failure" --as-of 2024-01-31`.

Expected outcome: run trace stored with provenance; recall pack returns only trials/beliefs with knowledge/market cutoffs at or before the as-of date, so no post-decision evidence leaks into the summary. Result tier is `measured_historical` only if data provenance and split are recorded; otherwise `unverified`.

## Example 3: Fair arm comparison with suite versioning

Task input:
> "Compare memory vs fixed search arms on 3 episodes across seeds 7, 11, 19, then version the suite so we can evolve it later."

Execution:
1. `python scripts/fair_search_benchmark.py --episodes 3 --seeds 7 11 19 --output results/fair_search_benchmark.json`.
2. Build a `BenchmarkSuite` manifest over the train/selection/sealed episodes with SHA-256 content hashes.
3. `verify_evolution(parent_suite, child_suite)` to confirm lineage; `validate_matched_reports(reports)` to confirm identical budgets, evidence tiers, and episode IDs before any cross-arm claim.

Expected outcome: paired-seed comparison JSON plus a content-hashed suite manifest. If arms share budget but the mutation arm matches fixed behavior (no live LLM), report the collapse explicitly. Promotion attempts on Sharpe return `insufficient_evidence`; record that abstention rather than overriding it.