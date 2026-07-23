from flask import Flask
import os
import datetime

app = Flask(__name__)

# Ruta al log de producción definido en el Corpus
LOG_PATH = "os.path.expanduser("~/") + REMI_CORE/oro_finance/registros/produccion_remi.log"

@app.route('/')
def home():
    contenido_log = "Esperando sincronización con MOTOR_GLOBAL..."
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                lineas = f.readlines()
                # Extraemos las últimas 15 líneas para el dashboard
                contenido_log = "".join(lineas[-15:])
        except Exception as e:
            contenido_log = f"Error leyendo log: {e}"

    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>REMI CORE v2026 - MONITOR</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ background-color: #050505; color: #00ff41; font-family: 'Consolas', monospace; padding: 20px; }}
            .container {{ 
                max-width: 1000px; margin: auto; border: 1px solid #00ff41; 
                padding: 20px; background: rgba(0, 255, 65, 0.05); 
                box-shadow: 0 0 30px rgba(0, 255, 65, 0.1);
            }}
            .header {{ text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 15px; margin-bottom: 20px; }}
            .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }}
            .stat-card {{ border: 1px solid #333; padding: 10px; text-align: center; background: #000; }}
            .label {{ font-size: 0.7em; color: #888; text-transform: uppercase; }}
            .value {{ font-size: 1.2em; color: #fff; margin-top: 5px; }}
            pre {{ 
                background: #000; padding: 15px; border: 1px solid #00ff41; 
                color: #00ff41; font-size: 0.85em; height: 400px; 
                overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;
            }}
            .footer {{ margin-top: 15px; font-size: 0.75em; color: #444; text-align: right; }}
            .blink {{ animation: blinker 1.5s linear infinite; }}
            @keyframes blinker {{ 50% {{ opacity: 0; }} }}
            h1 {{ letter-spacing: 10px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>REMI CAPACITOR</h1>
                <div style="color: #fff; font-size: 0.8em;">SISTEMA PATRIMONIAL AUT&Oacute;NOMO v2026</div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="label">Estado</div>
                    <div class="value blink" style="color: #00ff41;">LIVE</div>
                </div>
                <div class="stat-card">
                    <div class="label">Red Principal</div>
                    <div class="value">BASE (Chain 8453)</div>
                </div>
                <div class="stat-card">
                    <div class="label">Hardware</div>
                    <div class="value">Intel i5-650</div>
                </div>
            </div>

            <div class="label" style="margin-bottom: 5px;">>_ Terminal_Output (produccion_remi.log)</div>
            <pre>{contenido_log}</pre>

            <div class="footer">
                Sincronizaci&oacute;n: {ahora} | Puerto: 5000 | Modo: REMI_SENSING_ORO
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    # Ejecución en red local
    app.run(host='0.0.0.0', port=5001)
