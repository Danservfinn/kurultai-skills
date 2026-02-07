#!/bin/bash
# Send a message to the OpenClaw agent network
# Usage: ./send_signal.sh "message" [--gateway|--signal|--dry-run] [--to AGENT_ID]
#
# v0.2: Dual transport — Gateway API (primary) or Signal relay (fallback)
# The old signal-cli-native-production RPC endpoint no longer exists.

set -e

# Configuration - override via environment
GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://moltbot-railway-template.railway.internal:8080}"
GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
EXTERNAL_URL="${OPENCLAW_EXTERNAL_URL:-https://kublai.kurult.ai}"
DEFAULT_RECIPIENT="${SIGNAL_RECIPIENT:-+19194133445}"
DEFAULT_AGENT="main"
SIGNAL_GROUP_ID="${SIGNAL_GROUP_ID:-BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=}"

# Parse arguments
MESSAGE=""
TRANSPORT="gateway"  # default: gateway API
TARGET_AGENT="$DEFAULT_AGENT"

while [[ $# -gt 0 ]]; do
    case $1 in
        --gateway)
            TRANSPORT="gateway"
            shift
            ;;
        --signal)
            TRANSPORT="signal"
            shift
            ;;
        --dry-run)
            TRANSPORT="dry-run"
            shift
            ;;
        --to)
            TARGET_AGENT="$2"
            shift 2
            ;;
        --group)
            TRANSPORT="signal-group"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 \"message\" [OPTIONS]"
            echo ""
            echo "Transports:"
            echo "  --gateway      Send via Gateway API (default, primary)"
            echo "  --signal       Send via Signal relay through gateway"
            echo "  --dry-run      Print message without sending"
            echo ""
            echo "Options:"
            echo "  --to AGENT     Target agent ID: main, researcher, writer, developer, analyst, ops"
            echo "                 (gateway mode only, default: main/kublai)"
            echo "  --group        Send to Signal group instead of DM"
            echo ""
            echo "Environment variables:"
            echo "  OPENCLAW_GATEWAY_URL    Gateway URL (default: http://moltbot-railway-template.railway.internal:8080)"
            echo "  OPENCLAW_GATEWAY_TOKEN  Gateway auth token (required for gateway/signal modes)"
            echo "  OPENCLAW_EXTERNAL_URL   External URL (default: https://kublai.kurult.ai)"
            echo ""
            echo "Examples:"
            echo "  $0 \"Hello Kublai\" --gateway"
            echo "  $0 \"\$(cat plan.md)\" --gateway --to main"
            echo "  $0 \"Status update\" --signal"
            echo "  $0 \"Preview message\" --dry-run"
            exit 0
            ;;
        *)
            if [[ -z "$MESSAGE" ]]; then
                MESSAGE="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$MESSAGE" ]]; then
    echo "Error: No message provided"
    echo "Usage: $0 \"message\" [--gateway|--signal|--dry-run] [--to AGENT_ID]"
    exit 1
fi

# Determine effective URL (internal or external)
determine_url() {
    # Try internal URL first, fall back to external
    if curl -s --connect-timeout 2 "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo "$GATEWAY_URL"
    else
        echo "$EXTERNAL_URL"
    fi
}

case "$TRANSPORT" in
    gateway)
        if [[ -z "$GATEWAY_TOKEN" ]]; then
            echo "Error: OPENCLAW_GATEWAY_TOKEN not set"
            echo "Set it with: export OPENCLAW_GATEWAY_TOKEN=<your-token>"
            exit 1
        fi

        EFFECTIVE_URL=$(determine_url)

        # Create temp file for request payload
        PAYLOAD_FILE=$(mktemp)
        trap "rm -f $PAYLOAD_FILE" EXIT

        cat > "$PAYLOAD_FILE" << EOFPAYLOAD
{
  "recipient": "$TARGET_AGENT",
  "message": $(echo "$MESSAGE" | jq -Rs .)
}
EOFPAYLOAD

        RESPONSE=$(curl -s -X POST "$EFFECTIVE_URL/api/message" \
            -H "Authorization: Bearer $GATEWAY_TOKEN" \
            -H "Content-Type: application/json" \
            -d @"$PAYLOAD_FILE")

        if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
            echo "Message sent via Gateway API to @$(echo "$RESPONSE" | jq -r '.recipient // "'"$TARGET_AGENT"'"')"
        elif echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
            echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
            exit 1
        else
            echo "Response:"
            echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
        fi
        ;;

    signal)
        if [[ -z "$GATEWAY_TOKEN" ]]; then
            echo "Error: OPENCLAW_GATEWAY_TOKEN not set"
            exit 1
        fi

        EFFECTIVE_URL=$(determine_url)

        PAYLOAD_FILE=$(mktemp)
        trap "rm -f $PAYLOAD_FILE" EXIT

        cat > "$PAYLOAD_FILE" << EOFPAYLOAD
{
  "recipient": "$DEFAULT_RECIPIENT",
  "message": $(echo "$MESSAGE" | jq -Rs .)
}
EOFPAYLOAD

        RESPONSE=$(curl -s -X POST "$EFFECTIVE_URL/api/signal/send" \
            -H "Authorization: Bearer $GATEWAY_TOKEN" \
            -H "Content-Type: application/json" \
            -d @"$PAYLOAD_FILE")

        if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
            echo "Message sent via Signal relay to $DEFAULT_RECIPIENT"
        else
            echo "Signal relay response:"
            echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
        fi
        ;;

    signal-group)
        if [[ -z "$GATEWAY_TOKEN" ]]; then
            echo "Error: OPENCLAW_GATEWAY_TOKEN not set"
            exit 1
        fi

        EFFECTIVE_URL=$(determine_url)

        PAYLOAD_FILE=$(mktemp)
        trap "rm -f $PAYLOAD_FILE" EXIT

        cat > "$PAYLOAD_FILE" << EOFPAYLOAD
{
  "groupId": "$SIGNAL_GROUP_ID",
  "message": $(echo "$MESSAGE" | jq -Rs .)
}
EOFPAYLOAD

        RESPONSE=$(curl -s -X POST "$EFFECTIVE_URL/api/signal/send" \
            -H "Authorization: Bearer $GATEWAY_TOKEN" \
            -H "Content-Type: application/json" \
            -d @"$PAYLOAD_FILE")

        if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
            echo "Message sent via Signal relay to group"
        else
            echo "Signal group relay response:"
            echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
        fi
        ;;

    dry-run)
        echo "=== DRY RUN ==="
        echo "Transport: would use gateway API"
        echo "Target: @$TARGET_AGENT"
        echo "Message length: ${#MESSAGE} chars"
        echo "---"
        echo "$MESSAGE"
        echo "---"
        echo ""
        echo "To send, run without --dry-run:"
        echo "  $0 \"...\" --gateway --to $TARGET_AGENT"
        ;;
esac
