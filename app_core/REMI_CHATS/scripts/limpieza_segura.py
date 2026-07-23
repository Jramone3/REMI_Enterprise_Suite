import os
from pathlib import Path
import shutil

HOME = Path.home()

RUTAS_OBJETIVO = [
    HOME / ".npm",
    HOME / ".cache",
]

CARPETAS_RUIDO = [
    "node_modules",
    "__pycache__",
]

REPORTE_ACCIONES = HOME / "limpieza_remi_log.txt"

PROTEGIDAS = [
    "Proyecto_Remi_IA_App/REMI_CHATS",
    "Proyecto_Remi_IA_App/Documentos",
    "BACKUP_REMI_20260328",
]

def es_protegida(ruta: Path) -> bool:
    s = str(ruta)
    return any(p in s for p in PROTEGIDAS)

def limpiar_node_modules():
    acciones = []
    for base in [HOME]:
        for root, dirs, files in os.walk(base):
            root_p = Path(root)
            if es_protegida(root_p):
                continue
            for d in list(dirs):
                if d in CARPETAS_RUIDO:
                    target = root_p / d
                    try:
                        size = sum(
                            os.path.getsize(os.path.join(dp, f))
                            for dp, _, fs in os.walk(target)
                            for f in fs
                        )
                    except Exception:
                        size = 0
                    acciones.append((target, size))
    return acciones

def limpiar_rutas_objetivo():
    acciones = []
    for ruta in RUTAS_OBJETIVO:
        if ruta.exists():
            try:
                size = 0
                for dp, _, fs in os.walk(ruta):
                    for f in fs:
                        try:
                            size += os.path.getsize(os.path.join(dp, f))
                        except Exception:
                            continue
                acciones.append((ruta, size))
            except Exception:
                continue
    return acciones

def main():
    acciones = []
    acciones += limpiar_node_modules()
    acciones += limpiar_rutas_objetivo()

    if not acciones:
        print("✅ No se encontraron carpetas ruidosas para limpiar.")
        return

    with open(REPORTE_ACCIONES, "w", encoding="utf-8") as log:
        log.write("🧹 LIMPIEZA SEGURA REMI\n\n")
        for ruta, size in acciones:
            log.write(f"PENDIENTE: {ruta} | {size / (1024**2):.2f} MB\n")

    print("⚠️ MODO SECO (dry-run). No se ha borrado nada.")
    print(f"Revisa: {REPORTE_ACCIONES}")
    print("Si estás de acuerdo, edita este script y habilita el borrado real.")

if __name__ == "__main__":
    main()
