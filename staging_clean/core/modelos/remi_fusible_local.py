#!/usr/bin/env python3
import requests
import json
import os

URL_XANO = "https://x8ki-letl-twmt.n7.xano.io/api:b2tTjU9L/readme"
API_KEY = "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.P1UQ1yz0d25DpNQSamDrv7ArF9zeY5QyDWLgEslMTrEnt4CLvckCnl9k-hwGiUN0Hg2WMzBm6XX7KZxZ9_hl6UdDZT0PbhQs.OCbiM8omP5tFuhUs0TZG8g.l_HGVIvzKyTKOds6rYVTKYWhwEt_3bKN_iY9gWHN8oAAiqF6vcXIwRmXDTsJ4aPBUAj9uA2YAtbC4ZFlqvB-KHmF1cBp_LAJLRPapld1QKKgt8Vw0xtfbATPwckd1kYXYBL55bswmlt-3LA5OsFCBM3ozKf7RT_s1q3MIK3PZjs.KTXrlfjBwtrm8_terOc2Z_KvgUNLiDWkU7MPF-gJtB4"

print("📡 [FUSIBLE DE EMERGENCIA]: Verificando estado del canal soberano...")

headers = {"Authorization": f"Bearer {API_KEY}"}

try:
    response = requests.get(URL_XANO, headers=headers, timeout=5)
    if response.status_code == 200:
        print("🟢 [MODO ONLINE]: El puente Xano está respondiendo con éxito. Inferencia principal delegada a Gemini 2.5 Flash.")
    else:
        print(f"⚠️ [ALERTA DE CANAL - Status {response.status_code}]: Respuesta anómala en la nube.")
        print("🔄 Conmutando al motor interno: REMI activará discernimiento básico en sda5 (Phi-3/TinyLlama local).")
except Exception as e:
    print("🚨 [CORTE DE RED DETECTADO]: No hay conexión con el proxy de Xano.")
    print("🛡️ [FUSIBLE ACTIVADO]: Activando modo contingencia offline para tareas de mantenimiento local.")
