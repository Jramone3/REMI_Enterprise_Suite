import time

# Datos de la operacion
hash_atrapado = "0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172"
codigo_correcto = "9001" # Ethereum Mainnet

# Creamos un mensaje que el indexador de Orbiter pueda reconocer
# El formato suele ser: [Prefijo][Codigo][Hash]
mensaje_hex = f"0x6f726269746572{codigo_correcto}{hash_atrapado[2:]}"

print(f"\n🚀 [REMI]: Preparando señal de rescate...")
print(f"📡 Mensaje Hexadecimal a enviar:")
print(f"\033[1;32m{mensaje_hex}\033[0m")
print("\n--- INSTRUCCIONES ---")
print("1. Abre tu billetera (Metamask/Rabby) en la red BASE.")
print("2. Envía 0 ETH a la dirección de Orbiter: 0xe4EdB277e4122137966efc68615b3c5890d2979E")
print("3. En 'Datos Hexadecimales' o 'Hex Data', pega el código verde de arriba.")
print("4. Confirma la transacción (costará menos de $0.01).")
