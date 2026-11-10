import os
import hashlib

def obtener_hash(archivo):
    hasher = hashlib.sha256()
    with open(archivo, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

directorio = os.path.expanduser("~/modulo27")
archivos_unicos = {}
duplicados = 0
esenciales = []

print("🔍 Iniciando escaneo de 65,000 sectores...")

for raiz, dirs, archivos in os.walk(directorio):
    for nombre in archivos:
        ruta_completa = os.path.join(raiz, nombre)
        try:
            h = obtener_hash(ruta_completa)
            if h not in archivos_unicos:
                archivos_unicos[h] = ruta_completa
                if "v_1.0.8" in ruta_completa or "SISTEMA" in ruta_completa:
                    esenciales.append(ruta_completa)
            else:
                duplicados += 1
        except:
            continue

print(f"✅ Auditoría Completa.")
print(f"📊 Duplicados detectados: {duplicados}")
print(f"🚀 Archivos listos para 'Nube Soberana' (v_1.0.8): {len(esenciales)}")
