# 📜 Índice técnico de firmas MintBridge XFCE v1.0.2

Este documento registra la relación entre scripts `.ps1` y sus firmas digitales `.sig`, verificadas con GPG y Kleopatra.

| Script                  | Firma                   | Validación       | Última revisión |
|------------------------|-------------------------|------------------|------------------|
| Blindaje.ps1           | Blindaje.ps1.sig        | gpg --verify     | ✅ 04/09/2025     |
| Migracion.ps1          | Migracion.ps1.sig       | gpg --verify     | ✅ 04/09/2025     |
| Verificacion.ps1       | Verificacion.ps1.sig    | gpg --verify     | ✅ 04/09/2025     |
| ControlEstructura.ps1  | ControlEstructura.ps1.sig | gpg --verify   | ✅ 04/09/2025     |
| setup.ps1              | setup.ps1.sig           | gpg --verify     | ✅ 04/09/2025     |

## 🔐 Clave pública utilizada
- Archivo: `jramonrivasg_publickey.asc`
- Ubicación: `firma/`
- Importada y validada en Kleopatra

## 🧪 Comando de verificación
```bash
gpg --verify archivo.sig archivo.ps1
MintBridge-XFEC-v1.0\signatures\
