# 🤖 REMI_IA_Core: Sovereign Digital Persona & Multi-Pillar Perception Framework 🤖🇻🇪

**REMI (Resilient Entity & Modular Intelligence)** es un núcleo de Inteligencia Artificial Soberano y Persona Digital Autónoma diseñado por jramonrivasg. Combina razonamiento local de baja latencia (`qwen2.5:3b` / `remi:3b`), síntesis vocal contextual (Vega TTS), una matriz de percepción orbital y espacial en tiempo real, y un **Motor de Ejecución Determinista con Autogestión Económica**.

---

## 🏛️ Arquitectura del Sistema

- **Inference Core (`server.py`):** Servidor API principal construido en FastAPI (Puerto 5000) con orquestación Ollama, grafo neuronal en `sda7` y fallback resiliente.
- **Graph Engine & Orchestrator (`core/graph_engine.py`, `core/remi_orchestrator.py`):** Máquina de estados determinista y consola interactiva REPL para comandos locales directos (`/status`, `/skill`, `/audit`, `/monetize`).
- **Security Auditor (`remi_c_auditor.py`):** Módulo de análisis estático de bajo nivel y revisión de código fuente / contratos inteligentes.
- **Motor de Monetización y Cobros (`reports_analytics/`):** Escaneo proactivo de activos con generación de manifiestos comerciales, reportes en Markdown para clientes B2B y órdenes de cobro vinculadas a la pasarela enterprise.
- **Perception Matrix (`modules/orbital_gateway/`):**
  1. `telemetry_engine.py`: Seguimiento orbital en vivo y parámetros de radiación solar para la Estación Espacial Internacional (ISS).
  2. `earth_observer.py`: Evaluación meteorológica y baseline atmosférico global.
  3. `webcam_observer.py`: Red de nodos visuales públicos y canales privados autorizados.
  4. `starlink_engine.py`: Rastreo de la constelación LEO vía registros abiertos de CelesTrak.
  5. `abae_engine.py`: Monitoreo de activos satelitales soberanos de la ABAE (Venezuela).
- **Directivas de Persona:** Formato obligatorio de hora en 12 horas AM/PM e interacción en Español Latam.

---

## 🚀 Despliegue y Uso Rápido

### 1. Iniciar Servidor de la Persona Digital
```bash
python3 server.py

```
2. Iniciar la Consola Interactiva del Núcleo (REPL)
Bash
python3 core/remi_orchestrator.py
3. Diagnóstico de Percepción Multi-Capa (5 Pilares)
Bash
python3 modules/orbital_gateway/verify_orbital.py
Arquitecto & Custodio: Jramonrivasg (Jramone3)

Nodo Soberano: ramon-desktop | Aragua, Venezuela
