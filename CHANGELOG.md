# Changelog

## [v1.0.0] - 2026-10-06
### Added
- Verificación criptográfica de firmas de Stripe (`stripe.Webhook.construct_event`) en `/api/webhook/stripe`.
- Manejo seguro de excepciones en la creación de índices únicos dentro del búnker MongoDB (`db.py`).
- Ficheros de documentación de liberación (`RELEASE_NOTES.md`).

### Changed
- `requirements.txt` unificado y actualizado con dependencias de producción y soporte de pasarela de pagos.
- Estructura del microservicio de licenciamiento optimizada para producción (`license_service.py`).

### Tested
- Suite completa de pruebas automatizadas validada (`15/15` tests pasando exitosamente).
