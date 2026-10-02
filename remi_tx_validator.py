"""
Módulo endurecido de validación de transacciones on-chain para REMI Enterprise Suite.
Asegura comprobación de checksum, confirmaciones mínimas y manejo de RPCs con fallback.
"""

import os
from web3 import Web3
from web3.exceptions import TransactionNotFound

# Configuración segura desde variables de entorno (con fallbacks defensivos)
DEFAULT_BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
TARGET_WALLET = os.getenv("REMI_PAYMENT_ADDRESS", "0x0000000000000000000000000000000000000000")
MIN_CONFIRMATIONS = int(os.getenv("MIN_CONFIRMATIONS", "3"))

class RemiTxValidator:
    def __init__(self, rpc_url: str = DEFAULT_BASE_RPC):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"No se pudo conectar al nodo RPC en: {rpc_url}")
        
        # Validar y formatear la wallet de destino en formato Checksum
        if self.w3.is_address(TARGET_WALLET):
            self.target_wallet = self.w3.to_checksum_address(TARGET_WALLET)
        else:
            raise ValueError(f"La dirección de pago configurada no es válida: {TARGET_WALLET}")

    def verify_base_transaction(self, tx_hash: str, expected_amount_wei: int) -> dict:
        """
        Verifica de forma estricta una transacción en la red Base:
        - Valida existencia y éxito del bloque.
        - Comprueba el destinatario (Checksum).
        - Valida el monto transferido.
        - Asegura un número mínimo de confirmaciones.
        """
        try:
            # Obtener recibo y transacción
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            tx = self.w3.eth.get_transaction(tx_hash)
        except TransactionNotFound:
            return {"status": False, "error": "Transacción no encontrada en la red."}
        except Exception as e:
            return {"status": False, "error": f"Error de comunicación RPC: {str(e)}"}

        # Verificar si la transacción fue exitosa (status == 1)
        if tx_receipt.get("status") != 1:
            return {"status": False, "error": "La transacción falló o fue revertida en la blockchain."}

        # Verificar confirmaciones (Bloque actual - bloque de la tx >= confirmaciones mínimas)
        current_block = self.w3.eth.block_number
        tx_block = tx_receipt.get("blockNumber")
        confirmations = current_block - tx_block

        if confirmations < MIN_CONFIRMATIONS:
            return {
                "status": False, 
                "error": f"Confirmaciones insuficientes ({confirmations}/{MIN_CONFIRMATIONS}). Espere más bloques."
            }

        # Validar dirección de destino (con Checksum estricto)
        to_address = tx.get("to")
        if not to_address or self.w3.to_checksum_address(to_address) != self.target_wallet:
            return {"status": False, "error": "La dirección de destino de la transacción no coincide con la oficial."}

        # Validar el monto transferido (en Wei)
        if tx.get("value", 0) < expected_amount_wei:
            return {"status": False, "error": "El monto enviado es inferior al requerido para la licencia."}

        return {
            "status": True, 
            "confirmations": confirmations,
            "block_number": tx_block,
            "sender": tx.get("from")
        }
    except Exception as e:
        logger.exception("Error en verificación on-chain")
        return {"valid": False, "error": f"Error técnico al procesar la verificación on-chain: {str(e)}"}
