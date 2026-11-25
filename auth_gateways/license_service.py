# license_service.py - Microservicio de Licenciamiento FastAPI (Producción)
import os
import logging
import time
import asyncio
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from auth_gateways.db import (
    init_db,
    save_license,
    find_license_by_email,
    find_license_by_tx_hash,
    save_audit_log,
    ping_db
)
from auth_gateways.remi_tx_validator import validate_transaction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("remi_license_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Arranque Fail-Fast estricto y aborto si falla MongoDB ---
    connected = False
    last_error = None
    for attempt in range(1, 11):
        try:
            init_db()
            connected = True
            logger.info("🚀 REMI Enterprise Suite - Búnker DB conectado y restricciones de índices únicas aplicadas.")
            print("🚀 REMI Enterprise Suite - Licencias iniciado correctamente.")
            break
        except Exception as e:
            last_error = e
            logger.warning(f"Intento {attempt}/10: Esperando a que MongoDB esté disponible... ({e})")
            print(f"⏳ Esperando conexión a MongoDB (intento {attempt}/10)...")
            await asyncio.sleep(2)
    
    if not connected:
        logger.critical(f"⚠️ FALLO CRÍTICO: No se pudo conectar a MongoDB tras 10 intentos: {last_error}. Abortando arranque.")
        raise RuntimeError(f"Fallo crítico de infraestructura: MongoDB no disponible o índices no aplicados ({last_error})")

    yield
    
    logger.info("🛑 Apagando servicios de REMI Enterprise...")
    print("🛑 Apagando servicios...")

app = FastAPI(
    title="REMI License Microservice",
    version="2.7.0",
    description="Microservicio blindado de emisión, verificación de licencias, pagos fiduciarios (Stripe) y automatización para REMI Enterprise Suite",
    lifespan=lifespan
)

class LicenseRequest(BaseModel):
    email: str
    tx_hash: str
    tier: str = "standard"

class IssueRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    body: str = Field(default="Generado automáticamente por REMI Core OS", max_length=2000)

def verify_api_key(x_api_key: str = Header(..., description="API Key de Administrador de REMI")):
    expected_key = os.getenv("REMI_API_KEY")
    if not expected_key:
        logger.critical("Error crítico: REMI_API_KEY no está configurada en el servidor.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error crítico de seguridad.")
    if x_api_key != expected_key:
        logger.warning("Intento de acceso denegado con API Key inválida o ausente.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida o ausente.")
    return x_api_key

@app.get("/")
def health_check():
    """Health check real: ejecuta ping a MongoDB y retorna 503 si la base está inaccesible."""
    try:
        ping_db()
        return {"status": "online", "database": "connected", "service": "REMI License Microservice"}
    except Exception as exc:
        logger.warning("Health check fallido: MongoDB no está disponible: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible o sin conectividad."
        )

@app.get("/licenses/verify/{email}")
def verify_license(email: str):
    record = find_license_by_email(email)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró ninguna licencia activa para este correo.")
    
    full_key = record.get("license", "")
    masked_key = "****-****-****-" + full_key[-4:] if len(full_key) >= 4 else "****"

    return {
        "email": record.get("email"),
        "masked_license": masked_key,
        "tier": record.get("tier", "standard"),
        "status": record.get("status", "ACTIVE"),
        "expires": record.get("expires")
    }

@app.post("/licenses/issue")
def issue_license(payload: LicenseRequest, api_key: str = Depends(verify_api_key)):
    if not payload.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo email es obligatorio.")
    
    local_master_bypass = os.getenv("REMI_INTERNAL_BYPASS_HASH")
    if local_master_bypass and payload.tx_hash == local_master_bypass:
        logger.info(f"[BYPASS INTERNO LOCAL]: Emitiendo licencia de auditoría para {payload.email}")
        fecha_expiracion = datetime.now() + timedelta(days=3650)
        raw_key = f"{payload.email}-ADMIN-BYPASS-REMI"
        hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
        licencia_final = f"REMI-DEV-ADMIN-{hash_key}"

        license_record = {
            "email": payload.email,
            "tx_hash": f"LOCAL_ADMIN_BYPASS_{payload.email}_{int(time.time())}",
            "license": licencia_final,
            "issued_at": datetime.utcnow().isoformat(),
            "expires": fecha_expiracion.strftime("%Y-%m-%d"),
            "tier": payload.tier or "enterprise",
            "status": "ACTIVE",
            "verification": {"valid": True, "note": "Local Admin Bypass"},
        }
        
        db_result = save_license(license_record)
        if not db_result.get("ok"):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al persistir bypass: {db_result.get('error')}")

        return {"valid": True, "message": "Licencia de bypass generada con éxito.", "license": licencia_final, "expires": fecha_expiracion.strftime("%Y-%m-%d")}

    if not payload.tx_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tx_hash es obligatorio.")
        
    verification = validate_transaction(payload.tx_hash, expected_min_amount=499.0, is_erc20=True)
    if not verification.get("valid"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Verificación on-chain fallida: {verification.get('error')}")
    
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al persistir la licencia: {db_result.get('error')}")

    return {"valid": True, "message": "Licencia emitida y guardada con éxito.", "license": licencia_final, "expires": fecha_expiracion.strftime("%Y-%m-%d")}

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    import stripe
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET no está configurado.")
        raise HTTPException(status_code=500, detail="Webhook secret no configurado.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload inválido")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma de Stripe inválida")

    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        if event_data.get("payment_status") != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago de Stripe no está completado.",
            )

        # Validación estricta de moneda (USD obligatoria)
        expected_currency = os.getenv("EXPECTED_LICENSE_CURRENCY", "usd").lower()
        currency = event_data.get("currency", "").lower()
        if currency != expected_currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Moneda inválida: {currency}. Se esperaba estrictamente {expected_currency}.",
            )

        session_id = event_data.get("id")
        if not session_id:
            raise HTTPException(status_code=400, detail="ID de sesión de Stripe ausente.")

        tx_key = f"STRIPE_SESSION_{session_id}"

        # 1. Consulta previa estricta para garantizar idempotencia absoluta y retornar 200 OK
        existing_license = find_license_by_tx_hash(tx_key)
        if existing_license:
            logger.info(f"Webhook de Stripe duplicado detectado por consulta previa para session_id {session_id}.")
            return {
                "status": "ALREADY_PROCESSED",
                "message": "Evento ya procesado anteriormente.",
                "license_key": existing_license.get("license")
            }

        expected_amount = float(os.getenv("EXPECTED_LICENSE_AMOUNT", "499.0")) * 100
        amount_total = event_data.get("amount_total", 0)
        if amount_total < expected_amount:
            raise HTTPException(status_code=400, detail=f"Monto insuficiente: {amount_total/100.0}.")

        customer_email = event_data.get("customer_email") or event_data.get("customer_details", {}).get("email")
        customer_name = event_data.get("customer_details", {}).get("name", "Cliente Enterprise")
        
        if not customer_email:
            raise HTTPException(status_code=400, detail="Correo del cliente ausente en la sesión.")

        fecha_expiracion = datetime.now() + timedelta(days=365)
        raw_key = f"REMI-FIAT-{customer_email}-{session_id}"
        hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
        licencia_final = f"REMI-FIAT-ANNUAL-{hash_key}"

        license_record = {
            "email": customer_email,
            "tx_hash": tx_key,
            "license": licencia_final,
            "issued_at": datetime.utcnow().isoformat(),
            "expires": fecha_expiracion.strftime("%Y-%m-%d"),
            "tier": "enterprise",
            "status": "ACTIVE",
            "client_name": customer_name,
            "gateway": "stripe"
        }

        db_result = save_license(license_record)
        if not db_result.get("ok"):
            # 2. Segunda verificación en caso de carrera concurrente (idempotencia por índice único)
            conflict_license = find_license_by_tx_hash(tx_key)
            if conflict_license:
                logger.info(f"Carrera concurrente resuelta para session_id {session_id}. Retornando licencia existente.")
                return {
                    "status": "ALREADY_PROCESSED",
                    "message": "Licencia ya procesada concurrentemente.",
                    "license_key": conflict_license.get("license")
                }
            logger.error(f"Fallo al persistir licencia Stripe: {db_result.get('error')}")
            raise HTTPException(status_code=500, detail="Error al persistir en base de datos.")

        return {"status": "PROCESSED", "message": "Licencia emitida correctamente", "license_key": licencia_final}

    return {"status": "IGNORED", "reason": f"Evento {event_type} sin acción"}

@app.post("/github/create-issue", tags=["GitHub Automation"])
async def create_github_issue(issue: IssueRequest, api_key: str = Depends(verify_api_key)):
    token = os.getenv("GITHUB_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GITHUB_BOT_TOKEN no configurado.")
    
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
        audit_entry = {"action": "CREATE_GITHUB_ISSUE", "issue_number": github_issue.number, "title": issue.title, "timestamp": datetime.utcnow().isoformat(), "status": "SUCCESS"}
        save_audit_log(audit_entry)
        return {"success": True, "issue_number": github_issue.number, "issue_url": github_issue.html_url}
    except Exception as ge:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error en GitHub API: {str(ge)}")
