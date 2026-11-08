# Examples

## Example 1: Add a date picker to a React form (rung 4 — native platform)

**Input task:** "Users need to pick a delivery date on the checkout form in `web/`."

**Steps shown:**
1. Read `web/src/pages/Checkout.tsx`; note the form already renders fields via the repo's shared `Input` component. Trace: form state → `Input` → submit handler.
2. Ladder: (1) needs to exist, yes; (2) no date picker in the codebase; (3) n/a frontend; (4) **browser-native date input holds** — stop here. No library install, no calendar component.
3. Implement: `<Input type="date" value={date} onChange={...} label="Delivery date" aria-required />` — 10 lines, reusing `Input`'s existing label/validation/accessibility wiring.
4. No branch/loop/money/security logic → no test required.

**Closing report:** "Rung 4 (native platform). Reused the repo's `Input`. Skipped: timezone-aware delivery windows — shortcut: revisit if shipping outside UTC. Not checked: Safari < 14 date input rendering."

## Example 2: Sum a CSV column of money amounts (rung 7 + one test)

**Input task:** "Add an endpoint that sums the `amount` column of a user-uploaded CSV."

**Steps shown:**
1. Read `api/routes/reports.py`; trace upload → parse → respond. Note existing `parse_csv` helper handles malformed rows.
2. Ladder: (1) needs to exist; (2) no existing sum helper; (3) **stdlib holds**: `csv` + `Decimal` — stop at stdlib, no new dependency.
3. Implement ~15 lines: reuse `parse_csv`, convert with `Decimal` (money — never float), return `{"total": str(total)}`. Reject non-numeric rows with a 400, not a silent skip.
4. Money + parser → write one test: `test_reports_sum_amounts` covering valid rows, a malformed row, and a non-numeric amount. Run `pytest api/test_reports.py -q`.

**Closing report:** "Rung 3 (stdlib), reused `parse_csv`. Test added and passing. Skipped: streaming for very large CSVs — shortcut: revisit if uploads exceed 10 MB. Not checked: behavior on quoted commas in the amount column."

## Example 3: Debounce a search input (rung 6 — one line)

**Input task:** "The search box fires a request per keystroke. Debounce it."

**Steps shown:**
1. Read `web/src/components/SearchBox.tsx`; trace keystroke → `onChange` → fetch. Note the repo has no debounce util.
2. Ladder: (1) needed; (2) none in codebase; (3) stdlib n/a; (4) no native debounce; (5) check `package.json` — `lodash` already installed → `debounce` available, so it is one line.
3. Implement: `const onSearch = debounce(fetchResults, 300)` (plus cleanup on unmount — that is correctness, not extra code).
4. No risky branch/loop → no test.

**Closing report:** "Rung 6 (one line, via installed `lodash.debounce`). Not checked: request cancellation for in-flight stale requests — shortcut: revisit if results flicker under slow networks."