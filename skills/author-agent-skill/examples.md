# Examples — author-agent-skill

## Example 1: PDF form-field extraction skill

Input (Kurultai task):
"Skill task: extract form field names and types from PDF files so agents can fill them. Bundle a helper script if useful."

Run:
- `<skill-name>` = `pdf-form-extract`
- Frontmatter: `name: pdf-form-extract`, `description: Extracts AcroForm field names, types, and flags from PDF files using pdftk or python3 pypdf. Use when a task involves reading, listing, or filling form fields in a PDF.`
- Body: instructions to run `pdftk <file> dump_data_fields`, parse output, and report a field table; `## Examples` with a W-9 and an IRS-1040 case; `## Guidelines` noting encrypted PDFs require a password argument.
- Bundled: `scripts/dump_fields.py` (chmod +x), referenced as `scripts/dump_fields.py` in SKILL.md.
- Test: symlink into a scratch project's `.claude/skills/`, launch Claude Code, prompt "Use the pdf-form-extract skill on sample.pdf".

## Example 2: Brand-guidelines document skill

Input:
"Skill task: write customer emails using our brand voice: direct, no exclamation marks, sign-off '— The Kurultai Team'."

Run:
- `<skill-name>` = `kurultai-brand-voice`
- Frontmatter `name: kurultai-brand-voice`; `description` states trigger: "Use when drafting any customer-facing email, announcement, or support reply for Kurultai."
- Body: tone rules, banned phrases list bundled as `resources/banned-phrases.txt`; `## Examples` shows one compliant and one non-compliant rewrite; `## Guidelines` requires a final banned-phrase grep before sending.
- Test in `.claude/skills/`, invoke with "Use kurultai-brand-voice to draft an outage notice."

## Example 3: Repo template fallback

Input: clone of anthropics/skills where `/tmp/skills-repo/template` does not exist.

Run: step 1 detects absence, creates `./xlsx-report-gen/SKILL.md` manually using the README template pattern (`---\nname: xlsx-report-gen\ndescription: ...\n---`), proceeds with steps 3–7 unchanged. Validation still runs via PyYAML or the sed fallback.