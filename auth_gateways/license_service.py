# license_service.py - Microservicio de Licenciamiento FastAPI (Producción)
import os
import logging
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv

# Cargar explícitamente el archivo .env local
load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from db import init_db, save_license, find_license_by_email, save_audit_log
from remi_tx_validator import validate_transaction

# Configuración de logging estructurado
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("remi_license_service")

app = FastAPI(
    title="REMI License Microservice",
    version="2.2.0",
    description="Microservicio blindado de emisión, verificación de licencias, pagos fiduciarios (Stripe) y automatización para REMI Enterprise Suite"
)

# Evento de inicio: inicializa la base de datos y crea índices únicos
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Búnker DB inicializado y restricciones de índices únicos aplicadas.")

# Esquemas de datos
class LicenseRequest(BaseModel):
    email: str
    tx_hash: str
    tier: str = "standard"  # standard o enterprise

class IssueRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    body: str = Field(default="Generado automáticamente por REMI Core OS", max_length=2000)

# Dependencia de seguridad: Validación estricta de API Key del Administrador
def verify_api_key(x_api_key: str = Header(..., description="API Key de Administrador de REMI")):
    expected_key = os.getenv("REMI_API_KEY")
    if not expected_key:
        logger.critical("Error crítico: REMI_API_KEY no está configurada en el servidor.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error crítico de seguridad: REMI_API_KEY no está configurada en el servidor."
        )
    if x_api_key != expected_key:
        logger.warning("Intento de acceso denegado con API Key inválida o ausente.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key de Administrador inválida o ausente."
        )
    return x_api_key

@app.get("/")
def health_check():
    return {"status": "online", "service": "REMI License Microservice"}

# Endpoint público: Verifica licencia por correo
@app.get("/licenses/verify/{email}")
def verify_license(email: str):
    record = find_license_by_email(email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna licencia activa para este correo."
        )
    
    public_response = {
        "email": record.get("email"),
        "license": record.get("license"),
        "tier": record.get("tier", "standard"),
        "status": record.get("status", "ACTIVE"),
        "expires": record.get("expires")
    }
    return public_response

# Endpoint protegido: Emisión de licencia con validación on-chain y Bypass Local
@app.post("/licenses/issue")
def issue_license(payload: LicenseRequest, api_key: str = Depends(verify_api_key)):
    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo email es obligatorio."
        )
    
    # -------------------------------------------------------------------------
    # BYPASS LOCAL PRIVADO (Solo funciona si tu archivo .env tiene esta variable)
    # Como el archivo .env está en tu .gitignore, GitHub NUNCA verá este bloque
    # -------------------------------------------------------------------------
    local_master_bypass = os.getenv("REMI_INTERNAL_BYPASS_HASH")
    if local_master_bypass and payload.tx_hash == local_master_bypass:
        logger.info(f"[BYPASS INTERNO LOCAL]: Emitiendo licencia de auditoría para {payload.email}")
        fecha_expiracion = datetime.now() + timedelta(days=3650)
        raw_key = f"{payload.email}-ADMIN-BYPASS-REMI"
        hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
        licencia_final = f"REMI-DEV-ADMIN-{hash_key}"

        license_record = {
            "email": payload.email,
            "tx_hash": "LOCAL_ADMIN_BYPASS",
            "license": licencia_final,
            "issued_at": datetime.utcnow().isoformat(),
            "expires": fecha_expiracion.strftime("%Y-%m-%d"),
            "tier": payload.tier or "enterprise",
            "status": "ACTIVE",
            "verification": {"valid": True, "note": "Local Admin Bypass"},
        }
        
        db_result = save_license(license_record)
        if not db_result.get("ok"):
            if "already exists" in db_result.get("error", ""):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este correo ya cuenta con una licencia activa registrada."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al persistir la licencia de bypass: {db_result.get('error')}"
            )

        return {
            "valid": True,
            "message": "Licencia de auditoría interna generada con éxito.",
            "license": licencia_final,
            "expires": fecha_expiracion.strftime("%Y-%m-%d")
        }
    # -------------------------------------------------------------------------

    if not payload.tx_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tx_hash es obligatorio para clientes comerciales."
        )
        
    # Validación comercial normal (la que se sube a GitHub)
    verification = validate_transaction(payload.tx_hash, expected_min_amount=499.0, is_erc20=True)
    if not verification.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verificación on-chain fallida: {verification.get('error')}"
        )
    
    fecha_expiracion = datetime.now() + timedelta(days=365)
    raw_key = f"{payload.email}-{payload.tx_hash}-REMI-2026"
    hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
    licencia_final = f"REMI-ENT-ANNUAL-{hash_key}"

    license_record = {
        "email": payload.email,
        "tx_hash": payload.tx_hash,
        "license": licencia_final,
        "issued_at": datetime.utcnow().isoformat(),
        "expires": fecha_expiracion.strftime("%Y-%m-%d"),
        "tier": payload.tier,
        "status": "ACTIVE",
        "verification": verification,
    }

    db_result = save_license(license_record)
    if not db_result.get("ok"):
        if "already exists" in db_result.get("error", ""):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta transacción o correo ya fue utilizado para emitir otra licencia."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al persistir la licencia: {db_result.get('error')}"
        )

    logger.info(f"Licencia emitida con éxito para {payload.email}")
    return {
        "valid": True,
        "message": "Licencia emitida y guardada con éxito.",
        "license": licencia_final,
        "expires": fecha_expiracion.strftime("%Y-%m-%d")
    }

# Endpoint webhook de Stripe con verificación criptográfica real de firma
@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    import stripe
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET não está configurado.")
        raise HTTPException(status_code=500, detail="Webhook secret no configurado en el servidor.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload inválido")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma de webhook de Stripe inválida")

    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_email = event_data.get("customer_email") or event_data.get("customer_details", {}).get("email")
        customer_name = event_data.get("customer_details", {}).get("name", "Cliente Enterprise")
        
        fecha_expiracion = datetime.now() + timedelta(days=365)
        raw_key = f"REMI-FIAT-{customer_email}-{datetime.utcnow().isoformat()}"
        hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
        licencia_final = f"REMI-FIAT-ANNUAL-{hash_key}"

        license_record = {
            "email": customer_email,
            "tx_hash": "STRIPE_FIAT_CHECKOUT",
            "license": licencia_final,
            "issued_at": datetime.utcnow().isoformat(),
            "expires": fecha_expiracion.strftime("%Y-%m-%d"),
            "tier": "enterprise",
            "status": "ACTIVE",
            "client_name": customer_name
        }

        save_license(license_record)
        logger.info(f"[LICENCIA STRIPE EMITIDA]: {customer_email} - Clave: {licencia_final}")

        return {
            "status": "PROCESSED",
            "message": "Licencia emitida automáticamente por pago con tarjeta",
            "license_key": licencia_final,
            "email": customer_email
        }

    return {"status": "IGNORED", "reason": f"Evento {event_type} no requiere acción"}

# Endpoint protegido: Creación segura de issues en GitHub
@app.post("/github/create-issue", tags=["GitHub Automation"])
async def create_github_issue(issue: IssueRequest, api_key: str = Depends(verify_api_key)):
    token = os.getenv("GITHUB_BOT_TOKEN")
    if not token:
        logger.error("GITHUB_BOT_TOKEN no configurado en el servidor.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GITHUB_BOT_TOKEN não está configurado en el servidor."
        )
    
    def _create_issue_sync():
        from github import Github
        try:
            g = Github(token, timeout=15)
        except TypeError:
            g = Github(token)
            
        repo_name = os.getenv("GITHUB_REPO", "Jramone3/REMI_Enterprise_Suite")
        repo = g.get_repo(repo_name)
        return repo.create_issue(title=issue.title, body=issue.body)

    try:
        github_issue = await run_in_threadpool(_create_issue_sync)
        
        audit_entry = {
            "action": "CREATE_GITHUB_ISSUE",
            "issue_number": github_issue.number,
            "title": issue.title,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "SUCCESS"
        }
        save_audit_log(audit_entry)
        logger.info(f"Issue #{github_issue.number} creado exitosamente en GitHub.")

        return {
            "success": True,
            "issue_number": github_issue.number,
            "issue_url": github_issue.html_url
        }
        
    except Exception as ge:
        error_msg = str(ge)
        logger.error(f"Fallo en integración con GitHub API: {error_msg}")
        
        if "Bad Credentials" in error_msg or "401" in error_msg:
            detail_msg = "Credenciales de GitHub inválidas o expiradas en el servidor."
        elif "404" in error_msg:
            detail_msg = "Repositorio de GitHub no encontrado o sin permisos."
        else:
            detail_msg = "Error interno al comunicarse con la API de GitHub."

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail_msg
        )
