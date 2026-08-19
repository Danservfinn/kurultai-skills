# Tests

Manual checklist for a reviewer.

1. **In-place safety.** Run the skill on a file input. Confirm the output went to `<INPUT_FILE>.humanized.md` (or another new path), the original `<INPUT_FILE>` is byte-identical to before (`git diff -- <INPUT_FILE>` shows nothing if tracked), and no `.bak` files exist afterward: `find . -name '*.bak'` returns nothing.
2. **Non-prose preservation.** Given an input with YAML frontmatter, one fenced code block, and two markdown links, run the diff and link checks from commands.md Step 6. Frontmatter diff is empty; link-target diff is empty; diff output shows changes only on prose lines.
3. **No invented facts.** Feed text with a missing detail (e.g. "I spent five days in Lisbon" with no month). Confirm the skill asks for the month instead of supplying one, and that every name, number, and date in the final text traces to the input or the writer's answer.
4. **Pattern coverage.** Feed text containing at least: an em dash, an emoji, a "not just X, it's Y" construction, a forced triad, "serves as", and a generic positive ending. Confirm none survive in the final version.
5. **Voice matching.** Provide a writing sample that uses em dashes deliberately. Confirm the final version keeps em dashes (sample overrides pattern 14).
6. **Work shown.** Confirm the output includes the first-pass draft and a short critique before the final version, in that order.