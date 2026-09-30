import os
from web3 import Web3

# Configuración por defecto para la red Base (puede sobreescribirse con variables de entorno)
DEFAULT_BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
TARGET_WALLET = os.getenv("REMI_PAYMENT_ADDRESS", "0x96De980a766CCb10A19B6962587e2b61B650b372").lower()

def verify_base_transaction(tx_hash: str, expected_min_value_eth: float = 0.001) -> dict:
    """
    Verifica de forma on-chain en la red Base si una transacción es válida,
    pertenece al destinatario corporativo de REMI y cumple con el monto mínimo.
    """
    try:
        w3 = Web3(Web3.HTTPProvider(DEFAULT_BASE_RPC))
        
        if not w3.is_connected():
            return {"valid": False, "error": "No se pudo conectar al nodo RPC de la red Base."}

        # Limpiar y validar formato del hash
        if not tx_hash.startswith("0x") or len(tx_hash) != 66:
            return {"valid": False, "error": "Formato de Hash de transacción (TxID) inválido."}

        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)

        if not tx or not receipt:
            return {"valid": False, "error": "La transacción no existe o aún no ha sido minada."}

        # Verificar estado de la transacción (1 = éxito en EVM)
        if receipt.get("status") != 1:
            return {"valid": False, "error": "La transacción falló o fue revertida en la cadena."}

        # Validar dirección de destino (to)
        recipient = tx.get("to")
        if not recipient or recipient.lower() != TARGET_WALLET:
            return {"valid": False, "error": f"El destinatario de la transacción no coincide con la wallet corporativa de REMI."}

        # Validar valor transferido en ETH/Native Token de Base (wei a ether)
        value_eth = w3.from_wei(tx.get("value", 0), 'ether')
        if value_eth < expected_min_value_eth:
            return {"valid": False, "error": f"El monto transferido ({value_eth} ETH) es inferior al mínimo requerido ({expected_min_value_eth} ETH)."}

        return {
            "valid": True,
            "from": tx.get("from"),
            "to": recipient,
            "value_eth": float(value_eth),
            "block_number": receipt.get("blockNumber")
        }

    except Exception as e:
        return {"valid": False, "error": f"Error técnico al procesar la verificación on-chain: {str(e)}"}
