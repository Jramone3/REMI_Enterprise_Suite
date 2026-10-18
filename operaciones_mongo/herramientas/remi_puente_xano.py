import requests
import json

print("--- INTERROGADOR MAESTRO DEL PUENTE XANO (REMI v1.0.8) ---")

API_KEY = "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.P1UQ1yz0d25DpNQSamDrv7ArF9zeY5QyDWLgEslMTrEnt4CLvckCnl9k-hwGiUN0Hg2WMzBm6XX7KZxZ9_hl6UdDZT0PbhQs.OCbiM8omP5tFuhUs0TZG8g.l_HGVIvzKyTKOds6rYVTKYWhwEt_3bKN_iY9gWHN8oAAiqF6vcXIwRmXDTsJ4aPBUAj9uA2YAtbC4ZFlqvB-KHmF1cBp_LAJLRPapld1QKKgt8Vw0xtfbATPwckd1kYXYBL55bswmlt-3LA5OsFCBM3ozKf7RT_s1q3MIK3PZjs.KTXrlfjBwtrm8_terOc2Z_KvgUNLiDWkU7MPF-gJtB4"
URL = "https://x8ki-letl-twmt.n7.xano.io/api:b2tTjU9L/readme"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    print(f"📡 Estableciendo conexión soberana con el endpoint de Xano...")
    # Cambiamos a GET para solicitar la información que reside allá arriba
    response = requests.get(URL, headers=headers, timeout=10)
    
    # Si Xano requiere POST para leer, el script intentará ambos métodos automáticamente
    if response.status_code in [404, 405]:
        print("🔄 El endpoint requiere método POST para consulta. Reintentando...")
        response = requests.post(URL, headers=headers, json={}, timeout=10)

    print(f"📊 Código de respuesta del servidor: {response.status_code}")
    
    if response.status_code == 200:
        print("\n==================================================")
        print("        DOCUMENTACIÓN MAESTRA EXTRAÍDA DE XANO    ")
        print("==================================================")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        print("==================================================")
    else:
        print(f"\n⚠️ El servidor denegó el acceso directo o está vacío. Respuesta cruda:")
        print(response.text)

except Exception as e:
    print(f"\n❌ Error de red al intentar cruzar el puente: {e}")
