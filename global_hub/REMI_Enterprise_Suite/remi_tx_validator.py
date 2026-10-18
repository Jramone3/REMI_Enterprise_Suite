import os
import logging
import time
from typing import Any, Callable
from web3 import Web3
from web3.exceptions import TimeExhausted
import requests

logger = logging.getLogger(__name__)

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def get_config():
    return {
        "payment_address": os.getenv("REMI_PAYMENT_ADDRESS", "").strip(),
        "min_confirmations": int(os.getenv("MIN_CONFIRMATIONS", "3")),
        "expected_token_address": os.getenv("EXPECTED_TOKEN_ADDRESS", "").strip().lower(),
        "expected_token_decimals": int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6")),
        "rpc_url": os.getenv("BASE_RPC_URL", "https://mainnet.base.org"),
        "rpc_timeout": int(os.getenv("RPC_TIMEOUT", "10")),
        "rpc_retries": int(os.getenv("RPC_RETRIES", "3")),
        "rpc_backoff": float(os.getenv("RPC_BACKOFF", "0.5")),
    }


def _rpc_call_with_retries(call_fn: Callable[..., Any], retries: int, backoff: float, *args, **kwargs):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return call_fn(*args, **kwargs)
        except (requests.exceptions.RequestException, TimeExhausted, Exception) as e:
            # Catch broad exceptions here because underlying providers may raise different types
            last_exc = e
            logger.debug("RPC call failed on attempt %d/%d: %s", attempt, retries, e)
            if attempt < retries:
                sleep_time = backoff * (2 ** (attempt - 1))
                time.sleep(sleep_time)
            else:
                raise
    raise last_exc


def verify_base_transaction(tx_hash: str, expected_min_amount: float = 0.0, is_erc20: bool = False):
    config = get_config()

    if not config["payment_address"]:
        logger.warning("REMI_PAYMENT_ADDRESS no configurada.")
        return {"valid": False, "error": "REMI_PAYMENT_ADDRESS no configurada."}

    if not tx_hash or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return {"valid": False, "error": "Tx hash inválido o formato incorrecto."}

    try:
        # Configure provider with a timeout
        provider = Web3.HTTPProvider(config["rpc_url"], request_kwargs={"timeout": config["rpc_timeout"]})
        w3 = Web3(provider)

        # Basic connectivity check with retries
        try:
            connected = _rpc_call_with_retries(lambda: w3.is_connected(), config["rpc_retries"], config["rpc_backoff"])
        except Exception as e:
            logger.exception("Error conectando al nodo RPC: %s", e)
            return {"valid": False, "error": "No se pudo conectar al nodo RPC de Base."}

        if not connected:
            return {"valid": False, "error": "No se pudo conectar al nodo RPC de Base."}

        # Fetch receipt with retries
        receipt = _rpc_call_with_retries(lambda: w3.eth.get_transaction_receipt(tx_hash), config["rpc_retries"], config["rpc_backoff"])

        # If receipt not found or tx failed
        if not receipt:
            return {"valid": False, "error": "La transacción no existe o no tiene receipt aún."}

        # web3 returns receipt.status as int (1 success, 0 failed)
        status = receipt.get("status") if isinstance(receipt, dict) else getattr(receipt, "status", None)
        if status is None:
            # Some providers may provide a different structure; try attribute access
            try:
                status = int(receipt.status)
            except Exception:
                status = None

        if status == 0:
            return {"valid": False, "error": "La transacción fue revertida (status == 0)."}
        if status != 1:
            # treat unknown as error
            return {"valid": False, "error": "La transacción no fue exitosa."}

        # Block & confirmations
        current_block = _rpc_call_with_retries(lambda: w3.eth.block_number, config["rpc_retries"], config["rpc_backoff"]) if hasattr(w3.eth, "block_number") else None
        tx_block = receipt.get("blockNumber", 0)
        confirmations = (current_block - tx_block + 1) if (current_block is not None and tx_block) else 0

        if confirmations < config["min_confirmations"]:
            return {"valid": False, "error": f"Confirmaciones insuficientes ({confirmations}/{config['min_confirmations']})."}

        target_address = config["payment_address"].lower()

        if not is_erc20:
            tx = _rpc_call_with_retries(lambda: w3.eth.get_transaction(tx_hash), config["rpc_retries"], config["rpc_backoff"])
            tx_to = (tx.get("to", "") if isinstance(tx, dict) else getattr(tx, "to", None))
            tx_to_normalized = tx_to.lower() if isinstance(tx_to, str) else tx_to
            if not tx_to_normalized or tx_to_normalized != target_address:
                return {"valid": False, "error": "La transacción no está dirigida a la dirección de pago."}

            value_wei = tx.get("value", 0) if isinstance(tx, dict) else getattr(tx, "value", 0)
            amount = float(w3.from_wei(value_wei, "ether"))
            if amount < expected_min_amount:
                return {"valid": False, "error": f"Monto insuficiente: {amount} < {expected_min_amount}"}

            return {"valid": True, "type": "NATIVE", "amount": amount, "confirmations": confirmations}
        else:
            token_address = config["expected_token_address"]
            decimals = config["expected_token_decimals"]

            # Build topic for recipient (padded)
            target_topic = "0x" + ("0" * 24) + target_address[2:]
            valid_transfer = False
            transferred_amount = 0.0

            for log in receipt.get("logs", []):
                log_address = log.get("address", "").lower()
                if token_address and log_address != token_address:
                    continue

                topics = log.get("topics", [])
                if not topics or len(topics) < 3:
                    continue

                # Normalize topic0 to hex string
                topic0 = topics[0].hex() if hasattr(topics[0], "hex") else (topics[0] if isinstance(topics[0], str) else None)
                if not topic0:
                    continue

                if topic0.lower() != TRANSFER_EVENT_SIGNATURE_HASH.lower():
                    continue

                topic_to = topics[2].lower() if isinstance(topics[2], str) else (topics[2].hex().lower() if hasattr(topics[2], "hex") else None)
                if not topic_to:
                    continue

                if topic_to != target_topic.lower():
                    continue

                raw_data = log.get("data", "0x0")
                try:
                    if isinstance(raw_data, str):
                        raw_val = int(raw_data, 16)
                    else:
                        raw_val = int(raw_data)
                except Exception:
                    logger.debug("No se pudo parsear data de log: %s", raw_data)
                    continue

                transferred_amount = raw_val / (10 ** decimals)
                if transferred_amount >= expected_min_amount:
                    valid_transfer = True
                    break

            if not valid_transfer:
                return {"valid": False, "error": "No se encontró transferencia ERC-20 válida a la dirección de pago."}

            return {"valid": True, "type": "ERC20", "amount": transferred_amount, "confirmations": confirmations}

    except Exception as e:
        logger.exception("Error verificando transacción %s: %s", tx_hash, e)
        return {"valid": False, "error": str(e)}
