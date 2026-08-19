# Commands

Placeholders:

- `<INPUT_FILE>` — path to the source file (e.g. `docs/launch-post.md`)
- `<OUTPUT_FILE>` — path for the result; default `<INPUT_FILE>.humanized.md`. Never equal to `<INPUT_FILE>`.
- `<START>`/`<END>` — line range of the prose section, if the file is long.

## Step 1 — read the input

```bash
cat <INPUT_FILE>
# or, for a long file:
sed -n '<START>,<END>p' <INPUT_FILE>
```

## Step 2-5 — draft, critique, second pass

LLM work; no shell commands. Track changes mentally or in a scratch file outside the working tree (`/tmp/humanizer-draft.md`):

```bash
cat > /tmp/humanizer-draft.md <<'EOF'
[first-pass rewrite]
EOF
```

## Step 6 — write the final version (file input)

Always write to a new file. Do not overwrite `<INPUT_FILE>` and do not create `.bak` files in the working tree:

```bash
cat > <OUTPUT_FILE> <<'EOF'
[final humanized text, with frontmatter/code/link targets reproduced byte-for-byte]
EOF
```

Verify only prose changed:

```bash
diff <INPUT_FILE> <OUTPUT_FILE>
```

Check frontmatter survived (if the input had any):

```bash
sed -n '1,/^---$/p' <INPUT_FILE> > /tmp/fm-in.txt
sed -n '1,/^---$/p' <OUTPUT_FILE> > /tmp/fm-out.txt
diff /tmp/fm-in.txt /tmp/fm-out.txt && echo "frontmatter identical"
```

Check link targets unchanged:

```bash
diff <(grep -o '](http[^)]*)' <INPUT_FILE> | sort) \
     <(grep -o '](http[^)]*)' <OUTPUT_FILE> | sort) && echo "links identical"
```

Clean up scratch files:

```bash
rm -f /tmp/humanizer-draft.md /tmp/fm-in.txt /tmp/fm-out.txt
```

## Step 7 — show the work

Present the first-pass draft, the critique, and the final text (or `<OUTPUT_FILE>` path) to the user. No commands.