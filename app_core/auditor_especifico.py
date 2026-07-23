from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://base-mainnet.public.blastapi.io"))
target = "0x3d126d6B1581f7566a34bD4e912920bBA41367D5"

print(f"\n--- AUDITANDO HALLAZGO: {target} ---")
balance = w3.eth.get_balance(target)
code = w3.eth.get_code(target).hex()

print(f"Saldo actual: {w3.from_wei(balance, 'ether')} ETH")
if "f2c42696" in code: # Selector de 'distribute' o 'withdraw'
    print("⚠️ ¡ALERTA! El contrato tiene funciones de retiro expuestas.")
else:
    print("[-] No se detectan funciones de retiro simples en el código superficial.")

# Verificamos si es un contrato verificado o código crudo
print(f"Longitud del Código: {len(code)}")
