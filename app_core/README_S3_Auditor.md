# 🛡️ REMI S3 Auditor - Micro-Servicio de Análisis Estático

Herramienta ligera para detectar brechas críticas de seguridad en configuraciones de Amazon S3 (compatible con JSON, YAML, CloudFormation y Terraform).

## 📋 Requisitos Previos
* Python 3.8 o superior
* Librería **PyYAML** (verificada en el entorno)

## 🚀 Uso Rápido
Importa la función principal en tu script o API:

```python
from s3_auditor import audit_s3_config_text

# Pasa el contenido de tu archivo de configuración como texto plano
resultado = audit_s3_config_text(contenido_en_texto)
print(resultado)
