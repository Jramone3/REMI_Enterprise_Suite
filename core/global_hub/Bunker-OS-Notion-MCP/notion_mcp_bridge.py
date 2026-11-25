import os
import json
import urllib.request
import urllib.error

# Configuración del Puente MCP para Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

def send_executive_report_to_notion(database_id: str, run_id: str, status: str, forensic_hash: str):
    """Envía un informe ejecutivo sanitizado a Notion utilizando la API oficial vía MCP."""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    # Estructura del payload ejecutivo (Zona Verde / Sanitizado)
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": f"REMI Report: {run_id}"
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": "OPERATIVO"
                }
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Ejecución de ciclo completada de forma segura bajo el modelo de Tres Zonas de Confianza.\n\n- Run ID: {run_id}\n- Estado del Sistema: {status}\n- Hash Forense (Tamper-Evident): {forensic_hash}"
                            }
                        }
                    ]
                }
            }
        ]
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(NOTION_API_URL, data=req_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            print("STATUS: REPORTE ENVIADO EXITOSAMENTE A NOTION VÍA MCP")
            return json.loads(response_body)
    except urllib.error.HTTPError as e:
        error_message = e.read().decode("utf-8")
        print(f"ERROR MCP NOTION (HTTP {e.code}): {error_message}")
        return None

if __name__ == "__main__":
    print("Módulo MCP Notion listo. Se requiere el ID de la base de datos de Notion para realizar pruebas de sincronización.")
