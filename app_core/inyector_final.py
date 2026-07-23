import subprocess
import json

# Datos del contrato y red
CONTRACT = "SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2"
KEY = "f0d4f993d117ee86b9a6c8d0e5232d795a08db1bc4c14044ed54feba94ab2485"
NONCE = 25917
FEE = 6000000

# Formateo del argumento complejo para el primer bin
# Estructura: (list (tuple (amount) (bin-id) (min-x) (min-y) (pool) (x-token) (y-token)))
args = '[{ amount: u98932202, bin-id: -159, min-x-amount: u343850625, min-y-amount: u0, pool-trait: "SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.stx-velar-v1", x-token-trait: "SP1Y5YST0XSHR7V55P6S7235TSB96QXK92P864835.stx-token", y-token-trait: "SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.velar-token" }]'

cmd = f'stx call_contract_func {CONTRACT.replace(".", " ")} withdraw-liquidity-multi {FEE} {NONCE} {KEY} \'{args}\''

print(f"🚀 Ejecutando extracción de Bin -159...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
