# license_service.py - Microservicio de Licenciamiento REMI
import os
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel, EmailStr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from db import init_db, save_license, get_license_by_email
from remi_tx_validator import validate_transaction

# Inicialización de Limitador de Tasa
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="REMI License Service", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Seguridad por API Key
API_KEY_NAME = "X-API-Key"
EXPECTED_API_KEY = os.getenv("REMI_API_KEY", "remi_secret_dev_key_2026")

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Credenciales de API Key inválidas o ausentes")
    return x_api_key

@app.on_event("startup")
def startup_event():
    init_db()

class LicenseRequest(BaseModel):
    email: EmailStr
    tx_hash: str
    tier: str = "standard"

@app.post("/licenses/issue")
@limiter.limit("5/minute")
def issue_license(request: Request, body: LicenseRequest, api_key: str = Depends(verify_api_key)):
    # 1. Validar la transacción en on-chain
    validation = validate_transaction(body.tx_hash)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=f"Transacción inválida: {validation['error']}")
    
    # 2. Guardar licencia en base de datos
    existing = get_license_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una licencia asociada a este correo.")
    
    license_doc = {
        "email": body.email,
        "tx_hash": body.tx_hash,
        "tier": body.tier,
        "status": "active"
    }
    
    try:
        save_license(license_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al registrar la licencia.")
        
    return {"status": "success", "message": "Licencia emitida correctamente", "tier": body.tier}

@app.get("/licenses/verify/{email}")
@limiter.limit("20/minute")
def verify_license(request: Request, email: str):
    record = get_license_by_email(email)
    if not record:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")
    
    # BLINDAJE: Ocultar completamente tx_hash y detalles internos sensibles
    return {
        "status": record.get("status", "active"),
        "email": record.get("email"),
        "tier": record.get("tier", "standard")
    }
