import subprocess
import os
import requests

AUDIT_DIR = "/home/ramon/REMI_CORE/core/auditoria_c/codigos_fuente"
LOG_REPORTE = "/home/ramon/REMI_CORE/core/auditoria_c/reporte_vulnerabilidades.log"

def ejecutar_cppcheck(ruta_proyecto):
    print(f"[REMI-C] Iniciando análisis estático de bajo nivel en: {ruta_proyecto}")
    try:
        resultado = subprocess.run(
            ["cppcheck", "--enable=all", "--inconclusive", "--std=c99", ruta_proyecto],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return resultado.stdout + resultado.stderr
    except Exception as e:
        return f"[ERROR] No se pudo ejecutar el análisis: {str(e)}"

def consultar_remi_cerebro(reporte_tecnico):
    url = "http://localhost:11434/api/chat"
    prompt = f"""
    Eres REMI, experto en ciberseguridad de sistemas y auditoría de código en C. 
    Analiza el siguiente reporte de errores de bajo nivel y código fuente. 
    Explica la falla de memoria o lógica y propón una refactorización segura y robusta (código perfecto sin fugas):
    
    {reporte_tecnico[:3000]}
    """
    
    payload = {
        "model": "llama3", # O tu modelo activo en Ollama
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["message"]["content"]
    return "[Error conectando con el cerebro de REMI]"

if __name__ == "__main__":
    if os.path.exists(AUDIT_DIR):
        analisis = ejecutar_cppcheck(AUDIT_DIR)
        print("[REMI-C] Análisis completado. Generando diagnóstico de REA...")
        diagnostico = consultar_remi_cerebro(analisis)
        
        with open(LOG_REPORTE, "w") as f:
            f.write(diagnostico)
        print(f"[REMI-C] Diagnóstico guardado en {LOG_REPORTE}")
    else:
        print(f"[AVISO] El directorio de código fuente {AUDIT_DIR} no existe.")
