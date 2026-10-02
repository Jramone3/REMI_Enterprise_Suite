"""
RemiTxValidator — Módulo endurecido y compatible con app.py
Valida transacciones en Base (Nativo y ERC-20) con checksums, confirmaciones y timeouts.
"""

import os
import logging
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_utils import is_address, to_checksum_address

logger = logging.getLogger("remi_tx_validator")
logging.basicConfig(level=logging.INFO)

DEFAULT_BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
TARGET_WALLET = os.getenv("REMI_PAYMENT_ADDRESS", "").strip()
EXPECTED_TOKEN = os.getenv("EXPECTED_TOKEN_ADDRESS", "").strip().lower()
EXPECTED_TOKEN_DECIMALS = int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6"))
MIN_CONFIRMATIONS = int(os.getenv("MIN_CONFIRMATIONS", "3"))
RPC_TIMEOUT = int(os.getenv("RPC_TIMEOUT_SECONDS", "10"))

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def _format_error(msg: str):
    logger.warning(msg)
    return {"valid": False, "error": msg}

def verify_base_transaction(tx_hash: str, expected_min_amount: float = 0.001, is_erc20: bool = False) -> dict:
    """
    expected_min_amount: en unidades humanas (ETH o token units). Ej: 499.0 para 499 USDT
    is_erc20: si True, valida logs ERC-20 usando EXPECTED_TOKEN_ADDRESS y EXPECTED_TOKEN_DECIMALS
    Retorna dict con 'valid': bool y campos adicionales.
    """
    try:
        if not isinstance(tx_hash, str) or not tx_hash.startswith("0x"):
            return _format_error("Formato de Tx hash inválido.")

        # Conexión RPC con timeout seguro
        w3 = Web3(Web3.HTTPProvider(DEFAULT_BASE_RPC, request_kwargs={"timeout": RPC_TIMEOUT}))
        if not w3.is_connected():
            return _format_error("No se pudo conectar al nodo RPC configurado.")

        if not TARGET_WALLET:
            return _format_error("REMI_PAYMENT_ADDRESS no configurada.")
        if not is_address(TARGET_WALLET):
            return _format_error("REMI_PAYMENT_ADDRESS inválida en configuración.")
        target_checksum = to_checksum_address(TARGET_WALLET)

        # Obtener receipt
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            return _format_error("La transacción no existe o aún no ha sido minada.")
        except Exception as e:
            return _format_error(f"Error al obtener receipt: {str(e)}")

        # Estado de la tx
        if receipt.get("status") not in (1, True):
            return _format_error("La transacción falló o fue revertida en la cadena.")

        tx_block = receipt.get("blockNumber")
        if tx_block is None:
            return _format_error("La transacción aún no está en un bloque confirmado.")

        current_block = w3.eth.block_number
        confirmations = (current_block - tx_block) + 1
        if confirmations < MIN_CONFIRMATIONS:
            return _format_error(f"Confirmaciones insuficientes ({confirmations}/{MIN_CONFIRMATIONS}).")

        # Validación ERC-20
        if is_erc20:
            if not EXPECTED_TOKEN:
                return _format_error("EXPECTED_TOKEN_ADDRESS no configurado para validación ERC-20.")

            transfer_found = False
            transferred_amount = 0.0

            for log in receipt.get("logs", []):
                log_addr = (log.get("address") or "").lower()
                if log_addr != EXPECTED_TOKEN:
                    continue
                topics = log.get("topics") or []
                if not topics or topics[0].lower() != TRANSFER_EVENT_SIGNATURE_HASH:
                    continue
                if len(topics) < 3:
                    continue
                to_topic = topics[2]
                if not isinstance(to_topic, str) or not to_topic.startswith("0x"):
                    continue
                recipient_address = "0x" + to_topic[-40:]
                try:
                    recipient_checksum = to_checksum_address(recipient_address)
                except Exception:
                    continue
                if recipient_checksum != target_checksum:
                    continue

                data = log.get("data", "0x0")
                raw_amount = int(data, 16) if isinstance(data, str) else int.from_bytes(data, "big")
                decimals = EXPECTED_TOKEN_DECIMALS
                transferred_amount = raw_amount / (10 ** decimals)
                transfer_found = True
                break

            if not transfer_found:
                return _format_error("No se encontró transferencia ERC-20 hacia la wallet objetivo en la tx.")
            if transferred_amount < expected_min_amount:
                return _format_error(f"Monto ERC-20 insuficiente ({transferred_amount} < {expected_min_amount}).")

            return {
                "valid": True,
                "type": "ERC20",
                "to": target_checksum,
                "amount": transferred_amount,
                "block_number": tx_block,
                "confirmations": confirmations,
            }

        # Validación Nativa (ETH)
        try:
            tx = w3.eth.get_transaction(tx_hash)
        except TransactionNotFound:
            return _format_error("Transacción nativa no encontrada.")
        except Exception as e:
            return _format_error(f"Error al obtener tx: {str(e)}")

        to_addr = tx.get("to")
        if not to_addr:
            return _format_error("La transacción no tiene campo 'to' (posible contrato).")
        try:
            to_checksum = to_checksum_address(to_addr)
        except Exception:
            return _format_error("Dirección destino inválida en la transacción.")
        if to_checksum != target_checksum:
            return _format_error("El destinatario no coincide con la wallet corporativa.")

        value_wei = tx.get("value", 0)
        value_eth = float(w3.from_wei(value_wei, "ether"))
        if value_eth < expected_min_amount:
            return _format_error(f"El monto transferido ({value_eth} ETH) es inferior al mínimo requerido.")

        return {
            "valid": True,
            "type": "NATIVE",
            "to": target_checksum,
            "amount": value_eth,
            "block_number": tx_block,
            "confirmations": confirmations,
        }

    except Exception as exc:
        logger.exception("Error técnico en verify_base_transaction")
        return {"valid": False, "error": f"Error técnico al procesar la verificación on-chain: {str(exc)}"}
