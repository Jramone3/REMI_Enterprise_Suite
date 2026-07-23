import subprocess
import itertools
import os

# 1. Definimos las raíces reales basadas en tus logs
raices = ['jrrg', 'remi', 'bunker', '2026', 'code', 'zero']
conectores = ['', '*', '.', '_']

# Generar variaciones de capitalización (ej: remi, Remi, REMI)
def obtener_variaciones(palabra):
    if palabra.isdigit():
        return [palabra]
    return list(set([palabra.lower(), palabra.capitalize(), palabra.upper()]))

# Expandir la lista con sus variantes de mayúsculas
componentes_mutados = []
for r in raices:
    componentes_mutados.append(obtener_variaciones(r))

# Combinar todas las variaciones posibles
palabras_candidatas = list(itertools.product(*componentes_mutados))

archivo_gpg = os.path.expanduser("~/Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/llave_para_cifrar.txt.gpg")
salida_tmp = "/tmp/llave_desencriptada.txt"

print("🛰️  REMI LOCALHOST: Iniciando motor de permutación sobre el i5...")
print("🎯 Analizando combinaciones lógicas de raíces y conectores...\n")

intento = 0
exito = False

# Probar combinaciones de 2 y 3 palabras raíz combinadas
for r_combinacion in range(2, 4):
    if exito: break
    for combo in itertools.permutations(raices, r_combinacion):
        if exito: break
        
        # Obtener todas las formas de capitalizar este combo específico
        combos_capitalizados = itertools.product(*[obtener_variaciones(p) for p in combo])
        
        for c_cap in combos_capitalizados:
            if exito: break
            
            # Probar diferentes conectores entre las palabras y al final
            for con in conectores:
                intento += 1
                
                # Variante 1: Pegadas con conector intermedio (ej: Remi*Bunker)
                clave_intento = con.join(c_cap)
                
                # Variante 2: Raíces pegadas + conector al final (ej: RemiBunker2026*)
                clave_intento_final = "".join(c_cap) + con
                
                for clave in [clave_intento, clave_intento_final]:
                    # Comando silencioso para interactuar con el binario de GPG
                    cmd = f"echo '{clave}' | gpg --batch --yes --passphrase-fd 0 -d '{archivo_gpg}' 2>/dev/null"
                    
                    resultado = subprocess.run(cmd, shell=True, capture_output=True)
                    
                    if resultado.returncode == 0:
                        print(f"\n🔓 ¡ÉXITO TOTAL EN EL INTENTO {intento}!")
                        print(f"🔑 CONTRASEÑA ENCONTRADA: {clave}")
                        print(f"📄 Guardando llave plana en: {salida_tmp}")
                        
                        # Escribimos el texto plano recuperado
                        with open(salida_tmp, "wb") as f:
                            f.write(resultado.stdout)
                        
                        exito = True
                        break
                
                if intento % 500 == 0:
                    print(f"⚡ Procesados {intento} intentos... Buscando...")

if not exito:
    print(f"\n⚠️  Bucle terminado. Se probaron {intento} variaciones lógicas sin éxito.")
    print("💡 Si recuerdas otra palabra clave vieja, la añadimos al array de raíces.")
