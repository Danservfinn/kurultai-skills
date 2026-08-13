#!/usr/bin/env bash
# surface-probe.sh — map a platform's public surface in one pass.
#
# Usage:  surface-probe.sh <base-url> [extra-routes-file]
#         surface-probe.sh https://example.com
#         surface-probe.sh example.com ./more-routes.txt
#
# Prints a TSV table (status, redirect, type, bytes, ms, title) for a standard route
# set plus any routes in the optional file, then lists sitemap.xml entries and
# summarizes what was found. Read-only: one GET per route, human-scale volume.

set -uo pipefail

BASE="${1:-}"
if [ -z "$BASE" ]; then
  echo "usage: surface-probe.sh <base-url> [extra-routes-file]" >&2
  exit 2
fi
case "$BASE" in
  http://*|https://*) ;;
  *) BASE="https://$BASE" ;;
esac
BASE="${BASE%/}"
EXTRA="${2:-}"

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

read -r -d '' ROUTES <<'EOF' || true
/
/pricing
/plans
/docs
/documentation
/guides
/quickstart
/api
/api/docs
/reference
/blog
/changelog
/roadmap
/about
/team
/careers
/contact
/customers
/case-studies
/login
/signin
/signup
/register
/dashboard
/demo
/status
/trust
/security
/privacy
/terms
/faq
/support
/help
/openapi.json
/swagger.json
/llms.txt
/llms-full.txt
/robots.txt
/sitemap.xml
/rss.xml
/feed
/.well-known/security.txt
/.well-known/ai-plugin.json
/mcp
/skill
/health
/healthz
/version
EOF

if [ -n "$EXTRA" ] && [ -f "$EXTRA" ]; then
  ROUTES="$ROUTES
$(grep -v '^[[:space:]]*#' "$EXTRA" | grep -v '^[[:space:]]*$')"
fi

FOUND=0; MISSING=0; REDIRECTED=0; ERRORED=0
HITS="$TMP/hits.txt"; : > "$HITS"

probe() {
  local path="$1" url body meta code ctype size ms eff title redir
  url="$BASE$path"
  body="$TMP/body"

  meta=$(curl -sS -L --max-time 15 --max-redirs 5 -A "$UA" \
           -H 'Accept: text/html,application/json,text/plain,*/*' \
           -o "$body" \
           -w '%{http_code}\t%{content_type}\t%{size_download}\t%{time_total}\t%{url_effective}' \
           "$url" 2>/dev/null) || meta=$'000\t-\t0\t0\t-'

  code=$(printf '%s' "$meta" | cut -f1)
  ctype=$(printf '%s' "$meta" | cut -f2 | cut -d';' -f1)
  size=$(printf '%s' "$meta" | cut -f3)
  ms=$(printf '%s' "$meta" | cut -f4 | awk '{printf "%d", $1*1000}')
  eff=$(printf '%s' "$meta" | cut -f5)

  redir="-"
  [ "$eff" != "$url" ] && [ "$eff" != "$url/" ] && redir="${eff#$BASE}"

  case "$ctype" in
    *html*)
      title=$(tr '\n\r\t' '   ' < "$body" \
              | grep -io '<title[^>]*>[^<]*' | head -1 \
              | sed 's/.*>//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/[[:space:]]\{2,\}/ /g' \
              | cut -c1-72)
      ;;
    *json*|*text*|*yaml*|*xml*)
      title=$(head -c 400 "$body" | tr '\n\r\t' '   ' | sed 's/[[:space:]]\{2,\}/ /g' | cut -c1-72)
      ;;
    *) title="[$ctype]" ;;
  esac
  [ -z "$title" ] && title="-"

  case "$code" in
    2*) FOUND=$((FOUND+1)); printf '%s\n' "$path" >> "$HITS" ;;
    3*) REDIRECTED=$((REDIRECTED+1)) ;;
    404|410) MISSING=$((MISSING+1)) ;;
    000) ERRORED=$((ERRORED+1)) ;;
    *) ERRORED=$((ERRORED+1)) ;;
  esac
  [ "$redir" != "-" ] && REDIRECTED=$((REDIRECTED+1))

  printf '%-4s\t%-22s\t%-16s\t%7s\t%5s\t%s\t%s\n' \
    "$code" "$path" "$ctype" "$size" "$ms" "$redir" "$title"
}

echo "# surface probe: $BASE"
echo "# $(date '+%Y-%m-%d %H:%M:%S')"
echo
printf '%-4s\t%-22s\t%-16s\t%7s\t%5s\t%s\t%s\n' \
  CODE ROUTE TYPE BYTES MS REDIRECT TITLE
printf '%s\n' "----------------------------------------------------------------------"

while IFS= read -r r; do
  [ -z "$r" ] && continue
  case "$r" in /*) ;; *) r="/$r" ;; esac
  probe "$r"
done <<< "$ROUTES"

echo
echo "# sitemap"
SM="$TMP/sitemap.xml"
if curl -sS -L --max-time 20 -A "$UA" -o "$SM" "$BASE/sitemap.xml" 2>/dev/null \
   && grep -qi '<loc>' "$SM"; then
  TOTAL=$(grep -ioc '<loc>' "$SM" 2>/dev/null || echo 0)
  echo "# $TOTAL <loc> entries; first 40:"
  grep -io '<loc>[^<]*' "$SM" | sed 's/.*>//' | head -40
  if grep -qi '<sitemapindex' "$SM"; then
    echo "# (this is a sitemap index — fetch the children for the full route list)"
  fi
else
  echo "# no usable sitemap.xml"
fi

echo
echo "# robots"
curl -sS -L --max-time 10 -A "$UA" "$BASE/robots.txt" 2>/dev/null \
  | grep -v '^[[:space:]]*$' | head -25 || echo "# none"

echo
echo "# summary: $FOUND ok / $MISSING missing / $REDIRECTED redirected / $ERRORED error"
echo "# live routes: $(tr '\n' ' ' < "$HITS")"
echo "#"
echo "# next: walk the nav and footer in a browser — this probe only guesses route names."
