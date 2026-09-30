import os
from web3 import Web3

DEFAULT_BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
TARGET_WALLET = os.getenv("REMI_PAYMENT_ADDRESS", "0x96De980a766CCb10A19B6962587e2b61B650b372").lower()
EXPECTED_TOKEN = os.getenv("EXPECTED_TOKEN_ADDRESS", "").lower() # Dejar vacío si es nativo, o colocar contrato USDT/USDC

# Firma del evento Transfer de ERC-20: Transfer(address,address,uint256)
TRANSFER_EVENT_SIGNATURE_HASH = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def verify_base_transaction(tx_hash: str, expected_min_amount: float = 0.001, is_erc20: bool = False) -> dict:
    """
    Verifica transacciones on-chain en la red Base (Soporta transferencias nativas y tokens ERC-20).
    """
    try:
        w3 = Web3(Web3.HTTPProvider(DEFAULT_BASE_RPC))
        
        if not w3.is_connected():
            return {"valid": False, "error": "No se pudo conectar al nodo RPC de la red Base."}

        if not tx_hash.startswith("0x") or len(tx_hash) != 66:
            return {"valid": False, "error": "Formato de Hash de transacción (TxID) inválido."}

        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt:
            return {"valid": False, "error": "La transacción no existe o aún no ha sido minada."}

        if receipt.get("status") != 1:
            return {"valid": False, "error": "La transacción falló o fue revertida en la cadena."}

        # --- CASO ERC-20 (USDT / USDC) ---
        if is_erc20:
            if not EXPECTED_TOKEN:
                return {"valid": False, "error": "EXPECTED_TOKEN_ADDRESS no está configurado para validación ERC-20."}
            
            transfer_found = False
            transferred_amount = 0.0

            for log in receipt.get("logs", []):
                # Verificar si el log proviene del contrato del token esperado
                if log.get("address", "").lower() == EXPECTED_TOKEN:
                    topics = log.get("topics", [])
                    if topics and topics.hex() if hasattr(topics[0], 'hex') else topics[0] == TRANSFER_EVENT_SIGNATURE_HASH:
                        # El topic[2] contiene la dirección de destino (padded a 32 bytes)
                        to_topic = topics
                        recipient_address = "0x" + to[-40:]
                        
                        if recipient_address.lower() == TARGET_WALLET:
                            # Decodificar el monto (data del log)
                            data = log.get("data", "0x0")
                            raw_amount = int(data, 16) if isinstance(data, str) else int.from_bytes(data, "big")
                            
                            # USDT/USDC en Base usan típicamente 6 decimales
                            decimals = int(os.getenv("EXPECTED_TOKEN_DECIMALS", "6"))
                            transferred_amount = raw_amount / (10 ** decimals)
                            transfer_found = True
                            break

            if not transfer_found:
                return {"valid": False, "error": "No se encontró una transferencia ERC-20 válida hacia la wallet corporativa en esta transacción."}

            if transferred_amount < expected_min_amount:
                return {"valid": False, "error": f"Monto ERC-20 insuficiente ({transferred_amount} < {expected_min_amount})."}

            return {
                "valid": True,
                "type": "ERC20",
                "to": TARGET_WALLET,
                "amount": transferred_amount,
                "block_number": receipt.get("blockNumber")
            }

        # --- CASO NATIVO (ETH) ---
        else:
            tx = w3.eth.get_transaction(tx_hash)
            if not tx:
                return {"valid": False, "error": "Transacción nativa no encontrada."}

            recipient = tx.get("to")
            if not recipient or recipient.lower() != TARGET_WALLET:
                return {"valid": False, "error": "El destinatario de la transacción no coincide con la wallet corporativa."}

            value_eth = float(w3.from_wei(tx.get("value", 0), 'ether'))
            if value_eth < expected_min_amount:
                return {"valid": False, "error": f"El monto transferido ({value_eth} ETH) es inferior al mínimo requerido."}

            return {
                "valid": True,
                "type": "NATIVE",
                "to": recipient,
                "amount": value_eth,
                "block_number": receipt.get("blockNumber")
            }

    except Exception as e:
        return {"valid": False, "error": f"Error técnico al procesar la verificación on-chain: {str(e)}"}
