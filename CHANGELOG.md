# Changelog

Todos los cambios relevantes de REMI Enterprise Suite se documentan aquí.

## [v2.1.0] - 2026-10-05
### Added
- Certificación oficial del sistema con nivel 100/100.
- Blindaje asíncrono para la integración con PyGithub usando `run_in_threadpool` para evitar bloqueos del event loop en FastAPI.
- Resiliencia de red con timeout de 15 segundos y mecanismo de fallback compatible con distintas versiones de PyGithub.
- Auditoría persistente en MongoDB mediante la colección `audit_logs` y la capa centralizada `db.py`.
- Validación y hardening de endpoints con esquemas Pydantic estrictos y cabecera obligatoria `X-API-Key`.
- Logging estructurado y observabilidad orientada a entorno empresarial.

### Changed
- Ajustes de seguridad y robustez para despliegue en producción.
- Mejora de la interoperabilidad y compatibilidad operativa entre módulos internos.
- Batería de pruebas unitarias reforzada y validada en verde.

### Security
- Fortalecimiento del modelo de seguridad del backend y del control de acceso a rutas críticas.

---

## [v1.0.1] - 2026-08-31
### Changed
- Eliminación completa de datos personales y fiscales sensibles en la interfaz pública.
- Actualización del módulo fiscal con una estructura corporativa neutra bajo el nombre `REMI Enterprise Core`.
- Integración de `qrcode` y `pillow` para garantizar la correcta compilación de códigos QR en entornos cloud (Render / Vercel).

### Fixed
- Correcciones operativas necesarias para despliegues de producción y validación en entornos de nube.

---

## [v1.0.0] - 2026-07-24
### Added
- Verificación criptográfica real de firmas en el webhook de Stripe mediante `stripe.Webhook.construct_event`.
- Protección del endpoint de pagos frente a payloads falsificados.
- Búnker MongoDB reforzado con índices únicos y control de duplicados mediante `DuplicateKeyError` / `E11000`.
- Consolidación de dependencias de producción en `requirements.txt`.
- Suite de pruebas automatizadas validada en la release inicial (`15/15` tests pasando).

### Changed
- Reorganización del stack mínimo necesario para despliegue en producción.
- Preparación de la infraestructura para entornos reales de operación.

### Deployment
- Configuración de secretos obligatorios de producción en GitHub Actions o entorno de despliegue.
- Ejecución de la suite de pruebas con `pytest -v` antes de despliegue.

---

## Notas
- Esta release log refleja el historial oficial publicado en GitHub para el repositorio `Jramone3/REMI_Enterprise_Suite`.
- Los enlaces más importantes de cada versión se mantienen en la sección de Releases del repositorio.
- Documentos complementarios: `CERTIFICATION.md`, `DEPLOYMENT_CHECKLIST.md`.
