import os
import logging
from web3 import Web3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remi_tx_validator")

DEFAULT_BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
TARGET_WALLET = os.getenv("REMI_PAYMENT_ADDRESS",
                          "0x96De980a766CCb10A19B6962587e2b61B650b372").lower()
EXPECTED_TOKEN = os.getenv("EXPECTED_TOKEN_ADDRESS", "").lower()
EXPECTED_TOKEN_DECIMALS = int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6"))

TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def verify_base_transaction(
        tx_hash: str,
        expected_min_amount: float = 0.001,
        is_erc20: bool = False) -> dict:
    try:
        if not tx_hash or not isinstance(tx_hash, str):
            return {"valid": False, "error": "Tx hash inválido."}

        if not tx_hash.startswith("0x") or len(tx_hash) < 10:
            return {"valid": False, "error": "Formato de Tx hash inválido."}

        # Permitir inyección de Web3 o instanciación estándar
        if callable(Web3) and not hasattr(Web3, "HTTPProvider"):
            w3 = Web3(DEFAULT_BASE_RPC)
        else:
            w3 = Web3(Web3.HTTPProvider(DEFAULT_BASE_RPC))

        if not w3.is_connected():
            return {
                "valid": False,
                "error": "No se pudo conectar al nodo RPC configurado."}

        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt:
            return {
                "valid": False,
                "error": "La transacción no existe o aún no ha sido minada."}

        if receipt.get("status") not in (1, True):
            return {
                "valid": False,
                "error": "La transacción falló o fue revertida en la cadena."}

        if is_erc20:
            if not EXPECTED_TOKEN:
                return {
                    "valid": False,
                    "error": "EXPECTED_TOKEN_ADDRESS no configurado para validación ERC-20."}

            transfer_found = False
            transferred_amount = 0.0

            for log in receipt.get("logs", []):
                log_addr = (log.get("address") or "").lower()
                if log_addr != EXPECTED_TOKEN:
                    continue

                topics = log.get("topics", [])
                if not topics or not isinstance(topics, list):
                    continue

                topic0 = topics[0]
                if not isinstance(topic0, str) or topic0.lower(
                ) != TRANSFER_EVENT_SIGNATURE_HASH:
                    continue

                if len(topics) < 3:
                    continue
                to_topic = topics[2]
                if not isinstance(to_topic,
                                  str) or not to_topic.startswith("0x"):
                    continue

                recipient_address = "0x" + to_topic[-40:]
                if recipient_address.lower() != TARGET_WALLET:
                    continue

                data = log.get("data", "0x0")
                raw_amount = int(
                    data,
                    16) if isinstance(
                    data,
                    str) else int.from_bytes(
                    data,
                    "big")
                decimals = EXPECTED_TOKEN_DECIMALS
                transferred_amount = raw_amount / (10 ** decimals)
                transfer_found = True
                break

            if not transfer_found:
                return {
                    "valid": False,
                    "error": "No se encontró transferencia ERC-20 hacia la wallet objetivo en la tx."}

            if transferred_amount < expected_min_amount:
                return {
                    "valid": False,
                    "error": f"Monto ERC-20 insuficiente ({transferred_amount} < {expected_min_amount})."}

            return {
                "valid": True,
                "type": "ERC20",
                "to": TARGET_WALLET,
                "amount": transferred_amount,
                "block_number": receipt.get("blockNumber"),
            }
        else:
            tx = w3.eth.get_transaction(tx_hash)
            if not tx:
                return {
                    "valid": False,
                    "error": "Transacción nativa no encontrada."}

            recipient = tx.get("to")
            if not recipient or recipient.lower() != TARGET_WALLET:
                return {
                    "valid": False,
                    "error": "El destinatario no coincide con la wallet corporativa."}

            value_wei = tx.get("value", 0)
            value_eth = float(w3.from_wei(value_wei, "ether"))
            if value_eth < expected_min_amount:
                return {
                    "valid": False,
                    "error": f"El monto transferido ({value_eth} ETH) es inferior al mínimo requerido."}

            return {
                "valid": True,
                "type": "NATIVE",
                "to": recipient,
                "amount": value_eth,
                "block_number": receipt.get("blockNumber"),
            }

    except Exception as e:
        logger.exception("Error en verificación on-chain")
        return {
            "valid": False,
            "error": f"Error técnico al procesar la verificación on-chain: {str(e)}"}
