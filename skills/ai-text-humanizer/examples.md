# Examples

## Example 1: Humanize a pasted launch post

Input (pasted text):

> We're thrilled to announce that Kurultai 2.0 is here — and it's not just an update, it's a revolution in how teams work. Nestled within the breathtaking landscape of agent orchestration, this release marks a pivotal moment in the evolution of AI workflows. 🚀
>
> Kurultai 2.0 boasts three key pillars: speed, scale, and simplicity. Experts believe it plays a crucial role in modern deployments. The future looks bright!

First-pass rewrite:

> Kurultai 2.0 is available now. The release focuses on agent orchestration. It changes three things: startup time, concurrent agent count, and the config format.

Critique: "three things" triad is only justified if the release notes actually list three changes — check the source. "Experts believe" is a vague source; drop it or name who. No facts (version number, feature list) were invented; if the actual changes are unknown, ask the writer.

Final version (after writer confirms the changes are: 40% faster startup, 100-agent concurrency, YAML config):

> Kurultai 2.0 is out. Startup is about 40% faster, agents can run 100 at a time instead of 20, and workflows are configured in YAML instead of JSON.

## Example 2: Humanize prose in a file, leaving everything else alone

Input: `docs/launch-post.md` containing YAML frontmatter, a code block, and AI-sounding prose.

Invocation (plain language, per the source README):

> Please humanize the prose in docs/launch-post.md

Run:

```bash
sed -n '1,40p' docs/launch-post.md   # read and mark prose vs. code/frontmatter
```

Write the result to a new file, never over the input:

```bash
cat > docs/launch-post.humanized.md <<'EOF'
---
title: Launch post          # frontmatter copied byte-for-byte
---
...humanized prose...
```fenced code block copied unchanged```...
EOF
```

Verify only prose changed:

```bash
diff docs/launch-post.md docs/launch-post.humanized.md
```

The diff must show changes only on prose lines. Link targets (`](https://...)`) and code blocks must not appear in the diff.

## Example 3: Voice matching with a writing sample

Input: a writing sample plus AI text.

> Here's a sample of my writing for voice matching:
> [2-3 paragraphs of the writer's own writing — short sentences, occasional em dashes, dry asides]
>
> Now humanize this text:
> The platform serves as a testament to modern engineering. It's not just a tool — it's a companion for your workflow.

Behavior: the sample overrides default rules, including the em-dash rule (pattern 14). If the writer uses em dashes deliberately, keep them. Output:

> The platform is well built. It's a tool — a good one — and it stays out of your way.

Facts check: no claims added or removed; "well built" must be supported by the source text or dropped.