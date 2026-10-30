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
