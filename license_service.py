from datetime import datetime, timedelta
import hashlib
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from db import save_license, find_license_by_email
from remi_tx_validator import verify_base_transaction

app = FastAPI(
    title="REMI Enterprise License Service",
    description="Microservicio FastAPI para la gestión y verificación on-chain de licencias corporativas.",
    version="1.0.0"
)

class LicenseRequest(BaseModel):
    email: EmailStr
    tx_hash: str
    is_erc20: bool = True
    expected_amount: float = 499.0

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "online", "service": "remi-license-service", "timestamp": datetime.utcnow().isoformat()}

@app.post("/licenses/issue", tags=["Licenses"])
def issue_license(payload: LicenseRequest):
    """Verifica la transacción on-chain y emite una licencia anual si el pago es válido."""
    if not payload.email or not payload.tx_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email y tx_hash son obligatorios.")

    try:
        verification = verify_base_transaction(
            payload.tx_hash,
            expected_min_amount=payload.expected_amount,
            is_erc20=payload.is_erc20
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error validando la transacción: {str(e)}")

    if not verification.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verificación fallida: {verification.get('error')}"
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
        "type": "ANNUAL",
        "amount": payload.expected_amount,
        "status": "ACTIVE",
        "verification": verification,
    }

    db_result = save_license(license_record)
    if not db_result.get("ok"):
        if "already exists" in db_result.get("error", ""):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta transacción ya fue utilizada para emitir otra licencia."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al persistir en base de datos: {db_result.get('error')}"
        )

    return {
        "success": True,
        "message": "Licencia emitida y guardada con éxito.",
        "license": licencia_final,
        "expires": fecha_expiracion.strftime("%Y-%m-%d")
    }

@app.get("/licenses/verify/{email}", tags=["Licenses"])
def verify_license(email: str):
    """Consulta el estado de la licencia asociada a un correo electrónico."""
    record = find_license_by_email(email)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró licencia para este correo.")
    
    # Ocultar ID interno de Mongo en la respuesta pública
    record.pop("_id", None)
    return {"status": "found", "license_data": record}
