# remi_tx_validator.py - Validador de transacciones on-chain
import requests
import os

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def validate_transaction(tx_hash: str):
    """Valida el formato y existencia de una transacción en la red Base/Ethereum."""
    if not tx_hash or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return {"valid": False, "error": "Formato de tx_hash inválido"}
    
    rpc_url = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 1
        }
        response = requests.post(rpc_url, json=payload, timeout=5)
        if response.status_code != 200:
            return {"valid": False, "error": "Error de comunicación con el nodo RPC"}
        
        data = response.json()
        tx_receipt = data.get("result")
        
        if not tx_receipt:
            return {"valid": False, "error": "Transacción no encontrada o pendiente"}
            
        return {"valid": True, "receipt": tx_receipt}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Alias de compatibilidad oficial
def verify_base_transaction(tx_hash: str, *args, **kwargs):
    return validate_transaction(tx_hash)
