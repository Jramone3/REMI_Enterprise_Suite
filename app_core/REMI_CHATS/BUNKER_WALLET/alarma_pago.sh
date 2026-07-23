#!/bin/bash
# Este script verifica el saldo y avisa si hay cambios
SALDO=$(python3 /home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/verificar_saldo.py | grep "SALDO ACTUAL" | awk '{print $3}')

if (( $(echo "$SALDO > 0" | bc -l) )); then
    echo "🚨 [ALERTA BÚNKER]: ¡RECURSOS DETECTADOS! Saldo: $SALDO ETH"
    echo "💰 ¡PAGO CONFIRMADO!" > /home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/aviso_urgente.txt
else
    echo "📡 Vigilando... La bóveda sigue vacía. (Saldo: $SALDO)"
fi
