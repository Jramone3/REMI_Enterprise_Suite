import requests

llaves = [
    "f0d4f993d117ee86b9a6c8d0e5232d795a08db1bc4c14044ed54feba94ab2485",
    "4ba76f707dbf0af5ceaae9aefc3656916ec8da1b5c864209b84c2bd16141d329",
    "d753e1b8de69ec9e240327cd5289c9ca6d9e521e5bd4fdee2ac5b4e85303cba2",
    "66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb",
    "d6833748595f9f6b12ab9dcd165886f8f7a9970e3a6e49a6face8196a83ab288",
    "c83dc511057bfebcfe4120d2199dfe47c83c633e4a7123e6b0d7b24b1a44db96"
]

from eth_account import Account

# RPC público de Base
RPC_URL = "https://mainnet.base.org"

print("📡 Verificando saldos en la red BASE...")

for pk in llaves:
    acct = Account.from_key(pk)
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [acct.address, "latest"],
        "id": 1
    }
    try:
        response = requests.post(RPC_URL, json=payload).json()
        balance_wei = int(response['result'], 16)
        balance_eth = balance_wei / 10**18
        if balance_eth > 0:
            print(f"💰 ¡ORO ENCONTRADO! | Dir: {acct.address} | Saldo: {balance_eth} ETH")
            print(f"🔑 Private Key: {pk}")
        else:
            print(f"❌ Vacía: {acct.address}")
    except:
        print(f"⚠️ Error consultando {acct.address}")
