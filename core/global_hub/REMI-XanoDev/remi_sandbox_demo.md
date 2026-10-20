# REMI-IA Sandbox Público

## Objetivo
Permitir pruebas rápidas del API y memoria.

## Ejemplo de uso
curl -X POST https://xano.dev/remi/api/v1/consulta \
  -H "Content-Type: application/json" \
  -d '{"prompt":"¿Cuál es mi proyecto?","lang":"es"}'

## Respuesta esperada
{
  "remi_output": "Tu proyecto se llama Desafío REMI-IA."
}
