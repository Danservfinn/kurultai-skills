# Commands

Placeholders: `TICKER` (symbol, e.g. SPY), `EPISODES` (episode count), `SEEDS` (space-separated seed list), `OUTFILE` (benchmark output path), `AS_OF` (ISO date cutoff, e.g. 2024-01-31), `PROMPT` (recall-prompt text), `MEMO` (memo file path). All commands run inside the cloned repo with the venv activated.

## Step 1 — Clone and install

```bash
git clone https://github.com/OnePunchMonk/AgentQuant.git
cd AgentQuant
python -m venv .venv && source .venv/bin/activate
python -m pip install -e .
# optional extras:
python -m pip install -e ".[ui]"   # dashboard
python -m pip install -e ".[llm]"  # LLM-guided proposals (needs provider credentials)
```

## Step 2 — Offline demo loop

```bash
python run_app.py
# outputs results/demo_run.json
```

## Step 3 — Bounded agent run with tracing

```bash
agentquant run --ticker TICKER --trace
```

## Step 4 — Memory queries with provenance cutoffs

```bash
agentquant memory trials
agentquant memory beliefs
agentquant memory beliefs --prompt "PROMPT" --as-of AS_OF
```

## Step 5 — Fair search benchmark

```bash
python scripts/fair_search_benchmark.py --episodes EPISODES --seeds SEEDS --output OUTFILE
# e.g. --episodes 3 --seeds 7 11 19 --output results/fair_search_benchmark.json
```

## Step 7 — Export replay artifacts

```bash
python scripts/export_research_memo.py --replay MEMO
```

## Step 6 — Suite versioning

Suite construction, `verify_evolution`, and `validate_matched_reports` are Python APIs (see `docs/BENCHMARK_EVOLUTION.md`), invoked from a script or REPL inside the repo, not standalone shell commands. Use them via `python -c` or a project script; do not fabricate CLI flags the repo does not provide.