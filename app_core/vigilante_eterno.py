import time
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
addr = '0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7'
last_bal = w3.eth.get_balance(addr)
print(f"👀 OJO AVIZOR: Vigilando 3.78 ETH en {addr}")
while True:
    try:
        curr = w3.eth.get_balance(addr)
        if curr != last_bal:
            print(f"🚨 ¡MOVIMIENTO! Nuevo saldo: {w3.from_wei(curr, 'ether')} ETH")
            last_bal = curr
        time.sleep(10)
    except:
        pass
