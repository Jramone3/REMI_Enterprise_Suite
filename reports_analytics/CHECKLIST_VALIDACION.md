Checklist de validación final — REMI Enterprise Suite

1) Entorno y variables
- [ ] .env o variables de entorno definidas: REMI_PAYMENT_ADDRESS, BASE_RPC_URL, MONGO_URI, REMI_DB_NAME, LLM_HOST
- [ ] No usar direcciones de pago hardcoded en producción

2) Servicios
- [ ] MongoDB accesible (puerto 27017 o MONGO_URI configurado)
- [ ] Servicio LLM disponible en LLM_HOST (http 11434 por defecto)

3) Construcción y arranque
- [ ] Dockerfile builda sin errores: docker build -t remi-enterprise .
- [ ] docker compose up --build termina con todos los contenedores "healthy" o sin errores críticos
- [ ] Streamlit responde en http://localhost:8501

4) Flujo de licenciamiento
- [ ] Emitir licencia desde la UI con un TxID de prueba (mock o real) y comprobar retorno exitoso
- [ ] Ver documento de licencia creado en Mongo: db.licenses.find().limit(5)
- [ ] Ver logs de la aplicación para confirmar que no hay excepciones no controladas

5) Validación on-chain
- [ ] Validador nativo: probar con transacción ETH de ejemplo (o mock) que tenga recipient = REMI_PAYMENT_ADDRESS y value >= mínimo
- [ ] Validador ERC-20: probar con receipt simulado que contenga un log Transfer hacia REMI_PAYMENT_ADDRESS con amount >= mínimo

6) Calidad
- [ ] pytest -q pasa sin fallos
- [ ] flake8 . --max-line-length=120 pasa sin errores críticos

7) CI/CD
- [ ] .github/workflows/ci.yml instala requirements-dev.txt y ejecuta pytest + flake8
- [ ] PR de cambios creado y revisado

8) Seguridad y operaciones
- [ ] No exponer claves o direcciones privadas en el repo
- [ ] Aplicar limitación de emisión (rate limit / protección) si el portal está público
- [ ] Revisar logs y configurar rotación/retención

9) Despliegue final
- [ ] Crear imagen tagged (ej: remi-enterprise:v1.0.0)
- [ ] Verificar despliegue en entorno staging con datos reales o con fixtures
- [ ] Realizar auditoría de seguridad para el manejo de claves y accesos

Notas:
- Para pruebas end-to-end reproducibles usa mongomock o un ambiente staging con una red RPC de pruebas.
- Guarda el backup de la colección `licenses` antes de migraciones mayores.
