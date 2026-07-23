import re
import os

# Buscamos cadenas de 64 caracteres hexadecimales (Private Keys)
pattern = re.compile(r'\b[a-fA-F0-9]{64}\b')
ruta = os.path.expanduser('~/Escritorio/Proyecto_Remi_IA_App/')

print(f"🚀 Iniciando barrido profundo en {ruta}...")

for root, dirs, files in os.walk(ruta):
    for file in files:
        if file.endswith(('.js', '.html', '.txt', '.json', '.log')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    for match in matches:
                        # Filtramos hashes comunes de ceros o fff
                        if match.lower() not in ['0'*64, 'f'*64]:
                            print(f"🔥 POSIBLE LLAVE: {match} | ORIGEN: {file}")
            except Exception:
                pass
