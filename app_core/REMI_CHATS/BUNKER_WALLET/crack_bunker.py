import subprocess
import itertools
import sys

archivo_gpg = "llave_para_cifrar.txt.gpg"

# Componentes clave que sabemos que usas
palabras = ["BUNKER", "ALPHA", "ARAGUA", "REMI", "CORE"]
anios = ["2025", "2026"]
separadores = ["_", "-", "", " "]

def probar_clave(passphrase):
    cmd = ["gpg", "--batch", "--yes", "--passphrase", passphrase, "-d", archivo_gpg]
    proceso = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proceso.returncode == 0:
        print(f"\n[¡ÉXITO!] Clave encontrada: {passphrase}")
        print("Contenido de la llave:")
        print(proceso.stdout)
        return True
    return False

# 1. Probar variaciones directas de la que recuerdas
variantes_directas = [
    "BUNKER_ALPHA_2026", "bunker_alpha_2026", "Bunker_Alpha_2026",
    "BUNKER_ALPHA2026", "BUNKER_ARAGUA_2026", "ARAGUA_BUNKER_2026",
    "BUNKER_ALPHA_2025", "bunker_alpha_2025", "BUNKER_ALPHA2025"
]

print("--> Fase 1: Probando variantes directas conocidas...")
for clave in variantes_directas:
    if probar_clave(clave):
        sys.exit(0)

# 2. Generar permutaciones inteligentes si la fase 1 falla
print("--> Fase 2: Ejecutando permutador lógico...")
for p in itertools.permutations(palabras, 2):
    for sep in separadores:
        for anio in anios:
            # Combinaciones tipo PALABRA1_PALABRA2_ANIO
            clave1 = f"{p[0]}{sep}{p[1]}{sep}{anio}"
            clave2 = f"{p[0].lower()}{sep}{p[1].lower()}{sep}{anio}"
            
            if probar_clave(clave1) or probar_clave(clave2):
                sys.exit(0)

print("\n[Fin] No se encontró la clave en este set de variaciones.")
