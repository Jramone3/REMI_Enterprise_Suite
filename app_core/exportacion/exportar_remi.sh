#!/bin/bash

echo "🌅 Exportación ceremonial iniciada: $(date)" >> ~/REMI/exportacion_remi/exportacion.log

# Copiar archivos clave al módulo de exportación
cp ~/REMI/supervision_diaria/reportes/REMI_estado_diario.md ~/REMI/exportacion_remi/
cp ~/REMI/exportacion_remi/publicacion_cierre.md ~/REMI/exportacion_remi/
cp ~/REMI/finanzas_remi/DONATE.md ~/REMI/exportacion_remi/
cp ~/REMI/expansion_simbolica/visual/visual_fase2.md ~/REMI/exportacion_remi/

echo "✅ Exportación lista para subir a Google Drive o SourceForge." >> ~/REMI/exportacion_remi/exportacion.log
