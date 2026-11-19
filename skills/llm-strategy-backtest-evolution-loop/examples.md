# Examples — llm-strategy-backtest-evolution-loop

## Example 1: First-time setup with CLI verification

Input (Kurultai task):
```
Repo: https://github.com/ZhuLinsen/alphaevo
Goal: sanity-check the CLI, then evolve rsi_reversion_v1 with the LLM for 3 rounds
Key: sk-... (OpenAI-compatible), model: openai/gpt-4o
```

Agent run:
1. `git clone https://github.com/ZhuLinsen/alphaevo.git && cd alphaevo`
2. `pip install -e ".[llm,data-yfinance]"` (extras as documented in README; if install fails, plain `pip install -e .` plus `pip install yfinance` may suffice — confirm with `alphaevo --help`).
3. `alphaevo --help` → confirms which subcommands exist. Note anything missing (e.g. no `shadow` group) for later steps.
4. `alphaevo evolve --help` → confirms `--method`, `--rounds`, `--output`, and reads env var names for the key/model.
5. `export ALPHAEVO_API_KEY=sk-... ; export ALPHAEVO_LLM_MODEL=openai/gpt-4o`
6. `alphaevo run rsi_reversion_v1 --adapter yfinance --start 2026-01-01 --end 2026-06-30` → baseline metrics recorded verbatim (whatever the run prints; do not expect README numbers).
7. `alphaevo evolve rsi_reversion_v1 --method llm --rounds 3 --output reports/`
8. Collect `reports/rsi_reversion_v1_research_report.md`, `_llm_evidence.md`, `_research_log.md`, `reports/trajectory/*.jsonl`; run `alphaevo tree rsi_reversion_v1`.

Output summary: final score vs baseline, which rounds were accepted/rejected and why (from `_research_log.md`), and the evolution tree.

## Example 2: Zero-key smoke test before committing an API budget

Input:
```
Verify the pipeline works without spending LLM tokens, then decide whether to pay for the full LLM run.
```

Agent run:
1. `alphaevo --help`; if a `showcase` command exists (README documents one using a bundled snapshot), run `alphaevo showcase` — no key required.
2. Inspect the printed round-by-round chain (diagnosis → mutation → retest) to confirm the evolution mechanics work in this build.
3. Only then set env vars and run Example 1's step 7 with `--rounds 1` as a cheap paid test before `--rounds 3`.

## Example 3: Post-evolution audit and forward registration

Input:
```
Strategy ma_crossover_v1 evolved but I need proof it isn't overfit before anyone touches it.
```

Agent run:
1. `alphaevo --help` → check for `rsi`, `truth`, `shadow`, `optimize` groups.
2. If available: `alphaevo rsi null-audit ma_crossover_v1` → expect zero false promotions under shuffled-return controls; record the result either way.
3. `alphaevo truth trials` → export the append-only trial ledger with DSR records; check the number of trials counted against the actual rounds run.
4. `alphaevo optimize ma_crossover_v1 --help` first; then apply documented overfit-rejection flags (e.g. `--reject-overfit` with gap caps) if present.
5. `alphaevo shadow register ma_crossover_v1 && alphaevo shadow status` → forward commitments (T+5/T+10/T+20) become the promotion gate.
6. Deliverable: audit note stating that historical backtests can only veto, promotion requires forward shadow outcomes, plus the exported evidence files. Flag that if mutations were all rejected (score unchanged from baseline), that is the anti-overfit gates working as designed.