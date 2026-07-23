#!/bin/bash
LOG="/home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/bitacora_limpieza.txt"
# Sumamos todos los diferenciales detectados en la bitácora
TOTAL=$(grep "DIF:" $LOG | awk '{sum+=$NF} END {print sum}')
echo $TOTAL > /home/ramon/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/suma_acumulada.txt
echo "💰 BOTÍN ACUMULADO ACTUAL: $TOTAL USD"
