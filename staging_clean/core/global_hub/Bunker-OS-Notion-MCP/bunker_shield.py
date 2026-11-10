import os
import json
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class RemiSecureBunker:
    def __init__(self, bunker_path="/mnt/sda7/remi_audit"):
        self.bunker_path = bunker_path
        self.key_path = os.path.join(bunker_path, "bunker.key")
        self.log_path = os.path.join(bunker_path, "immutable_audit.log")
        self._initialize_bunker()

    def _initialize_bunker(self):
        """Inicializa el búnker local asegurando directorios, permisos y llave maestra AES-256 (32 bytes)."""
        if not os.path.exists(self.bunker_path):
            os.makedirs(self.bunker_path, mode=0o700, exist_ok=True)
            
        if not os.path.exists(self.key_path):
            # Generar exactamente 32 bytes (256 bits) requeridos por AESGCM
            key = os.urandom(32)
            with open(self.key_path, "wb") as f:
                f.write(key)
            os.chmod(self.key_path, 0o600)

    def _get_master_key(self):
        with open(self.key_path, "rb") as f:
            return f.read()

    def dlp_preflight_check(self, data_payload):
        """Escaneo DLP preventivo para evitar fugas de llaves o tokens en Zona Roja."""
        forbidden_patterns = ["ntn_", "sk-", "Bearer ", "password", "secret"]
        payload_str = json.dumps(data_payload)
        for pattern in forbidden_patterns:
            if pattern in payload_str:
                raise ValueError(f"ALERTA DLP: Patrón sensible detectado '{pattern}'. Ciclo abortado por seguridad.")
        return True

    def encrypt_zero_knowledge(self, plaintext_dict, run_id):
        """Cifrado Zero-Knowledge con Autenticación de Datos Adicionales (AAD)."""
        self.dlp_preflight_check(plaintext_dict)
        key = self._get_master_key()
        aesgcm = AESGCM(key)
        
        nonce = os.urandom(12)
        aad = run_id.encode('utf-8')
        plaintext = json.dumps(plaintext_dict).encode('utf-8')
        
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
        
        # Registrar evento de cifrado exitoso en la bitácora
        self.append_tamper_evident_log("ENCRYPT_PAYLOAD", f"Datos patrimoniales cifrados exitosamente para tránsito cloud (Run ID: {run_id}).")
        
        # Empaquetar artefacto seguro para la Zona Ámbar/Verde
        return {
            "run_id": run_id,
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex()
        }

    def append_tamper_evident_log(self, event_type, details):
        """Bitácora forense encadenada por hashes (Tamper-Evident)."""
        timestamp = datetime.utcnow().isoformat()
        
        # Leer el hash del último registro para mantener la cadena inmutable
        last_hash = "0" * 64
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    try:
                        last_entry = json.loads(lines[-1].strip())
                        last_hash = last_entry.get("current_hash", last_hash)
                    except json.JSONDecodeError:
                        pass

        log_entry = {
            "timestamp": timestamp,
            "event": event_type,
            "details": details,
            "previous_hash": last_hash
        }
        
        # Calcular hash actual de la entrada
        entry_string = json.dumps(log_entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_string.encode('utf-8')).hexdigest()
        log_entry["current_hash"] = current_hash

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return current_hash

# Ejecución principal y pruebas de validación del búnker local
if __name__ == "__main__":
    bunker = RemiSecureBunker()
    bunker.append_tamper_evident_log("SYSTEM_INIT", "Escudo del búnker unificado activado y listo para operar.")
    
    run_id_test = "RUN-2026-0915-001"
    test_data = {"task": "auditoria_perimetral", "status": "STATUS: IDENTIDAD_ALINEADA"}
    
    encrypted_package = bunker.encrypt_zero_knowledge(test_data, run_id_test)
    
    print("STATUS: BÚNKER LOCAL BLINDADO Y OPERATIVO (AES-GCM + Tamper-Evident)")
    print(f"Paquete Cifrado Generado: {encrypted_package['run_id']}")
