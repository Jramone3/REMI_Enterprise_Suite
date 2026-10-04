from db import save_license

# Primer registro de prueba
record_1 = {
    "email": "test_cliente@example.com",
    "tx_hash": "0x123456789abcdeftest",
    "license": "REMI-ENT-ANNUAL-TEST001",
    "issued_at": "2026-10-03T12:00:00",
    "expires": "2027-10-03",
    "type": "ANNUAL",
    "amount": 499.0,
    "status": "ACTIVE",
    "verification": {"valid": True}
}

# Segundo registro con el MISMO tx_hash (debe fallar por duplicado)
record_2 = {
    "email": "otro_cliente@example.com",
    "tx_hash": "0x123456789abcdeftest",  # Mismo Hash
    "license": "REMI-ENT-ANNUAL-TEST002",
    "issued_at": "2026-10-03T12:05:00",
    "expires": "2027-10-03",
    "type": "ANNUAL",
    "amount": 499.0,
    "status": "ACTIVE",
    "verification": {"valid": True}
}

print("--- Ejecutando prueba de persistencia ---")

# Intento 1: Debería guardarse con éxito
res_1 = save_license(record_1)
print(f"Resultado inserción 1: {res_1}")

# Intento 2: Debería detectar el índice único y retornar el error controlado
res_2 = save_license(record_2)
print(f"Resultado inserción 2 (duplicado): {res_2}")
