# Commands

Placeholders: `<project-folder>` = path to the project; `<memory-file>` = markdown memory file (e.g., CLAUDE.md); `<text>` = memory text or search query; `<timestamp>` = output of `date +%Y%m%d%H%M%S`.

## Step 1 — Verify package
```bash
npm view unforgit name version repository homepage
```

## Step 2 — Install
```bash
npm install -g unforgit
unforgit --version
```

## Step 3 — Initialize
```bash
cd <project-folder>
unforgit init
```

## Step 4 — Import markdown (dry-run, then real)
```bash
unforgit md import <memory-file> --dry-run
unforgit md import <memory-file>
```

## Step 5 — Remember
```bash
unforgit remember "<text>"
```

## Step 6 — Recall
```bash
unforgit recall "<text>"
```

## Step 7 — Backup then export
```bash
cp CLAUDE.md CLAUDE.md.bak.$(date +%Y%m%d%H%M%S)
unforgit md export --format claude --out CLAUDE.md
diff CLAUDE.md.bak.* CLAUDE.md
```

## Step 8 — Team sync (requires configured remote)
```bash
unforgit push
unforgit pull
```

## Step 9 — Dashboard
```bash
unforgit web
# open http://localhost:3838 ; Ctrl-C to stop
lsof -i :3838   # if port conflict suspected