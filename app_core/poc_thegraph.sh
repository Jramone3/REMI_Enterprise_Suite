#!/bin/bash
# PoC de Auditoría - The Graph Protocol [REMI-TG-2026]
# Objetivo: Verificación de Deadlock administrativo en 0x296E...

CONTRACT="0x296Ebf81430eA5561143B4b15B17CC3C549e2a53"
RPC="https://arb1.arbitrum.io/rpc"

echo "=== INICIANDO AUDITORÍA FORENSE ==="
echo "Consultando variable controller()..."
RESULT=$(cast call $CONTRACT "controller()(address)" --rpc-url $RPC)

if [ "$RESULT" == "0x0000000000000000000000000000000000000000" ]; then
    echo "ESTADO: VULNERABLE (Controller nulo detectado)"
    exit 1
else
    echo "ESTADO: SEGURO (Controller configurado: $RESULT)"
    exit 0
fi
