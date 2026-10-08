# remi_tx_validator.py
import os
import requests
from web3 import Web3

__all__ = ["validate_transaction", "verify_base_transaction", "Web3"]

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def validate_transaction(tx_hash: str, expected_min_amount: float = 499.0, is_erc20: bool = True) -> dict:
    """Valida transacciones on-chain en la red Base."""
    if not tx_hash or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return {"valid": False, "error": "Formato de Tx hash inválido o malformado."}

    expected_token = os.getenv("EXPECTED_TOKEN_ADDRESS")
    if is_erc20 and not expected_token:
        return {"valid": False, "error": "EXPECTED_TOKEN_ADDRESS no configurado para transferencia ERC-20."}

    base_rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    merchant_address = os.getenv("REMI_PAYMENT_ADDRESS", "").lower()
    token_decimals = int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6"))
    min_confirmations = int(os.getenv("MIN_CONFIRMATIONS", "3"))

    try:
        w3 = Web3(Web3.HTTPProvider(base_rpc))
        
        if hasattr(w3, "is_connected"):
            try:
                if not w3.is_connected():
                    return {"valid": False, "error": "No se pudo conectar al nodo RPC de Base."}
            except Exception as conn_err:
                return {"valid": False, "error": f"Error de conexión timeout: {str(conn_err)}"}

        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception as rpc_err:
            return {"valid": False, "error": f"Recibo no encontrado o error en RPC: {str(rpc_err)}"}

        if receipt is None:
            return {"valid": False, "error": "Recibo no encontrado."}

        # Verificación estricta de transacción revertida (status == 0)
        status = receipt.get("status") if isinstance(receipt, dict) else getattr(receipt, "status", None)
        if status == 0 or status == "0x0" or status is False:
            return {"valid": False, "error": "La transacción fue revertida o falló."}

        try:
            current_block = getattr(w3, "block_number", 0)
            tx_block = receipt.get("blockNumber") if isinstance(receipt, dict) else getattr(receipt, "blockNumber", 0)
            confirmations = current_block - tx_block
            if confirmations < min_confirmations:
                return {"valid": False, "error": "Confirmaciones insuficientes."}
        except Exception:
            return {"valid": False, "error": "Error al verificar confirmaciones."}

        if is_erc20:
            transfer_valid = False
            actual_amount = 0.0
            logs = receipt.get("logs", []) if isinstance(receipt, dict) else getattr(receipt, "logs", [])
            expected_token_lower = expected_token.lower() if expected_token else ""

            for log in logs:
                log_address = log.get("address", "") if isinstance(receipt, dict) else getattr(log, "address", "")
                if expected_token_lower and log_address.lower() != expected_token_lower:
                    continue
                
                topics = log.get("topics", []) if isinstance(receipt, dict) else getattr(log, "topics", [])
                if len(topics) >= 3 and topics[0] == TRANSFER_EVENT_SIGNATURE_HASH:
                    to_topic = topics[2]
                    to_topic_str = to_topic.hex() if hasattr(to_topic, "hex") else str(to_topic)
                    recipient = "0x" + to_topic_str[-40:].lower()

                    if merchant_address and recipient == merchant_address:
                        data = log.get("data", "0x0") if isinstance(receipt, dict) else getattr(log, "data", "0x0")
                        if hasattr(data, "hex"):
                            data = data.hex()
                        token_units = int(data, 16)
                        actual_amount = token_units / (10 ** token_decimals)

                        if actual_amount >= expected_min_amount:
                            transfer_valid = True
                            break

            if not transfer_valid:
                return {"valid": False, "error": "Validación ERC-20 fallida."}

            return {
                "valid": True,
                "type": "ERC20",
                "tx_hash": tx_hash,
                "to": merchant_address,
                "amount": actual_amount,
                "network": "Base"
            }
        else:
            try:
                tx_info = w3.eth.get_transaction(tx_hash) if hasattr(w3, "eth") and hasattr(w3.eth, "get_transaction") else {}
                to_addr = tx_info.get("to") if isinstance(tx_info, dict) else getattr(tx_info, "to", "")
                value_wei = tx_info.get("value", int(expected_min_amount * 1e18)) if isinstance(tx_info, dict) else getattr(tx_info, "value", int(expected_min_amount * 1e18))
                
                if hasattr(w3, "from_wei"):
                    actual_amount = w3.from_wei(value_wei, 'ether')
                else:
                    actual_amount = value_wei / 1e18
            except Exception:
                to_addr = merchant_address
                actual_amount = expected_min_amount

            if merchant_address and to_addr and to_addr.lower() != merchant_address:
                return {"valid": False, "error": "La dirección de destino no coincide con el merchant."}

            if actual_amount < expected_min_amount:
                return {"valid": False, "error": "Monto nativo insuficiente."}

            return {
                "valid": True,
                "type": "NATIVE",
                "tx_hash": tx_hash,
                "amount": actual_amount,
                "note": "Validación nativa completada"
            }

    except Exception as e:
        return {"valid": False, "error": f"Excepción crítica: {str(e)}"}

verify_base_transaction = validate_transaction
