from eth_account import Account

llaves = [
    "f0d4f993d117ee86b9a6c8d0e5232d795a08db1bc4c14044ed54feba94ab2485",
    "4ba76f707dbf0af5ceaae9aefc3656916ec8da1b5c864209b84c2bd16141d329",
    "d753e1b8de69ec9e240327cd5289c9ca6d9e521e5bd4fdee2ac5b4e85303cba2",
    "66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb",
    "d6833748595f9f6b12ab9dcd165886f8f7a9970e3a6e49a6face8196a83ab288",
    "c83dc511057bfebcfe4120d2199dfe47c83c633e4a7123e6b0d7b24b1a44db96"
]

objetivo = "0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86".lower()

print(f"🔎 Comprobando {len(llaves)} llaves contra el objetivo...")

for pk in llaves:
    try:
        acct = Account.from_key(pk)
        print(f"Dirección generada: {acct.address}")
        if acct.address.lower() == objetivo:
            print(f"\n🎯 ¡BINGO! LA LLAVE ES: {pk}")
            break
    except Exception as e:
        print(f"Error con llave {pk[:10]}...: {e}")
