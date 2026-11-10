#!/usr/bin/env bash

# ==============================================================================
# REMI INTER-PROCESS BRIDGE DISPATCHER
# ==============================================================================

TARGET_CMD="$1"

if [ -z "$TARGET_CMD" ]; then
    echo "❌ [BRIDGE_ERROR]: Null command payload provided to bridge pipeline."
    exit 1
fi

echo "🌉 [BRIDGE_DISPATCH]: Executing command sequence: $TARGET_CMD"
/bin/bash -c "$TARGET_CMD"
