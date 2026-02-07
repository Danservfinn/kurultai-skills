#!/bin/bash
# Receive messages from the OpenClaw agent network
# Usage: ./receive_signal.sh [--gateway|--logs] [OPTIONS]
#
# v0.2: Dual receive — Gateway API status polling or moltbot Railway log parsing.
# The old signal-cli-native service no longer exists as a separate Railway service.

set -e

# Configuration
GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://moltbot-railway-template.railway.internal:8080}"
GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
EXTERNAL_URL="${OPENCLAW_EXTERNAL_URL:-https://kublai.kurult.ai}"
MOLTBOT_SERVICE="${MOLTBOT_SERVICE:-moltbot-railway-template}"
DEFAULT_SINCE="5m"

# Parse arguments
MODE="logs"  # default: Railway log parsing
SINCE="$DEFAULT_SINCE"
FOLLOW=false
RAW=false
PLAN_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --gateway)
            MODE="gateway"
            shift
            ;;
        --logs)
            MODE="logs"
            shift
            ;;
        --plan)
            PLAN_ID="$2"
            shift 2
            ;;
        --since)
            SINCE="$2"
            shift 2
            ;;
        --follow|-f)
            FOLLOW=true
            shift
            ;;
        --raw)
            RAW=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [MODE] [OPTIONS]"
            echo ""
            echo "Modes:"
            echo "  --gateway     Poll Gateway API for plan status (requires OPENCLAW_GATEWAY_TOKEN)"
            echo "  --logs        Parse moltbot Railway logs (default, requires Railway CLI)"
            echo ""
            echo "Options:"
            echo "  --plan ID     Filter by plan ID (works with both modes)"
            echo "  --since TIME  Look back TIME for logs mode (default: 5m). Examples: 30s, 10m, 1h"
            echo "  --follow, -f  Stream logs continuously (logs mode only)"
            echo "  --raw         Show raw log output without filtering (logs mode only)"
            echo ""
            echo "Environment variables:"
            echo "  OPENCLAW_GATEWAY_URL    Gateway URL"
            echo "  OPENCLAW_GATEWAY_TOKEN  Gateway auth token"
            echo "  MOLTBOT_SERVICE         Railway service name (default: moltbot-railway-template)"
            echo ""
            echo "Examples:"
            echo "  $0 --gateway --plan plan-20260206-001"
            echo "  $0 --logs --since 5m"
            echo "  $0 --logs --follow"
            echo "  $0 --logs --raw --since 10m"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Determine effective URL
determine_url() {
    if curl -s --connect-timeout 2 "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo "$GATEWAY_URL"
    else
        echo "$EXTERNAL_URL"
    fi
}

case "$MODE" in
    gateway)
        if [[ -z "$GATEWAY_TOKEN" ]]; then
            echo "Error: OPENCLAW_GATEWAY_TOKEN not set"
            exit 1
        fi

        EFFECTIVE_URL=$(determine_url)

        if [[ -n "$PLAN_ID" ]]; then
            echo "Checking status for plan: $PLAN_ID"
            echo "---"
            RESPONSE=$(curl -s "$EFFECTIVE_URL/api/plans/$PLAN_ID/status" \
                -H "Authorization: Bearer $GATEWAY_TOKEN")
        else
            echo "Checking recent agent activity..."
            echo "---"
            RESPONSE=$(curl -s "$EFFECTIVE_URL/api/messages/recent" \
                -H "Authorization: Bearer $GATEWAY_TOKEN")
        fi

        if echo "$RESPONSE" | jq '.' > /dev/null 2>&1; then
            echo "$RESPONSE" | jq '.'
        else
            echo "$RESPONSE"
        fi
        ;;

    logs)
        # Check Railway CLI
        if ! command -v railway &> /dev/null; then
            echo "Error: Railway CLI not installed"
            echo "Install with: brew install railway"
            echo ""
            echo "Alternative: use --gateway mode instead"
            exit 1
        fi

        # Check project link
        if ! railway status &> /dev/null 2>&1; then
            echo "Error: Not linked to a Railway project"
            echo "Run: railway link"
            exit 1
        fi

        parse_logs() {
            local SENDER_NAME=""
            local SENDER_NUMBER=""
            local TIMESTAMP=""
            local FOUND_MESSAGES=0

            while IFS= read -r line; do
                # Filter by plan ID if specified
                if [[ -n "$PLAN_ID" ]]; then
                    if ! echo "$line" | grep -q "$PLAN_ID"; then
                        # Still capture envelope headers for context
                        if echo "$line" | grep -qE '^Envelope from: "'; then
                            SENDER_NAME=$(echo "$line" | sed -n 's/^Envelope from: "\([^"]*\)".*/\1/p')
                            SENDER_NUMBER=$(echo "$line" | sed -n 's/.*"\s*\(+[0-9]*\).*/\1/p')
                        fi
                        if echo "$line" | grep -qE '^Timestamp:'; then
                            TIMESTAMP=$(echo "$line" | sed -n 's/.*(\([^)]*\)).*/\1/p')
                        fi
                        continue
                    fi
                fi

                # Capture envelope headers
                if echo "$line" | grep -qE '^Envelope from: "'; then
                    SENDER_NAME=$(echo "$line" | sed -n 's/^Envelope from: "\([^"]*\)".*/\1/p')
                    SENDER_NUMBER=$(echo "$line" | sed -n 's/.*"\s*\(+[0-9]*\).*/\1/p')
                fi

                # Capture timestamp
                if echo "$line" | grep -qE '^Timestamp:'; then
                    TIMESTAMP=$(echo "$line" | sed -n 's/.*(\([^)]*\)).*/\1/p')
                fi

                # Capture message body
                if echo "$line" | grep -qE '^Body:|^Message body:'; then
                    BODY=$(echo "$line" | sed 's/^Body: //; s/^Message body: //')
                    echo "[$TIMESTAMP] $SENDER_NAME ($SENDER_NUMBER):"
                    echo "$BODY"
                    echo "---"
                    FOUND_MESSAGES=$((FOUND_MESSAGES + 1))
                fi

                # Also capture agent delegation messages from Node.js logs
                if echo "$line" | grep -qE 'agentToAgent|delegation|HANDBACK|STATUS-UPDATE'; then
                    echo "[agent] $line"
                    FOUND_MESSAGES=$((FOUND_MESSAGES + 1))
                fi
            done

            echo "$FOUND_MESSAGES"
        }

        if [[ "$FOLLOW" == "true" ]]; then
            echo "Streaming moltbot logs (Ctrl+C to stop)..."
            if [[ -n "$PLAN_ID" ]]; then
                echo "Filtering for plan: $PLAN_ID"
            fi
            echo "---"

            if [[ "$RAW" == "true" ]]; then
                railway logs --service "$MOLTBOT_SERVICE"
            else
                railway logs --service "$MOLTBOT_SERVICE" 2>&1 | parse_logs
            fi
        else
            if [[ "$RAW" == "true" ]]; then
                railway logs --service "$MOLTBOT_SERVICE" --since "$SINCE" --lines 200
            else
                echo "Checking moltbot logs from last $SINCE..."
                if [[ -n "$PLAN_ID" ]]; then
                    echo "Filtering for plan: $PLAN_ID"
                fi
                echo "---"

                RESULT=$(railway logs --service "$MOLTBOT_SERVICE" --since "$SINCE" --lines 500 2>&1 | parse_logs)

                # The last line of RESULT is the count
                FOUND_MESSAGES=$(echo "$RESULT" | tail -1)
                TOTAL_LINES=$(echo "$RESULT" | wc -l | tr -d ' ')
                if [[ "$TOTAL_LINES" -gt 1 ]]; then
                    MESSAGES=$(echo "$RESULT" | head -n $((TOTAL_LINES - 1)))
                    echo "$MESSAGES"
                fi

                if [[ "$FOUND_MESSAGES" == "0" || -z "$FOUND_MESSAGES" || ! "$FOUND_MESSAGES" =~ ^[0-9]+$ ]]; then
                    echo "No message content found in the last $SINCE"
                    echo ""
                    echo "Tips:"
                    echo "  Use --raw to see all log entries"
                    echo "  Use --gateway for API-based status checks"
                    echo "  Try --since 1h for a longer window"
                else
                    echo "Found $FOUND_MESSAGES message(s)"
                fi
            fi
        fi
        ;;
esac
