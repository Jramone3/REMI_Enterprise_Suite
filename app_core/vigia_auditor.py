import os
import subprocess
import time

HANGAR_PATH = os.path.expanduser("~/Escritorio/Proyecto_Remi_IA_App/AUDITORIAS")

CLIENTES_MAINNET = {
    "Cuenta_Notario_Principal": "0x6a8a000000000000000000000000000000006a8a", # Reemplaza con tu dirección real
    "LIDO": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "THE_GRAPH_GATEWAY": "0xc944e90c64b2c07662a292be6248bd0757398181",
    "THE_GRAPH_STAKING_L1": "0x296Ebf81430eA5561143B4b15B17CC3C549e2a53", # ESTE ES NUESTRO HALLAZGO
    "THRESHOLD": "0x33e18a092a93ff21ad04746c7da12e35d34dc7c4",
    "OPTIMISM": "0x25ace71c97B33Cc4729CF772ae268934F7ab57A1"
}

def sonda_on_chain():
    print(f"\n📡 [SONDA] Verificando integridad Mainnet...")
    # Tu clave personal de Alchemy queda integrada aquí
    RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/BnzsY8k4GQ9_QG3Q8eZ_7"
    
    for nombre, addr in CLIENTES_MAINNET.items():
        try:
            res = subprocess.check_output(
                ['cast', 'code', addr, '--rpc-url', RPC_URL], 
                text=True, 
                stderr=subprocess.DEVNULL,
                timeout=10
            )
            # Si recibimos bytecode, la integridad es correcta
            if len(res) > 10:
                print(f"✅ [ON-CHAIN] {nombre}: Integridad OK.")
            else:
                print(f"❌ [ALERTA] {nombre}: Contrato no encontrado o vacío.")
        except Exception:
            print(f"⚠️ [SONDA] {nombre}: Error de conexión con Alchemy.")

def escanear_bunker_recursivo():
    print(f"\n🛡️ [VIGÍA] Escaneando profundamente en {HANGAR_PATH}...")
    for root, dirs, files in os.walk(HANGAR_PATH):
        if "foundry.toml" in files and "lib" not in root:
            print(f"🔍 [AUDITORÍA] Tests en: {os.path.relpath(root, HANGAR_PATH)}")
            res = subprocess.run(['forge', 'test'], cwd=root, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"   ✅ PASSED")
            else:
                # Mostramos las últimas 5 líneas del error para entender qué pasa
                error_log = res.stderr.splitlines()[-5:]
                print(f"   🚨 FAILED: {root}")
                print(f"   ⚠️ Resumen de error: {error_log}")

if __name__ == "__main__":
    while True:
        escanear_bunker_recursivo()
        sonda_on_chain()
        print("\n⏳ [SENTRY] Ciclo finalizado. Espera de 24 horas.")
        time.sleep(86400)
