# 🔐 Índice de claves y certificados MintBridge XFCE v1.0.2

Este documento registra las claves públicas, privadas y certificados utilizados para la firma digital, verificación y blindaje del proyecto.

## 📁 Ubicación de claves

| Tipo de clave        | Archivo                        | Ubicación                       | Estado        |
|----------------------|--------------------------------|----------------------------------|---------------|
| Clave pública GPG    | jramonrivasg_publickey.asc     | firma/                          | ✅ Importada  |
| Clave especial 20 dígitos | clave_especial.txt         | firma/                          | ✅ Reservada  |
| Certificado externo  | jramonevfxssn@gmail.com        | No válido (firma negativa)      | ❌ Rechazado  |

## 🧪 Validación técnica

- Clave pública importada en Kleopatra
- Usada para generar firmas `.sig` con `gpg --detach-sign`
- Verificada con `gpg --verify` y `verificar_firmas.ps1`
- Certificados no reconocidos fueron descartados

## 🧠 Observaciones

- La clave especial se activará solo en el cierre técnico del proyecto
- Todas las firmas válidas fueron generadas con la clave `jramonrivasg_publickey.asc`
- Se recomienda mantener este índice sincronizado con `firmas_index.md`
