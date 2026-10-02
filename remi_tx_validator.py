import os
import logging
from web3 import Web3

logger = logging.getLogger(__name__)

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def get_config():
    return {
        "payment_address": os.getenv("REMI_PAYMENT_ADDRESS", "").strip(),
        "min_confirmations": int(os.getenv("MIN_CONFIRMATIONS", "3")),
        "expected_token_address": os.getenv("EXPECTED_TOKEN_ADDRESS", "").strip().lower(),
        "expected_token_decimals": int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6")),
        "rpc_url": os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    }

def verify_base_transaction(tx_hash: str, expected_min_amount: float = 0.0, is_erc20: bool = False):
    config = get_config()
    
    if not config["payment_address"]:
        logger.warning("REMI_PAYMENT_ADDRESS no configurada.")
        return {"valid": False, "error": "REMI_PAYMENT_ADDRESS no configurada."}

    if not tx_hash or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return {"valid": False, "error": "Tx hash inválido o formato incorrecto."}

    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
        if not w3.is_connected():
            return {"valid": False, "error": "No se pudo conectar al nodo RPC de Base."}

        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt or receipt.get("status") != 1:
            return {"valid": False, "error": "La transacción falló o no existe."}

        current_block = w3.eth.block_number
        tx_block = receipt.get("blockNumber", 0)
        confirmations = current_block - tx_block + 1

        if confirmations < config["min_confirmations"]:
            return {"valid": False, "error": f"Confirmaciones insuficientes ({confirmations}/{config['min_confirmations']})."}

        target_address = config["payment_address"].lower()

        if not is_erc20:
            tx = w3.eth.get_transaction(tx_hash)
            if not tx or tx.get("to", "").lower() != target_address:
                return {"valid": False, "error": "La transacción no está dirigida a la dirección de pago."}
            
            value_wei = tx.get("value", 0)
            amount = float(w3.from_wei(value_wei, "ether"))
            if amount < expected_min_amount:
                return {"valid": False, "error": f"Monto insuficiente: {amount} < {expected_min_amount}"}
            
            return {"valid": True, "type": "NATIVE", "amount": amount, "confirmations": confirmations}
        else:
            token_address = config["expected_token_address"]
            decimals = config["expected_token_decimals"]
            
            target_topic = "0x" + "0" * 24 + target_address[2:]
            valid_transfer = False
            transferred_amount = 0.0

            for log in receipt.get("logs", []):
                if log.get("address", "").lower() == token_address:
                    topics = log.get("topics", [])
                    if len(topics) >= 3 and topics[0].hex() == TRANSFER_EVENT_SIGNATURE_HASH if hasattr(topics[0], "hex") else topics[0] == TRANSFER_EVENT_SIGNATURE_HASH:
                        if topics[2].lower() == target_topic.lower():
                            raw_data = log.get("data", "0x0")
                            if isinstance(raw_data, str):
                                raw_val = int(raw_data, 16)
                            else:
                                raw_val = int(raw_data)
                            transferred_amount = raw_val / (10 ** decimals)
                            if transferred_amount >= expected_min_amount:
                                valid_transfer = True
                                break

            if not valid_transfer:
                return {"valid": False, "error": "No se encontró transferencia ERC-20 válida a la dirección de pago."}

            return {"valid": True, "type": "ERC20", "amount": transferred_amount, "confirmations": confirmations}

    except Exception as e:
        return {"valid": False, "error": str(e)}
