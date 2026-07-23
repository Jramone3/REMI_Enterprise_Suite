import ccxt
import datetime

def escanear_polvo_real():
    # Usamos Binance y Kraken, que son más estables para acceso público
    exchanges = {
        'binance': ccxt.binance(),
        'kraken': ccxt.kraken()
    }
    precios = {}
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    ruta_log = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/bitacora_limpieza.txt"

    try:
        for nombre, ex in exchanges.items():
            ticker = ex.fetch_ticker('BTC/USDT')
            precios[nombre] = ticker['last']
        
        p_binance = precios['binance']
        p_kraken = precios['kraken']
        dif = abs(p_binance - p_kraken)

        reporte = f"[{ts}] SCAN: Binance:{p_binance} | Kraken:{p_kraken} | DIF: {dif:.2f}\n"
        
        with open(ruta_log, "a") as f:
            if dif > 0.50:
                f.write(f"✨ POLVO DETECTADO: {reporte}")
                print(f"✨ ¡DIFERENCIA DETECTADA! {dif:.2f} USD")
            else:
                f.write(reporte)
                print(f"✅ Escaneo limpio: Dif {dif:.2f}")
                
    except Exception as e:
        print(f"⚠️ Error en la red: {e}")

if __name__ == "__main__":
    print("🧹 ASPIRADORA CCXT (V2): Iniciando descontaminación...")
    escanear_polvo_real()
