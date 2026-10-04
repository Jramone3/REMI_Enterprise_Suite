# license_service.py - Microservicio FastAPI seguro para gestión de licencias
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os

from db import init_db, save_license, find_license_by_email
from remi_tx_validator import validate_transaction

app = FastAPI(title="REMI License Microservice", version="2.0.0")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
REMI_API_KEY = os.getenv("REMI_API_KEY", "remi_secret_dev_key_2026")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == REMI_API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Credenciales de API Key inválidas o ausentes")

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos y los índices únicos al arrancar."""
    init_db()

class LicenseRequest(BaseModel):
    email: EmailStr
    tx_hash: str
    tier: str = "enterprise"

@app.post("/licenses/issue")
def issue_license(payload: LicenseRequest, api_key: str = Depends(get_api_key)):
    """Emite una nueva licencia tras validar la transacción on-chain (Protegido por API Key)."""
    # 1. Validar transacción on-chain
    validation = validate_transaction(payload.tx_hash)
    if not validation.get("valid"):
        raise HTTPException(status_code=400, detail=f"Transacción inválida: {validation.get('error', 'Desconocido')}")

    # 2. Guardar licencia en DB
    license_data = {
        "email": payload.email,
        "tx_hash": payload.tx_hash,
        "tier": payload.tier,
        "status": "active"
    }
    
    result = save_license(license_data)
    if not result.get("ok"):
        if "duplicate" in str(result.get("error", "")).lower():
            raise HTTPException(status_code=409, detail="La transacción ya fue utilizada para emitir una licencia.")
        raise HTTPException(status_code=500, detail=result.get("error", "Error interno de base de datos"))

    return {"status": "success", "message": "Licencia emitida correctamente", "id": result.get("inserted_id")}

@app.get("/licenses/verify/{email}")
def verify_license(email: str):
    """Verifica una licencia de forma pública sin exponer datos sensibles ni hashes de transacciones."""
    record = find_license_by_email(email)
    if not record:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")
    
    # Excluir explícitamente tx_hash u otros datos internos por seguridad
    safe_response = {
        "email": record.get("email"),
        "tier": record.get("tier"),
        "status": record.get("status", "active")
    }
    return {"status": "valid", "license": safe_response}
