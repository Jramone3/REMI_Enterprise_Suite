#!/bin/bash
# Script para insertar contenido base en la documentación de REMI-IA (Xano/Dev)

# Archivo: remi_api_publico.md
cat > ~/documentacion/xano/remi_api_publico.md << 'EOF'
# REMI-IA Public API (Xano)

## Endpoint
POST /api/v1/remi/consulta

## Parámetros
- `prompt` (string): texto de entrada
- `lang` (string): idioma preferido (es/en)

## Ejemplo de uso
curl -X POST https://xano.dev/remi/api/v1/consulta \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hola REMI","lang":"es"}'

## Respuesta
{
  "remi_output": "Hola, soy REMI-IA, tu agente bilingüe."
}

## Notas
- El API está documentado y auditable.
- Se integra con Copilot como gateway multi-modelo.
EOF

# Archivo: README_REMI_XANO.md
cat > ~/documentacion/xano/README_REMI_XANO.md << 'EOF'
# REMI-IA en el Xano AI-Powered Backend Challenge

## Componentes
- [API Público](remi_api_publico.md)
- [Frontend Demo](remi_frontend_demo.md)
- [Memoria Persistente](remi_memoria_demo.md)
- [Sponsors Template](remi_sponsors_template.md)
- [Comunidad DEV](remi_comunidad_dev.md)

## Narrativa
REMI-IA es un agente multi-modelo con trazabilidad bilingüe y memoria auditable.
Integra Copilot como gateway y conecta Gemini, Grok, Claude y Ollama.
Su circuito financiero validado (Binance → Zinli → Visa) garantiza sostenibilidad.

## Objetivo
Demostrar que REMI-IA no solo es un backend inteligente,
sino un estándar abierto para onboarding y comunidad global.
EOF

# Archivo: remi_comunidad_dev.md
cat > ~/documentacion/xano/remi_comunidad_dev.md << 'EOF'
# REMI-IA para la comunidad DEV

## Español
REMI-IA ofrece un backend multi-modelo con trazabilidad bilingüe.
Cada demo está documentada y auditable para reproducibilidad.
La comunidad puede integrarlo, probarlo y extenderlo con confianza.

## English
REMI-IA provides a multi-model backend with bilingual traceability.
Every demo is documented and auditable for reproducibility.
The community can integrate, test, and extend it with confidence.
EOF

echo "✅ Contenido insertado en remi_api_publico.md, README_REMI_XANO.md y remi_comunidad_dev.md"
