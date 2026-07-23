import os
import json
from pathlib import Path
import time

BASE_DIRS = [
    str(Path.home() / "Escritorio"),
    str(Path.home() / "Documentos"),
]

EXT_CODIGO = {".py", ".js", ".ts", ".json", ".sh", ".yml", ".yaml"}
EXT_DOCS = {".md", ".txt", ".pdf", ".odt", ".docx"}
EXT_MEDIA = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".mp3", ".wav"}

EXCLUDE_DIRS = [
    "node_modules",
    "__pycache__",
    ".git",
    ".cache",
    "BACKUP_REMI_20260328",
]

SALIDA_JSON = Path.home() / "clasificacion_remi.json"

def es_excluida(ruta: str) -> bool:
    partes = ruta.split(os.sep)
    return any(e in partes for e in EXCLUDE_DIRS)

def clasificar():
    data = {
        "codigo": [],
        "documentos": [],
        "media": [],
        "otros": [],
    }

    for base in BASE_DIRS:
        for root, dirs, files in os.walk(base):
            if es_excluida(root):
                dirs[:] = []
                continue

            for f in files:
                ruta = os.path.join(root, f)
                ext = os.path.splitext(f)[1].lower()
                try:
                    size = os.path.getsize(ruta)
                except Exception:
                    size = 0

                item = {
                    "ruta": ruta,
                    "ext": ext or "<sin_ext>",
                    "size_mb": round(size / (1024**2), 2),
                }

                if ext in EXT_CODIGO:
                    data["codigo"].append(item)
                elif ext in EXT_DOCS:
                    data["documentos"].append(item)
                elif ext in EXT_MEDIA:
                    data["media"].append(item)
                else:
                    data["otros"].append(item)

    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {
                "fecha": time.ctime(),
                "resumen": {
                    "codigo": len(data["codigo"]),
                    "documentos": len(data["documentos"]),
                    "media": len(data["media"]),
                    "otros": len(data["otros"]),
                },
                "detalle": data,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"✅ Clasificación completada. Archivo: {SALIDA_JSON}")

if __name__ == "__main__":
    clasificar()
