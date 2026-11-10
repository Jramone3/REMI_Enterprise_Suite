# REMI Enterprise Suite: Spot / Demo de 60 segundos

Formato: 16:9, 1920×1080, 30 fps. Versión vertical 9:16 opcional para Reels/Shorts, reencuadrando la UI.
Tono: técnico, sobrio, confiado. Música: electrónica minimalista, ~100 BPM, sin voz.
Regla de producción: **todo lo que se muestre en pantalla debe ser grabación real de la app** (Streamlit en Render, consola de MongoDB Atlas, terminal). Las ilustraciones generadas por IA se usan solo para título, transiciones y miniaturas.

Antes de grabar:
- Despierta la demo en Render 2 minutos antes.
- Prepara datos de ejemplo ficticios (nada de clientes ni correos reales).
- Oculta URIs, API keys y la dirección de pago en las capturas. Usa un perfil de navegador limpio.
- Confirma qué LLM usa realmente la demo (el README habla de Ollama/llama3; tu brief, de Gemini 2.5 Flash) y ajusta la escena 4.

---

## Storyboard (60 s)

| # | Tiempo | Pantalla | Locución ES | Voice-over EN |
|---|---|---|---|---|
| 1 | 0:00–0:06 | **Gancho.** Fondo oscuro. Texto animado: "Tu agente de IA funciona. ¿Y ahora qué?" Tres iconos que aparecen: 🔑 acceso, 💳 pago, 🧾 auditoría. (Ilustración IA + tipografía animada) | "Tu agente de IA ya funciona. Pero, ¿quién puede usarlo, cómo paga y cómo lo audita?" | "Your AI agent works. But who can run it, how do they pay, and how do you audit it?" |
| 2 | 0:06–0:12 | **Logo REMI** sobre fondo de red de nodos. Subtítulo: "Multi-agent AI. Licensing. Audit. One stack." | "Presentamos REMI Enterprise Suite: IA multiagente, licencias y auditoría en un solo stack." | "Meet REMI Enterprise Suite: multi-agent AI, licensing and audit in one stack." |
| 3 | 0:12–0:22 | **UI de Streamlit** (grabación). Cursor abre el centro de comando. Panel lateral con módulos, vista general operativa. Zoom suave al panel principal. | "Un centro de comando para operar tus agentes desde una sola interfaz." | "One command center to operate your agents from a single interface." |
| 4 | 0:22–0:32 | **Flujo LLM** (grabación). Se escribe una tarea en el chat. Aparece la respuesta del agente en streaming. Superposición discreta: `Prompt → Agente → Respuesta`. Etiqueta con el modelo realmente usado. | "Dale una tarea en lenguaje natural y los agentes la ejecutan, con el modelo que tú elijas." | "Give it a task in plain language and the agents execute it, with the model you choose." |
| 5 | 0:32–0:42 | **Búnker MongoDB Atlas** (grabación). Consola de Atlas, base `remi_enterprise`, colección de licencias y de auditoría con documentos de ejemplo. Resalta un registro nuevo con *highlight*. | "Cada licencia y cada evento queda registrado en MongoDB. Trazabilidad total." | "Every license and every event is recorded in MongoDB. Full traceability." |
| 6 | 0:42–0:52 | **Pagos.** Pantalla dividida: izquierda, checkout de Stripe en modo test; derecha, una transacción en un explorador de Base (testnet o hash de ejemplo). Ambas terminan en: "✔ Licencia emitida". | "Cobra con tarjeta o con cripto en la red Base. La licencia se emite automáticamente." | "Get paid by card or on Base. The license is issued automatically." |
| 7 | 0:52–0:60 | **Cierre.** Terminal: `docker compose up` y luego la URL. Pantalla final con logo, URL de la demo, icono de GitHub y "Open source · MIT". | "Despliégalo con Docker en tu infraestructura. Pruébalo hoy en remi-enterprise-suite punto onrender punto com." | "Deploy it with Docker on your own infrastructure. Try it today at remi-enterprise-suite.onrender.com." |

Conteo de palabras de locución: ES ≈ 105 palabras, EN ≈ 90. Es ajustado para 60 s a ritmo natural; si al grabar sobra, recorta la escena 2.

### Guión limpio para grabar (solo locución)

**Español**
> Tu agente de IA ya funciona. Pero, ¿quién puede usarlo, cómo paga y cómo lo audita?
> Presentamos REMI Enterprise Suite: IA multiagente, licencias y auditoría en un solo stack.
> Un centro de comando para operar tus agentes desde una sola interfaz.
> Dale una tarea en lenguaje natural y los agentes la ejecutan, con el modelo que tú elijas.
> Cada licencia y cada evento queda registrado en MongoDB. Trazabilidad total.
> Cobra con tarjeta o con cripto en la red Base. La licencia se emite automáticamente.
> Despliégalo con Docker en tu infraestructura. Pruébalo hoy en remi-enterprise-suite punto onrender punto com.

**English**
> Your AI agent works. But who can run it, how do they pay, and how do you audit it?
> Meet REMI Enterprise Suite: multi-agent AI, licensing and audit in one stack.
> One command center to operate your agents from a single interface.
> Give it a task in plain language and the agents execute it, with the model you choose.
> Every license and every event is recorded in MongoDB. Full traceability.
> Get paid by card or on Base. The license is issued automatically.
> Deploy it with Docker on your own infrastructure. Try it today at remi-enterprise-suite.onrender.com.

---

## Producción sin trabajo manual de edición

- **Voz:** puedes generarla con cualquier servicio de texto a voz. El repo ya incluye `generar_audios.py`; revisa si sirve para esto.
- **Grabación de pantalla:** OBS Studio (gratis). Resolución 1920×1080, cursor visible, zoom en post.
- **Montaje:** CapCut, DaVinci Resolve (gratis) o Remotion si quieres automatizarlo por código.
- **Subtítulos:** sube ES y EN como pistas aparte; los espectadores ven muchos vídeos sin sonido.

---

## Prompts de imagen

Consejos generales: no pidas texto largo en la imagen (los generadores lo deletrean mal). Añade el texto después en Canva/Figma. No uses logos de terceros (Streamlit, MongoDB, Stripe, Base) en el generador; añádelos tú desde sus kits de marca oficiales si los necesitas.

### A. Miniatura principal 16:9 (YouTube / Product Hunt / HN)

**Midjourney**
```
Futuristic enterprise control room seen from slightly above, a glowing network of
interconnected AI agent nodes in teal and electric violet floating over a dark
navy dashboard, thin data lines flowing into a vault-like glass cube, clean
negative space on the left third for headline text, cinematic lighting, shallow
depth of field, ultra detailed, product marketing key art --ar 16:9 --style raw --v 7
```

**DALL-E**
```
A wide 16:9 key visual for a B2B software launch: a network of glowing teal and
violet nodes (representing AI agents) connected to a translucent glass vault on a
dark navy background. Minimal, modern, premium look. Leave the left third empty
for a headline. No text, no logos, no people.
```

**Flux**
```
Wide cinematic key art, abstract multi-agent AI network, teal and violet glowing
nodes linked by fine light lines, central glass vault cube holding data streams,
dark navy background, soft volumetric light, large empty area on the left for
text overlay, sharp focus, 16:9, no text, no logos
```

### B. Imagen "Licencia + pagos" (escena 6 / post de LinkedIn)

**Midjourney**
```
Isometric illustration of a glowing digital license card passing through two
gateways, one shaped like a payment card terminal and one like a blockchain block,
emerging verified with a green check glow, dark navy background, teal and violet
palette, clean vector-like 3D, soft shadows --ar 1:1 --v 7
```

**DALL-E**
```
Isometric 3D illustration: a digital license card travels through two gateways
(a payment terminal and a blockchain block) and comes out with a green checkmark
glow. Dark navy background, teal and violet accents, clean modern style. No text.
```

**Flux**
```
Isometric 3D scene, glowing license card moving through a card payment terminal
gateway and a blockchain block gateway, verified checkmark glow at the exit,
dark navy background, teal and violet palette, crisp edges, no text
```

### C. Miniatura vertical 9:16 (Reels / Shorts)

**Midjourney**
```
Vertical composition, a lone glowing AI agent node at the top connected by light
threads to three smaller nodes below (access, payment, audit), dark gradient
background from navy to violet, bold simple shapes readable on a phone screen,
space at the top for a hook headline --ar 9:16 --style raw --v 7
```

**DALL-E**
```
Vertical 9:16 poster: one glowing AI agent node at the top connected by light
threads to three smaller nodes below, dark navy-to-violet gradient background,
simple bold shapes, empty space at the top for a headline. No text, no logos.
```

**Flux**
```
Vertical 9:16, glowing central AI node linked by light threads to three smaller
nodes, dark navy to violet gradient, bold flat-glow shapes legible on mobile,
empty headroom for text, no text, no logos
```

### D. Imagen de cabecera para artículos de blog (1200×630)

**Midjourney**
```
Abstract blueprint-style illustration of a software architecture: stacked layers
of interface, API, database and blockchain, thin glowing connections, deep navy
background with teal line work, editorial tech-blog header, calm and precise
--ar 1.91:1 --v 7
```

**DALL-E**
```
Editorial header image for a technical blog: a stylized layered architecture
(interface, API, database, blockchain) drawn with thin glowing teal lines on
a deep navy background. Calm, precise, uncluttered. No text.
```

**Flux**
```
Blueprint style layered software architecture illustration, four stacked
translucent layers connected by thin glowing teal lines, deep navy background,
editorial tech blog header, wide 1.91:1, no text
```

### Texto para superponer en las miniaturas (hazlo en Canva/Figma)

- `AI agents that you can actually sell`
- `Multi-agent AI + licensing + audit`
- `Self-hosted. Open source.`
- ES: `Agentes de IA listos para vender`
