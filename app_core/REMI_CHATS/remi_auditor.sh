#!/bin/bash
# Auditoría de Espacios Vitales de REMI
echo "--- INICIO DE AUDITORÍA: ESPACIOS VITALES ---"
echo "Estado de Almacenamiento (sda5/sda7):"
df -h | grep -E 'sda5|sda7'
echo "---"
echo "Conteo de archivos en Proyecto_Remi_IA_App:"
find /home/ramon/REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/ -type f | wc -l
echo "---"
echo "Estado de Memoria RAM:"
free -h | grep Mem
echo "--- FIN DE AUDITORÍA ---"
