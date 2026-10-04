# license_service.py - Microservicio de Licenciamiento FastAPI
import os
from datetime import datetime, timedelta
import hashlib
from fastapi import FastAPI, HTTPException, Depends, Header, status
from pydantic import BaseModel
from db import init_db, save_license, find_license_by_email
from remi_tx_validator import validate_transaction

app = FastAPI(
    title="REMI License Microservice",
    version="2.0.0",
    description="Microservicio blindado de emisión y verificación de licencias para REMI Enterprise Suite"
)

# Evento de inicio: inicializa la base de datos y crea índices únicos (tx_hash, email)
@app.on_event("startup")
def startup_event():
    init_db()
    print("[INFO] Búnker DB inicializado y restricciones de índices únicos aplicadas.")

# Esquema de datos para emitir licencias
class LicenseRequest(BaseModel):
    email: str
    tx_hash: str
    tier: str = "standard"  # standard o enterprise

# Dependencia de seguridad: Validación de API Key del Administrador
# Dependencia de seguridad: Validación estricta de API Key del Administrador
def verify_api_key(x_api_key: str = Header(..., description="API Key de Administrador de REMI")):
    expected_key = os.getenv("REMI_API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error crítico de seguridad: REMI_API_KEY no está configurada en el servidor."
        )
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key de Administrador inválida o ausente."
        )
    return x_api_key

@app.get("/")
def health_check():
    return {"status": "online", "service": "REMI License Microservice"}

# Endpoint público blindado: Verifica licencia por correo ocultando datos sensibles (tx_hash)
@app.get("/licenses/verify/{email}")
def verify_license(email: str):
    record = find_license_by_email(email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna licencia activa para este correo."
        )
    
    # SANITIZACIÓN EXIGIDA: Ocultar tx_hash y datos internos sensibles
    public_response = {
        "email": record.get("email"),
        "license": record.get("license"),
        "tier": record.get("tier", "standard"),
        "status": record.get("status", "ACTIVE"),
        "expires": record.get("expires")
    }
    return public_response

# Endpoint protegido: Emisión de licencia con validación on-chain y API Key obligatoria
@app.post("/licenses/issue")
def issue_license(payload: LicenseRequest, api_key: str = Depends(verify_api_key)):
    if not payload.email or not payload.tx_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email y tx_hash son obligatorios."
        )
    
    # Validar la transacción on-chain en la red Base
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

    return {
        "valid": True,
        "message": "Licencia emitida y guardada con éxito.",
        "license": licencia_final,
        "expires": fecha_expiracion.strftime("%Y-%m-%d")
    }
