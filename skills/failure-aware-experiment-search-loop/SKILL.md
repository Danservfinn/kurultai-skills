---
name: failure-aware-experiment-search-loop
description: Run AgentQuant's bounded, reproducible agent research loop — propose experiments, evaluate under shared budget and seeds, store trials/failures with provenance, and fairly compare search policies
category: ops-automation
---

# Failure-aware experiment search loop (AgentQuant)

## Goal

Set up and run the AgentQuant research harness: a bounded analyze/propose/backtest/reflect/store loop over quantitative strategies, with failure-inclusive memory, provenance-tagged evidence tiers, and paired-seed comparison of search arms under identical budgets. Produce replayable artifacts (demo trace, benchmark JSON, memory records, suite manifests, research memos).

## Inputs

- Historical or synthetic price data (the CLI fetches OHLCV via `fetch_ohlcv_data`, e.g. `--ticker SPY`; the demo uses synthetic fixtures and needs no network or API key)
- Experiment budget: max iterations and cost model (per-arm tool call / wall-time / JSON-byte limits)
- List of search arms/policies to compare (fixed, search, frozen-agent, memory, mutation — defaults built into `scripts/fair_search_benchmark.py`)
- Random seeds for paired comparison (e.g. `7 11 19`)
- Optional: LLM provider credentials (install `.[llm]`) for live proposal backends; live arms must fail closed without credentials

## Steps

1. Clone and install:
   ```bash
   git clone https://github.com/OnePunchMonk/AgentQuant.git
   cd AgentQuant
   python -m venv .venv && source .venv/bin/activate
   python -m pip install -e .
   ```
   Requires Python 3.10+. Add `.[ui]` for the dashboard, `.[llm]` for LLM-guided proposals.
2. Run the offline demo loop: `python run_app.py`. This executes three search iterations on synthetic prices and writes `results/demo_run.json` showing the analyze/propose/backtest/reflect/store loop and its trace. It is a wiring demo, not a performance benchmark.
3. Fetch real data and run the bounded research agent: `agentquant run --ticker SPY --trace`. This chains `fetch_ohlcv_data` → `run_agent` with `TraceRecorder`, producing a regime card and a comparison table of candidate results.
4. Store and query trials and beliefs in the SQLite `MemoryService` with provenance. Use `agentquant memory` subcommands (trials, beliefs, `--prompt` for recall packs), filtered by as-of date, asset, and regime, so decisions only use pre-decision evidence.
5. Compare search policies fairly on shared episodes:
   ```bash
   python scripts/fair_search_benchmark.py --episodes 3 --seeds 7 11 19 \
     --output results/fair_search_benchmark.json
   ```
   This runs fixed, search, frozen-agent, memory, and mutation arms on identical data, budgets, and seeds.
6. Version the experiment suite: build a `BenchmarkSuite` manifest with content-hashed train/selection/sealed episodes, verify lineage with `verify_evolution(parent, child)`, and check that candidate reports share identical budgets, evidence tier, and episode IDs via `validate_matched_reports`.
7. Keep failed attempts in denominators, tag every result with an evidence tier (`fixture` / `measured_historical` / `prospective` / `unverified`), and export replay artifacts: traces, episode bundles, and research memos via `scripts/export_research_memo.py` (supports `--replay` for integrity-checked memo replay).

## Outputs

- `results/demo_run.json` — demo trace of the search loop
- `results/fair_search_benchmark.json` — arm comparison under matched budgets and seeds
- Versioned `BenchmarkSuite` manifests with content hashes and verified lineage
- SQLite memory records (trials, beliefs) with provenance and date cutoffs
- Research memo / episode bundle artifacts for integrity-checked replay

## Failure modes

- Offline mutation arms collapse to identical behavior without a live LLM backend (FallbackPlanner ignores prompt mutations); matching scores then falsely suggest learning. Live comparison must fail closed when `--live` credentials are missing.
- Hash chaining (gate ledger, fixture manifests) can be evaded by anyone able to rewrite and rehash the whole ledger unless the head hash is anchored externally.
- Fixture-tier results overclaimed as historical or prospective evidence. A fixture result is never a historical or prospective result; `unverified` applies when provenance is missing.
- In-process budget limits cannot stop hanging handlers; only `ToolBudget.isolate_process=True` (POSIX fork with deadline termination) enforces deadlines, and it is a cancellation boundary, not a security sandbox.
- Sharpe-based statistical gate abstains with `insufficient_evidence` pending a validated Deflated Sharpe Ratio; do not remove conservative abstention to force a promotion.
- UI/CLI surfaces may still dual-write legacy stores; verify which store a record came from.

## Source

- Repository: https://github.com/OnePunchMonk/AgentQuant (accessed 2026-11-19)
- `README.md`, `docs/AGENTQUANT_HARNESS_ARCHITECTURE.md`, `docs/ASSISTANT_TOOL_CONTRACT.md`, `docs/ASSISTANT_TOOL_EVALUATION.md`, `docs/BENCHMARK_EVOLUTION.md`
- Key code: `src/agent/agent_graph.py`, `src/agent/search_arms.py`, `src/memory/`, `src/cli.py`, `scripts/fair_search_benchmark.py`, `scripts/export_research_memo.py`, `gate/`