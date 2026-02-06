#!/bin/bash
# Receive messages from Signal via Railway logs
# Usage: ./receive_signal.sh [--since TIME] [--follow] [--raw]
#
# Polls signal-cli-native Railway logs for incoming message content.
# Requires: Railway CLI installed and linked to the project.

set -e

# Configuration
SERVICE="${SIGNAL_CLI_SERVICE:-signal-cli-native}"
DEFAULT_SINCE="5m"

# Parse arguments
SINCE="$DEFAULT_SINCE"
FOLLOW=false
RAW=false

while [[ $# -gt 0 ]]; do
    case $1 in
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
            echo "Usage: $0 [--since TIME] [--follow] [--raw]"
            echo ""
            echo "Options:"
            echo "  --since TIME   Look back TIME (default: 5m). Examples: 30s, 10m, 1h, 1d"
            echo "  --follow, -f   Stream logs continuously (like tail -f)"
            echo "  --raw          Show raw log output without filtering"
            echo ""
            echo "Examples:"
            echo "  $0                    # Check last 5 minutes"
            echo "  $0 --since 1h         # Check last hour"
            echo "  $0 --follow           # Stream live"
            echo "  $0 --raw --since 10m  # Raw logs from last 10 minutes"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI not installed"
    echo "Install with: brew install railway"
    exit 1
fi

# Check project link
if ! railway status &> /dev/null; then
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
        # Capture envelope headers: Envelope from: "Name" +1234567890
        if echo "$line" | grep -qE '^Envelope from: "'; then
            SENDER_NAME=$(echo "$line" | sed -n 's/^Envelope from: "\([^"]*\)".*/\1/p')
            SENDER_NUMBER=$(echo "$line" | sed -n 's/.*"\s*\(+[0-9]*\).*/\1/p')
        fi

        # Capture timestamp
        if echo "$line" | grep -qE '^Timestamp:'; then
            TIMESTAMP=$(echo "$line" | sed -n 's/.*(\([^)]*\)).*/\1/p')
        fi

        # Capture message body
        if echo "$line" | grep -qE '^Body:'; then
            BODY=$(echo "$line" | sed 's/^Body: //')
            echo "[$TIMESTAMP] $SENDER_NAME ($SENDER_NUMBER):"
            echo "$BODY"
            echo "---"
            FOUND_MESSAGES=$((FOUND_MESSAGES + 1))
        fi

        # Also capture "Message body:" format
        if echo "$line" | grep -qE '^Message body:'; then
            BODY=$(echo "$line" | sed 's/^Message body: //')
            echo "[$TIMESTAMP] $SENDER_NAME ($SENDER_NUMBER):"
            echo "$BODY"
            echo "---"
            FOUND_MESSAGES=$((FOUND_MESSAGES + 1))
        fi
    done

    echo "$FOUND_MESSAGES"
}

if [[ "$FOLLOW" == "true" ]]; then
    echo "Streaming Signal messages (Ctrl+C to stop)..."
    echo "---"

    if [[ "$RAW" == "true" ]]; then
        railway logs --service "$SERVICE"
    else
        railway logs --service "$SERVICE" 2>&1 | parse_logs
    fi
else
    if [[ "$RAW" == "true" ]]; then
        railway logs --service "$SERVICE" --since "$SINCE" --lines 200
    else
        echo "Checking messages from last $SINCE..."
        echo "---"

        # Get logs and parse
        RESULT=$(railway logs --service "$SERVICE" --since "$SINCE" --lines 500 2>&1 | parse_logs)

        # The last line of RESULT is the count
        FOUND_MESSAGES=$(echo "$RESULT" | tail -1)
        # All lines except the last (macOS compatible)
        TOTAL_LINES=$(echo "$RESULT" | wc -l | tr -d ' ')
        if [[ "$TOTAL_LINES" -gt 1 ]]; then
            MESSAGES=$(echo "$RESULT" | head -n $((TOTAL_LINES - 1)))
            echo "$MESSAGES"
        fi

        if [[ "$FOUND_MESSAGES" == "0" || -z "$FOUND_MESSAGES" || ! "$FOUND_MESSAGES" =~ ^[0-9]+$ ]]; then
            echo "No message content found in the last $SINCE"
            echo "(Only receipts and delivery confirmations)"
            echo ""
            echo "Tip: Use --raw to see all log entries"
        else
            echo "Found $FOUND_MESSAGES message(s)"
        fi
    fi
fi
