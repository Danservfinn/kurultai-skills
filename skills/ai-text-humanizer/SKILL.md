---
name: ai-text-humanizer
description: Rewrite AI-sounding text so it reads naturally using a 35-pattern checklist derived from Wikipedia's "Signs of AI writing", without changing factual content, code, frontmatter, or link targets.
category: content
---

# AI text humanizer

## Goal

Rewrite AI-sounding prose so it reads like a person wrote it, without changing what it says. Apply the 35 patterns from Wikipedia's "Signs of AI writing" (maintained by WikiProject AI Cleanup). Preserve every factual detail; never invent names, numbers, dates, quotes, or citations.

## Inputs

- AI-sounding text pasted directly, or a file path to prose (e.g. `docs/launch-post.md`).
- Optional: a 2-3 paragraph writing sample for voice matching.

No API keys or external services are required.

## Steps

1. Read the input. If it is a file, read it with `cat` (or `sed -n` for a line range). Identify which parts are prose versus code blocks, data, YAML frontmatter, and link targets. Only prose will change.
2. Make a first rewrite pass. Do not treat the original structure as fixed. Apply the 35 patterns:
   - Content (1-6): inflated importance/legacy, name-dropping, shallow -ing analysis, sales language, vague sources, formulaic challenges-and-outlook.
   - Language (7-13): overused AI words (actually, additionally, gated on, quietly, testament, landscape, showcasing), avoiding is/are (serves as, features, boasts), "not X but Y" and clipped endings, forced triads, changing names and repeated sentence openings, false from-X-to-Y ranges, passive voice with missing subjects.
   - Style (14-19, 26-35): em/en dashes, excessive bold, bold mini-heading lists, title-case headings, emojis, curly quotes, too many hyphenated pairs, fake deeper truth, announcing the next point, heading repeated below itself, writing about the old version, forced punchlines/fragments, formulaic sayings, fake-candid openings, answering unraised objections, rejecting fake alternatives.
   - Chatbot (20-22): leftover chatbot text, knowledge-limit disclaimers and guesses, overly agreeable tone.
   - Filler (23-25): filler phrases, stacked qualifiers, generic positive endings.
3. Preserve all factual details. Names, numbers, dates, quotes, and citations must come from the source or the writer. If a detail is missing (e.g. a month, a neighborhood), ask the writer rather than inventing it.
4. Set the target voice. If a writing sample was provided, match its rhythm, word choice, punctuation, and deliberate quirks — the sample overrides default style rules, including the em-dash rule. Otherwise: keep the writer's style for personal writing; use neutral plain prose for technical/reference text.
5. Critique the first draft against the 35 patterns and the original claims. List anything that still sounds artificial, then rewrite those parts in a second pass. Do not over-apply patterns to deliberate choices (intentional repetition, real technical uses of "gating", "gate", "quality gates").
6. Write the final version. If the input was pasted text, present it inline. If the input was a file, write the result with a heredoc to a new output file (default `<INPUT_FILE>.humanized.md`, never the input path), then verify with `diff` that only prose lines changed. Remove any backup file you created before finishing.
7. Show the work: present the first-pass rewrite and a short critique of remaining AI-sounding parts before the final version.

## Outputs

- Humanized final text preserving original meaning and facts.
- First-pass draft plus a short critique of remaining artificial-sounding patterns.

## Failure modes

- Inventing factual details (names, dates, numbers) not present in the source.
- Over-applying patterns to deliberate stylistic choices (intentional repetition, real technical uses of "gating").
- Altering code, frontmatter, or link targets when processing files — verify with `diff` before delivering.
- Missing the writer's voice when no sample is provided.
- Overwriting the input file in place or leaving stray `.bak` files in the working tree.

## Source

https://github.com/blader/humanizer (MIT). Pattern list derived from Wikipedia's "Signs of AI writing" (https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. Accessed 2026-08-19.