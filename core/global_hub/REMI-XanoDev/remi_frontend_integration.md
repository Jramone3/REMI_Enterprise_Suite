# REMI-IA Frontend Integration

## Objetivo
Conectar formulario simple en WeWeb/Lovable al endpoint:
POST /api/v1/remi/consulta

## Campos
- Prompt (texto)
- Idioma (selector)
- Botón "Enviar"
- Área de respuesta

## Ejemplo de conexión
fetch("https://xano.dev/remi/api/v1/consulta", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: "Hola REMI", lang: "es" })
}).then(r => r.json()).then(data => console.log(data.remi_output));
