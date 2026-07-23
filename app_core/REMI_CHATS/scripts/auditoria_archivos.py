import os
import time
from pathlib import Path

BASE_DIRS = [
    str(Path.home() / "Escritorio"),
    str(Path.home() / "Documentos"),
]

EXCLUDE_DIRS = [
    "node_modules",
    "__pycache__",
    ".git",
    ".cache",
    "BACKUP_REMI_20260328",
]

EXT_IMPORTANTES = {
    ".py", ".js", ".ts", ".json", ".md", ".sh",
    ".txt", ".env", ".yml", ".yaml"
}

REPORTE = Path.home() / "auditoria_remi_reporte.txt"

def es_excluida(ruta: str) -> bool:
    partes = ruta.split(os.sep)
    return any(e in partes for e in EXCLUDE_DIRS)

def scan():
    grandes = []
    por_ext = {}
    total_archivos = 0
    total_peso = 0

    for base in BASE_DIRS:
        for root, dirs, files in os.walk(base):
            if es_excluida(root):
                dirs[:] = []
                continue

            for f in files:
                try:
                    ruta = os.path.join(root, f)
                    size = os.path.getsize(ruta)
                    total_archivos += 1
                    total_peso += size

                    ext = os.path.splitext(f)[1].lower()
                    por_ext.setdefault(ext or "<sin_ext>", {"count": 0, "size": 0})
                    por_ext[ext or "<sin_ext>"]["count"] += 1
                    por_ext[ext or "<sin_ext>"]["size"] += size

                    if size > 200 * 1024 * 1024:  # > 200 MB
                        grandes.append((size, ruta))
                except Exception:
                    continue

    grandes.sort(reverse=True)

    with open(REPORTE, "w", encoding="utf-8") as r:
        r.write("🧾 AUDITORÍA DE ARCHIVOS REMI\n")
        r.write(f"Fecha: {time.ctime()}\n\n")
        r.write(f"Total de archivos escaneados: {total_archivos}\n")
        r.write(f"Peso total aproximado: {total_peso / (1024**3):.2f} GB\n\n")

        r.write("📂 Distribución por extensión:\n")
        for ext, data in sorted(por_ext.items(), key=lambda x: -x[1]["size"]):
            r.write(f"  {ext:10} -> {data['count']:6} archivos | {data['size'] / (1024**2):8.2f} MB\n")

        r.write("\n💣 ARCHIVOS MUY GRANDES (>200MB):\n")
        if not grandes:
            r.write("  Ninguno detectado.\n")
        else:
            for size, ruta in grandes:
                r.write(f"  {size / (1024**2):8.2f} MB  |  {ruta}\n")

    print(f"✅ Auditoría completada. Reporte en: {REPORTE}")

if __name__ == "__main__":
    scan()
