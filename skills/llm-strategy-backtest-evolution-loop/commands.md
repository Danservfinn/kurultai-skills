# Commands — llm-strategy-backtest-evolution-loop

Placeholders:
- `<strategy_id>` — strategy YAML id, e.g. `rsi_reversion_v1`
- `<date>` — ISO date, e.g. `2026-01-01`
- `<rounds>` — integer, e.g. `3`
- `<api_key>` / `<model>` — your LLM provider key and a model string the key supports (e.g. `openai/gpt-4o`); confirm env var names from the repo README before exporting

## Step 1 — install and verify CLI surface
```bash
git clone https://github.com/ZhuLinsen/alphaevo.git
cd alphaevo
pip install -e ".[llm,data-yfinance]"
alphaevo --help
alphaevo evolve --help
alphaevo run --help
alphaevo optimize --help
```

## Step 2 — set LLM environment
```bash
export ALPHAEVO_API_KEY=<api_key>
export ALPHAEVO_LLM_MODEL=<model>
```

## Step 3 — baseline backtest
```bash
alphaevo run <strategy_id> --adapter yfinance --start <date> --end <date>
```

## Step 4 — LLM evolution loop
```bash
alphaevo evolve <strategy_id> --method llm --rounds <rounds> --output reports/
```

## Step 5 — optional parameter search (only flags confirmed via --help)
```bash
alphaevo optimize <strategy_id> --help
alphaevo optimize <strategy_id> --objective robust_profit_quality --reject-overfit
```

## Step 6 — noise/promotion audit (if subcommands exist)
```bash
alphaevo rsi null-audit <strategy_id>
alphaevo truth trials
```

## Step 7 — forward shadow registration (if subcommands exist)
```bash
alphaevo shadow register <strategy_id>
alphaevo shadow status
```

## Step 8 — export evidence
```bash
alphaevo tree <strategy_id>
ls reports/
ls reports/trajectory/ 2>/dev/null
```

## Optional — no-key snapshot showcase (if present in this build)
```bash
alphaevo showcase