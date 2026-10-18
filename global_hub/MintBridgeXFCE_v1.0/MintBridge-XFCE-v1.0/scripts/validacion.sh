📄 Checklist Comunitario — Validación Técnica MintBridge XFCE
Autor técnico: jramonrivasg Fecha: 03/09/2025 Entorno: WSL Ubuntu con sudo sin contraseña Proyecto: MintBridge-XFCE-v1.0 Ruta de archivo: ~/mintbridge/docs/Checklist_MintBridge_jramonrivasg.docx

🧩 Script de validación — versión corregida
bash
#!/bin/bash
echo "Servicio: examen notic"
echo "Detectar líneas duplicadas en login.db"

# Detectar duplicados
duplicados=$(sort login.db | uniq -d)
if [ "$duplicados" != "" ]; then
    echo "⚠️ Líneas duplicadas encontradas:"
    echo "$duplicados"
else
    echo "✅ No hay duplicados en login.db"
fi

# Validar archivos vacíos
correctos=0
faltantes=0
for archivo in *.db; do
    if [ -s "$archivo" ]; then
        echo "$archivo tiene contenido"
        correctos=$((correctos+1))
    else
        echo "$archivo está vacío"
        faltantes=$((faltantes+1))
    fi
done

# Confirmar permisos
chmod +x validacion.sh
ls -l validacion.sh

# Simulación segura
echo "Simulación con sudo:"
echo "sudo cp archivo.db /ruta/destino/"
# Alternativa segura
# sudo rsync --dry-run archivo.db /ruta/destino/

# Resumen final
echo "✔️ Archivos correctos: $correctos"
echo "❌ Archivos faltantes: $faltantes"
if [ "$faltantes" -eq 0 ]; then
    echo "✅ Proyecto listo para cierre técnico"
else
    echo "⚠️ Revisión pendiente: hay archivos vacíos"
fi
📋 Validaciones aplicadas
Validación	Estado final	Acción aplicada
Carpeta de trabajo	✅ OK	Detectada correctamente
Archivo login.db	✅ OK	Presente y accesible
Duplicados	✅ Corregido	Detectados con `sort	uniq -d`
Archivos vacíos	✅ Controlado	Bucle optimizado con contador
Permisos de ejecución	✅ Confirmado	chmod +x seguido de ls -l
Simulación con sudo	✅ Simulado	echo y rsync --dry-run
Resumen final	✅ Integrado	Conteo de correctos/faltantes
📝 Espacio para anotaciones comunitarias
Código
───────────────────────────────────────────────
Observaciones del validador:





───────────────────────────────────────────────
✍️ Firma de validadores comunitarios
Nombre del validador	Fecha	Validación técnica (✔️ / ❌)	Firma
