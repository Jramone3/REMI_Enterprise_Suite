# 🤖 REMI_IA_Core: Sovereign Digital Persona & Multi-Pillar Perception Framework 🤖🇻🇪

**REMI (Resilient Entity & Modular Intelligence)** es un núcleo de Inteligencia Artificial Soberano y Persona Digital Autónoma diseñado por jramonrivasg. Combina razonamiento local de baja latencia (`qwen2.5:3b` / `remi:3b`), síntesis vocal contextual (Vega TTS), una matriz de percepción orbital y espacial en tiempo real, y un **Orquestador REPL Local de Comandos, Skills y Monetización**.

---

## 🏛️ Arquitectura del Sistema

- **Inference Core (`server.py`):** Servidor API principal construido en FastAPI (Puerto 5000) con orquestación Ollama, almacenamiento neuronal en `sda7` y fallback resiliente.
- **REPL Orchestrator (`core/remi_orchestrator.py`):** Consola interactiva y enrutador directo de comandos locales para gestión de habilidades (`/skill`), diagnóstico del nodo (`/status`), auditorías (`/audit`) y monetización (`/monetize`).
- **Security Auditor (`remi_c_auditor.py`):** Módulo de análisis estático de bajo nivel para auditoría de código fuente y contratos inteligentes.
- **Motor de Monetización B2B (`reports_analytics/`):** Autogestión económica local para generación de manifiestos comerciales (`AUDITOR_SERVICE_MANIFEST.json`), reportes para clientes y facturación (`REMI_ENTERPRISE_INVOICE.json`).
- **Perception Matrix (`modules/orbital_gateway/`):**
  1. `telemetry_engine.py`: Seguimiento orbital en vivo y radiación solar para la Estación Espacial Internacional (ISS).
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

2. Iniciar Consola REPL (Enrutador de Comandos & Skills)
Bash
python3 core/remi_orchestrator.py
3. Diagnóstico de Percepción Multi-Capa (5 Pilares)
Bash
python3 modules/orbital_gateway/verify_orbital.py
Arquitecto & Custodio: Jramonrivasg (Jramone3)

Nodo Soberano: ramon-desktop | Aragua, Venezuela
