#!/bin/bash
# Script para publicar documentación y sandbox de REMI-IA en repositorio Xano/Dev
# Incluye log de auditoría con fecha y hora

REPO_DIR=~/documentacion/xano
SANDBOX_DIR=/mnt/sda7/REMI/remi_sandbox_publico
LOG_FILE=$REPO_DIR/log_publicacion_remi.txt

# Inicializar repositorio si no existe
if [ ! -d "$REPO_DIR/.git" ]; then
  cd $REPO_DIR
  git init
fi

# Copiar sandbox al repositorio
if [ -d "$SANDBOX_DIR" ]; then
  cp -r $SANDBOX_DIR $REPO_DIR/
  echo "✅ Sandbox copiado desde $SANDBOX_DIR a $REPO_DIR"
else
  echo "⚠️ No se encontró la carpeta $SANDBOX_DIR"
fi

# Agregar archivos clave
cd $REPO_DIR
git add README_REMI_XANO.md remi_api_publico.md remi_frontend_demo.md remi_memoria_demo.md remi_sponsors_template.md remi_comunidad_dev.md remi_sandbox_publico/

# Commit con fecha/hora
COMMIT_MSG="Publicación REMI-IA Xano/Dev + Sandbox - $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Push al remoto (ajusta <URL_de_tu_repo>)
git push origin master

# Registrar log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Publicación realizada con commit: $COMMIT_MSG" >> $LOG_FILE

echo "✅ Publicación completada y registrada en $LOG_FILE"
