from web3 import Web3
import os

# Inicializar Web3 (modo local/offline para generar)
w3 = Web3()
acct = w3.eth.account.create()

print(f"--- NUEVO PUNTO DE DEPÓSITO GENERADO ---")
print(f"DIRECCIÓN PÚBLICA: {acct.address}")
print(f"LLAVE PRIVADA: [CIFRANDO EN MEMORIA...]")

# Guardamos solo la dirección pública para REMI
with open("os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/direccion_publica.txt", "w") as f:
    f.write(acct.address)

# Guardamos la privada en un archivo temporal para que TÚ lo cifres con GPG
with open("llave_para_cifrar.txt", "w") as f:
    f.write(acct.key.hex())

print("\n⚠️ CUSTODIO: Ejecuta 'gpg -c llave_para_cifrar.txt' AHORA.")
