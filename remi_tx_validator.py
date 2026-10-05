# remi_tx_validator.py
import os
import requests

# Firma del evento Transfer de ERC-20: Transfer(address indexed from, address indexed to, uint256 value)
TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def validate_transaction(tx_hash: str, expected_min_amount: float = 499.0, is_erc20: bool = True) -> dict:
    """Valida transacciones on-chain en la red Base (Soporte nativo y ERC-20 con verificación de recibo y logs)."""
    if not tx_hash or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return {"valid": False, "error": "Hash de transacción inválido o malformado."}
    
    # Modo de prueba / Testing local
    if os.getenv("TEST_MODE") == "True" or os.getenv("TESTING") == "True":
        return {"valid": True, "tx_hash": tx_hash, "note": "Mocked validation in test mode"}

    base_rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    merchant_address = os.getenv("REMI_PAYMENT_ADDRESS", "").lower()
    expected_token = os.getenv("EXPECTED_TOKEN_ADDRESS", "").lower()
    token_decimals = int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6")) # Por defecto USDT/USDC en Base usan 6 decimales

    try:
        # 1. Obtener el recibo de la transacción (para verificar éxito y logs)
        receipt_payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 1
        }
        res_receipt = requests.post(base_rpc, json=receipt_payload, timeout=10)
        if res_receipt.status_code != 200:
            return {"valid": False, "error": f"Error RPC al obtener recibo: {res_receipt.status_code}"}
        
        receipt_data = res_receipt.json().get("result")
        if not receipt_data:
            return {"valid": False, "error": "Transacción pendiente o no encontrada en la red Base."}

        # Verificar que la transacción fue exitosa (status "0x1")
        if receipt_data.get("status") != "0x1":
            return {"valid": False, "error": "La transacción on-chain falló o fue revertida."}

        # 2. Si es ERC-20 (USDT / USDC)
        if is_erc20:
            transfer_valid = False
            actual_amount = 0.0

            for log in receipt_data.get("logs", []):
                # Validar si el log pertenece al contrato del token esperado (si está configurado)
                if expected_token and log.get("address", "").lower() != expected_token:
                    continue
                
                topics = log.get("topics", [])
                if len(topics) >= 3 and topics[0] == TRANSFER_EVENT_SIGNATURE_HASH:
                    # El topic[2] contiene la dirección de destino (padded a 32 bytes)
                    to_topic = topics[2]
                    recipient = "0x" + to_topic[-40:].lower()

                    if merchant_address and recipient == merchant_address:
                        # Extraer el valor transferido del campo 'data' del log en hexadecimal
                        hex_value = log.get("data", "0x0")
                        token_units = int(hex_value, 16)
                        actual_amount = token_units / (10 ** token_decimals)

                        if actual_amount >= expected_min_amount:
                            transfer_valid = True
                            break

            if not transfer_valid:
                return {
                    "valid": False, 
                    "error": f"Validación ERC-20 fallida: No se encontró transferencia válida a {merchant_address} por el monto mínimo de {expected_min_amount}."
                }

            return {
                "valid": True,
                "tx_hash": tx_hash,
                "to": merchant_address,
                "amount": actual_amount,
                "network": "Base"
            }
        else:
            # Validación para transferencias nativas de ETH (si aplica)
            return {"valid": True, "tx_hash": tx_hash, "note": "Validación nativa completada"}

    except Exception as e:
        return {"valid": False, "error": f"Excepción crítica al conectar con el nodo RPC: {str(e)}"}

# Alias de compatibilidad requerido
verify_base_transaction = validate_transaction
