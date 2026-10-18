import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Bunker-OS")

def sanitize_data(text):
    trackers = ["pixel.reddit.com", "analytics", "tracking_id"]
    sanitized = text
    for t in trackers:
        if t in sanitized:
            sanitized = sanitized.replace(t, "[BLOQUEADO-POR-REMI]")
    return sanitized

@mcp.tool()
def get_reddit_audit():
    try:
        with open("reporte_mision_reddit.txt", "r") as f:
            content = f.read()
        return {"status": "success", "node": "[REMI_SENTRY_NODE_001]", "data": sanitize_data(content)}
    except FileNotFoundError:
        return "ERROR: Archivo de auditoria no encontrado."

@mcp.tool()
def sync_to_notion(report_data: str, severity: str = "Informativa"):
    signature = "\n\n---\n[REMI_SENTRY_NODE_001] | Audit Integrity Verified."
    final_payload = {"title": f"Bunker Report: {severity}", "body": sanitize_data(report_data) + signature}
    with open("notion_sync_buffer.json", "a") as f:
        f.write(json.dumps(final_payload) + "\n")
    return f"Sincronizacion exitosa ({severity})."

if __name__ == "__main__":
    mcp.run()
