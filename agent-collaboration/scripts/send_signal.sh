#!/bin/bash
# Send a message to Signal via signal-cli JSON-RPC
# Usage: ./send_signal.sh "message" [--group GROUP_ID] [--dm PHONE_NUMBER]
#
# Direct signal-cli RPC bypasses Authentik authentication on the OpenClaw gateway.
# Group ID for Kublai Klub: BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=

set -e

# Configuration - override via environment
SIGNAL_RPC_URL="${SIGNAL_RPC_URL:-https://signal-cli-native-production.up.railway.app/api/v1/rpc}"
SIGNAL_ACCOUNT="${SIGNAL_ACCOUNT:-+15165643945}"
DEFAULT_RECIPIENT="${SIGNAL_RECIPIENT:-+19194133445}"
DEFAULT_GROUP_ID="${SIGNAL_GROUP_ID:-BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=}"

# Parse arguments
MESSAGE=""
TARGET_TYPE="dm"
TARGET="$DEFAULT_RECIPIENT"

while [[ $# -gt 0 ]]; do
    case $1 in
        --group)
            TARGET_TYPE="group"
            TARGET="$2"
            shift 2
            ;;
        --dm)
            TARGET_TYPE="dm"
            TARGET="$2"
            shift 2
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
    echo "Usage: $0 \"message\" [--dm PHONE_NUMBER] [--group GROUP_ID]"
    echo ""
    echo "Examples:"
    echo "  $0 \"Hello Kublai\"                       # Send DM to default recipient (+19194133445)"
    echo "  $0 \"Message\" --dm +1234567890           # Send DM to specific number"
    echo "  $0 \"Group message\" --group GROUP_ID    # Send to Signal group"
    echo ""
    echo "Environment variables:"
    echo "  SIGNAL_RPC_URL    - signal-cli JSON-RPC endpoint"
    echo "  SIGNAL_ACCOUNT    - Signal account phone number"
    echo "  SIGNAL_RECIPIENT  - Default DM recipient (default: +19194133445)"
    echo "  SIGNAL_GROUP_ID   - Group ID for --group mode"
    exit 1
fi

# Set default target if not specified
if [[ -z "$TARGET" ]]; then
    TARGET="$DEFAULT_GROUP_ID"
fi

# Create temp file for request payload
PAYLOAD_FILE=$(mktemp)
trap "rm -f $PAYLOAD_FILE" EXIT

# Build the JSON-RPC request
if [[ "$TARGET_TYPE" == "group" ]]; then
    cat > "$PAYLOAD_FILE" << EOFPAYLOAD
{
  "jsonrpc": "2.0",
  "method": "send",
  "params": {
    "account": "$SIGNAL_ACCOUNT",
    "groupId": "$TARGET",
    "message": $(echo "$MESSAGE" | jq -Rs .)
  },
  "id": 1
}
EOFPAYLOAD
else
    cat > "$PAYLOAD_FILE" << EOFPAYLOAD
{
  "jsonrpc": "2.0",
  "method": "send",
  "params": {
    "account": "$SIGNAL_ACCOUNT",
    "recipient": ["$TARGET"],
    "message": $(echo "$MESSAGE" | jq -Rs .)
  },
  "id": 1
}
EOFPAYLOAD
fi

# Send via signal-cli JSON-RPC
RESPONSE=$(curl -s -X POST "$SIGNAL_RPC_URL" \
    -H "Content-Type: application/json" \
    -d @"$PAYLOAD_FILE")

# Check response
if echo "$RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
    SUCCESS_COUNT=$(echo "$RESPONSE" | jq '[.result.results[] | select(.type == "SUCCESS")] | length')
    TOTAL_COUNT=$(echo "$RESPONSE" | jq '.result.results | length')
    echo "Message sent successfully ($SUCCESS_COUNT/$TOTAL_COUNT recipients)"

    # Show any failures
    FAILURES=$(echo "$RESPONSE" | jq -r '.result.results[] | select(.type != "SUCCESS") | "\(.recipientAddress.number // .recipientAddress.uuid): \(.type)"')
    if [[ -n "$FAILURES" ]]; then
        echo "Failures:"
        echo "$FAILURES"
    fi
else
    echo "Error sending message:"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    exit 1
fi
