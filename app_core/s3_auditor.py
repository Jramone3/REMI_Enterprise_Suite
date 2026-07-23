import json
import yaml
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger()

def parse_config_content(content_str):
    """
    Intenta parsear el texto plano como JSON o YAML.
    Devuelve un diccionario con los datos o None si hay error.
    """
    try:
        # Intentar JSON primero
        return json.loads(content_str)
    except json.JSONDecodeError:
        try:
            # Si falla JSON, intentar YAML
            return yaml.safe_load(content_str)
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear el contenido como JSON o YAML: {e}")
            return None

def audit_s3_config_text(content_str):
    """
    Analiza de forma estática el contenido de texto de una configuración 
    de S3, CloudFormation o Terraform en busca de brechas críticas.
    """
    data = parse_config_content(content_str)
    if not data:
        return {
            "status": "ERROR",
            "secure": False,
            "message": "El formato del texto no es un JSON o YAML válido."
        }

    issues = []
    content_text_lower = content_str.lower()

    # --- Chequeos de Acceso Público ---
    # 1. Bloqueo de ACLs Públicas
    if '"blockpublicacls": false' in content_text_lower or 'blockpublicacls: false' in content_text_lower:
        issues.append("El Bloqueo de ACLs Públicas (BlockPublicAcls) está desactivado.")
    
    # 2. Bloqueo de Políticas Públicas
    if '"blockpublicpolicy": false' in content_text_lower or 'blockpublicpolicy: false' in content_text_lower:
        issues.append("El Bloqueo de Políticas Públicas (BlockPublicPolicy) está desactivado.")
    
    # 3. Ignorar ACLs Públicas
    if '"ignorepublicacls": false' in content_text_lower or 'ignorepublicacls: false' in content_text_lower:
        issues.append("La opción de Ignorar ACLs Públicas (IgnorePublicAcls) está desactivada.")
    
    # 4. Restringir Buckets Públicos
    if '"restrictpublicbuckets": false' in content_text_lower or 'restrictpublicbuckets: false' in content_text_lower:
        issues.append("La opción de Restringir Buckets Públicos (RestrictPublicBuckets) está desactivada.")

    # 5. Políticas de Bucket con Principal "" (acceso anónimo/público amplio)
    if ('principal: ""' in content_text_lower or 'principal: { "aws": "" }' in content_text_lower) and \
       ('effect: allow' in content_text_lower) and \
       ('s3:getobject' in content_text_lower or 's3:putobject' in content_text_lower or 's3:listbucket' in content_text_lower):
        issues.append("Se detectó una política de bucket con 'Principal' abierto y 'Effect: Allow' para acciones S3, lo que podría indicar acceso público no deseado.")

    # 6. Permisos "PublicRead" o "PublicReadWrite" en ACLs o políticas
    if '"publicread"' in content_text_lower or '"publicreadwrite"' in content_text_lower:
        issues.append("Se detectó una política o ACL con permisos 'PublicRead' o 'PublicReadWrite'.")

    # --- Chequeo de Encriptación por Defecto ---
    encryption_keywords = [
        'serversideencryptionconfiguration', # CloudFormation
        'default_encryption',               # Terraform
        'ssealgorithm',                     # General
        'kmsmasterkeyid',                   # KMS
        'kmsencryptioncontext'              # KMS
    ]
    found_encryption_config = any(keyword in content_text_lower for keyword in encryption_keywords)
    if not found_encryption_config:
        issues.append("No se encontró configuración explícita de Encriptación por Defecto (SSE-S3 o SSE-KMS).")

    # Veredicto final
    if issues:
        return {
            "status": "Vulnerable",
            "secure": False,
            "findings": issues,
            "message": "Se encontraron brechas de configuración críticas."
        }
    else:
        return {
            "status": "Seguro",
            "secure": True,
            "findings": [],
            "message": "La configuración cumple con las reglas básicas de seguridad evaluadas."
        }

if __name__ == "__main__":
    sample_config_vulnerable = """
    Resources:
      MyS3Bucket:
        Type: AWS::S3::Bucket
        Properties:
          BucketName: my-super-public-bucket
          PublicAccessBlockConfiguration:
            BlockPublicAcls: false
            IgnorePublicAcls: false
            BlockPublicPolicy: false
            RestrictPublicBuckets: false
    """
    resultado = audit_s3_config_text(sample_config_vulnerable)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
