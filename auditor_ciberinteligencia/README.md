# Remi_core Auditor de Ciberinteligencia y CVEs

## Descripción General
Subsistema autónomo e independiente acoplado a la infraestructura de `REMI_CORE`, diseñado para la búsqueda, monitoreo pasivo, correlación de CVEs críticos y análisis predictivo de parches de seguridad en sistemas Linux. Se comunica directamente con la **REMI Enterprise Suite**.

## Arquitectura de Directorios
- `engine/`: Contiene los scripts de monitoreo de CVEs, verificación de paquetes locales y generadores de reportes.
- `config/`: Archivos de configuración de entorno (`settings.env`) y perfiles de seguridad (`security_profiles.json`).
- `feeds/`: Caché local de vulnerabilidades consultadas.
- `reports/`: Historial de auditorías y métricas de *hardening* generadas.

## Custodio y Autoría
- **Operador:** Ramón (Jramone3)
- **Núcleo de Inteligencia:** REMI Enterprise Suite
