import os
import json
import urllib.request
import urllib.error
from bunker_shield import RemiSecureBunker

# Configuración del Puente MCP y Credenciales del Búnker
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

class RemiOrchestratorMCP:
    def __init__(self, database_id="TU_DATABASE_ID_DE_NOTION"):
        self.bunker = RemiSecureBunker()
        self.database_id = database_id

    def execute_pipeline(self, run_id: str, raw_payload: dict):
        print(f"[{run_id}] INICIO DE CICLO: Máquina de Estados Idempotente activada.")
        
        # PASO 1: PACKAGED & DLP PREFLIGHT (Zona Roja)
        try:
            self.bunker.dlp_preflight_check(raw_payload)
            print(f"[{run_id}] [PACKAGED] DLP Preflight superado con éxito.")
        except ValueError as e:
            print(f"[{run_id}] [ABORTADO] {e}")
            return False

        # PASO 2: ENCRYPTED (Zero-Knowledge con AAD)
        encrypted_package = self.bunker.encrypt_zero_knowledge(raw_payload, run_id)
        print(f"[{run_id}] [ENCRYPTED] Datos cifrados correctamente en Zona Roja.")

        # PASO 3 & 4: SYNCED & REPORTED (Zona Verde / Notion MCP)
        report_status = self._send_to_notion(run_id, "OPERATIVO", encrypted_package["nonce"])
        
        # PASO 5 & 6: AUDITED & DONE (Bitácora Tamper-Evident)
        forensic_hash = self.bunker.append_tamper_evident_log(
            "PIPELINE_SUCCESS", 
            {"run_id": run_id, "notion_sync": report_status}
        )
        print(f"[{run_id}] [AUDITED] Hash forense encadenado: {forensic_hash}")
        print(f"[{run_id}] [DONE] Ciclo completado bajo soberanía absoluta del búnker.")
        return True

    def _send_to_notion(self, run_id: str, status: str, fingerprint: str):
        if self.database_id == "TU_DATABASE_ID_DE_NOTION":
            print("[MCP NOTION] Advertencia: ID de base de datos no configurado. Simulando reporte ejecutivo...")
            return "SIMULATED_SUCCESS"

        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        }

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": f"REMI Report: {run_id}"}}]
                },
                "Status": {
                    "select": {"name": status}
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"Informe automatizado de Bunker OS (REMI_CORE).\n\n- Run ID: {run_id}\n- Estado: {status}\n- Sello Criptográfico (Fingerprint): {fingerprint}"
                            }
                        }]
                    }
                }
            ]
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(NOTION_API_URL, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                print("[MCP NOTION] [REPORTED] Sincronización exitosa con Notion vía MCP.")
                return "SUCCESS"
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"[MCP NOTION ERROR] HTTP {e.code}: {err_msg}")
            return f"ERROR_{e.code}"

if __name__ == "__main__":
    # Inicializar orquestador en el búnker local (/mnt/sda7/remi_audit/)
    orchestrator = RemiOrchestratorMCP()
    
    # Prueba de ejecución con datos limpios
    test_run_id = "RUN-2026-0915-PROD"
    test_payload = {
        "agent": "REMI_SENTRY_NODE_001",
        "task": "auditoria_perimetral_automatica",
        "metrics": {"threats_blocked": 0, "status": "CLEAN"}
    }
    
    orchestrator.execute_pipeline(test_run_id, test_payload)
