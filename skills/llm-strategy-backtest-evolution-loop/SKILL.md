---
name: llm-strategy-backtest-evolution-loop
description: Run an LLM-driven iterative research loop over a YAML stock strategy with AlphaEvo — backtest, diagnose, mutate, re-test behind anti-overfit gates, and export an evidence trail. Use when the user wants to evolve, optimize, or stress-test a quant strategy from a repo like github.com/ZhuLinsen/alphaevo and needs auditable artifacts (research report, LLM evidence, trajectory JSONL, trial ledger).
category: ops-automation
---
```

# LLM Strategy Backtest Evolution Loop

## Goal

Take a YAML strategy (entry/exit/params DSL), establish a backtest baseline, run LLM-driven evolution for a fixed number of rounds, gate every mutation through walk-forward / train-val-test gap checks, verify no false promotions on noise, register survivors for forward shadow tracking, and export the full evidence trail.

## Inputs

- A cloned copy of the AlphaEvo repo (or a repo exposing an `alphaevo` CLI). Verify the CLI surface exists before relying on it — see Step 1.
- A strategy YAML file, or a strategy ID already known to the strategy store (e.g. `rsi_reversion_v1`). The DSL uses `entry.triggers/guards`, `exit.stop_loss/take_profit`, `params.tunable`.
- Market data: either a bundled snapshot (no key needed for showcase-style runs) or a live adapter (`yfinance` for US/global, `akshare` for A-share). Requires the matching pip extra.
- An LLM API key and model name for `--method llm` runs (env vars named per the repo's README, e.g. `ALPHAEVO_API_KEY` / `ALPHAEVO_LLM_MODEL` — confirm with `alphaevo evolve --help`). Model names are provider-specific strings like `openai/gpt-4o`; do not assume a specific identifier, use one your key actually supports.
- Evolution parameters: rounds, samples, date range (`--start` / `--end`), output directory.

## Steps

1. **Install and sanity-check the CLI.** From the repo root, install with extras as documented in the README (e.g. `pip install -e ".[llm,data-yfinance]"`). Then run `alphaevo --help` and `alphaevo evolve --help` and read the output. If any command or flag used below (`run`, `evolve`, `optimize`, `tree`, and any `rsi`/`truth`/`shadow` subcommands) does not appear in the help text, stop and adjust to the actual CLI surface — do not guess flags.
2. **Set environment variables** for the LLM provider (key and model). Confirm the exact variable names from the repo's Quick Start section; if they differ, use the repo's names.
3. **Run a baseline backtest**: `alphaevo run <strategy_id> --adapter yfinance --start <date> --end <date>` (check `alphaevo run --help` for supported flags). Record signals, win rate, avg return, max drawdown, and score. A zero-signal baseline usually means contradictory/over-strict entry conditions — the LLM diagnosis step is designed to catch this.
4. **Start LLM evolution**: `alphaevo evolve <strategy_id> --method llm --rounds 3 --output reports/`. Each round the LLM receives backtest results, produces a failure diagnosis, and writes a small mutation to the YAML (e.g. `entry.logic and->or`, `stop_loss pct->atr`, parameter value changes). The system re-backtests after each mutation; changes are kept only if they improve out-of-sample-penalized fitness and pass walk-forward / train-val-test gap gates. Expect some or all mutations to be rejected — that is the gates working, not a failure.
5. **Optionally run parameter search** with overfit rejection. Inspect `alphaevo optimize --help` first; use whatever objective/rejection flags it actually documents (README shows an intent like `--objective robust_profit_quality --reject-overfit`, plus train/val gap caps). If those flags don't exist in the help output, skip this step and note it.
6. **Verify no false promotions on noise.** If the help output confirms `rsi null-audit` and `truth` subcommands exist, run `alphaevo rsi null-audit <id>` (shuffled-return null-signal controls) and inspect the append-only trial ledger with `alphaevo truth trials`. Otherwise record that these gates are unavailable in this build.
7. **Register survivors for forward tracking**: if `shadow` subcommands exist, run `alphaevo shadow register <id>` then `alphaevo shadow status` (forward commitments at T+5/T+10/T+20 decide promotion).
8. **Export evidence**: collect from the output directory the per-run artifacts — `<id>_research_report.md`, `<id>_llm_evidence.md`, `<id>_research_log.md`, and `trajectory/*.jsonl` (trajectory / sharegpt / preference exports). Render the lineage with `alphaevo tree <id>`. Do not rank runs done on different data windows or protocols against each other.

## Outputs

- Evolved strategy YAML versions with parent-child lineage (`alphaevo tree <id>`).
- `reports/<id>_research_report.md`, `<id>_llm_evidence.md`, `<id>_research_log.md`.
- `trajectory/*.jsonl` exports (trajectory, sharegpt, preference formats, per the Trajectory Data Flywheel docs).
- Trial ledger with Deflated Sharpe Ratio records (if `truth` is available).
- Shadow-ledger forward commitments and promotion status (if `shadow` is available).

## Failure modes

- **Unverifiable CLI surface**: commands/flags from the README may not match the installed build. Step 1's `--help` check is mandatory; the loop must degrade gracefully.
- LLM mutations may be rejected by anti-overfit gates — the strategy stays at baseline (documented behavior for already-reasonable strategies like `ma_crossover_v1`).
- Live data providers (yfinance/akshare) can introduce latency spikes and timeout-driven fallback.
- Zero-signal strategies from contradictory entry conditions require correct LLM diagnosis in round 1.
- Discovered factors are research artifacts and need human review before any production use.
- Different data windows/protocols produce incomparable results — never cross-compare runs.
- LLM API key missing/invalid: `--method llm` runs fail; the bundled-snapshot showcase path needs no key and can be used for a first validation instead.

## Source

- https://github.com/ZhuLinsen/alphaevo (README Quick Start, "How Self-Evolution Works", CLI Commands, Anti-Overfitting, Trajectory Data Flywheel sections)
- Source date: 2026-11-19