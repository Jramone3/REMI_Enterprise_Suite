from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REMI Enterprise Suite v1.0.0 - AI Soberana y 100% Local</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Geist', sans-serif; background-color: #030712; color: #f3f4f6; }
        .neon-glow { text-shadow: 0 0 20px rgba(0, 242, 254, 0.5); }
        .border-neon { border-color: rgba(0, 242, 254, 0.4); box-shadow: 0 0 15px rgba(0, 242, 254, 0.15); }
    </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-cyan-500 selection:text-black">
    <header class="border-b border-cyan-900/40 bg-black/60 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-cyan-400 rounded-full animate-ping"></div>
            <span class="font-bold text-lg tracking-wider text-cyan-400">REMI_BUNKER.SYS</span>
        </div>
        <div class="flex items-center space-x-4">
            <span class="text-xs px-3 py-1 rounded bg-cyan-950/80 border border-cyan-800 text-cyan-300 font-mono">v1.0.0 ENTERPRISE</span>
            <a href="https://github.com/Jramone3/REMI_Enterprise_Suite" target="_blank" class="text-sm bg-gray-900 hover:bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg transition">GitHub</a>
        </div>
    </header>

    <main class="flex-1 max-w-6xl mx-auto px-6 py-16 flex flex-col items-center text-center">
        <div class="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-mono mb-8">
            <span>🛡️ Ciberseguridad y Soberanía Local Garantizada</span>
        </div>
        
        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight max-w-4xl mb-6 leading-tight">
            Inteligencia Artificial Soberana, Segura y <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 neon-glow">100% Local</span> para tu Empresa
        </h1>
        
        <p class="text-lg md:text-xl text-gray-400 max-w-2xl mb-10 font-light">
            Despliega agentes autónomos y herramientas de auditoría en tu propia infraestructura (Windows, macOS y Linux) sin pagar tarifas por token ni arriesgar la confidencialidad de tus datos.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 mb-16">
            <a href="https://sourceforge.net" target="_blank" class="bg-cyan-500 hover:bg-cyan-400 text-black font-semibold px-8 py-3.5 rounded-xl transition shadow-lg shadow-cyan-500/20">
                Descargar Paquete Firmado (SourceForge)
            </a>
            <a href="#licenciamiento" class="bg-gray-900 hover:bg-gray-800 text-cyan-400 border border-cyan-800/60 font-semibold px-8 py-3.5 rounded-xl transition">
                Adquirir Licencia Enterprise ($499 USD)
            </a>
        </div>

        <div class="w-full max-w-4xl bg-gray-900/80 border border-neon rounded-2xl p-8 mb-16 text-left relative overflow-hidden">
            <div class="absolute top-0 right-0 bg-cyan-500/10 text-cyan-400 text-xs font-mono px-4 py-1.5 rounded-bl-xl border-l border-b border-cyan-800/50">
                NODO OPERATIVO · PUERTO 8000
            </div>
            <div class="flex flex-col md:flex-row items-center gap-6">
                <div class="w-24 h-24 rounded-full bg-cyan-950 border-2 border-cyan-400/80 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/20">
                    <span class="text-3xl">🤖</span>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-cyan-400 mb-2">Núcleo Interactivo de Remi</h3>
                    <p class="text-gray-300 text-sm leading-relaxed mb-4">
                        "Saludos. Soy Remi, el núcleo de agentes autónomos de REMI Enterprise Suite. Operando de forma 100% local bajo FastAPI y Uvicorn en el puerto 8000. Cero fugas de datos, cifrado SQLite/JSON y cero tarifas por token."
                    </p>
                    <div class="flex flex-wrap gap-2 text-xs font-mono text-cyan-300">
                        <span class="bg-black/40 px-2.5 py-1 rounded border border-cyan-900">GET /api/v1/health</span>
                        <span class="bg-black/40 px-2.5 py-1 rounded border border-cyan-900">POST /api/v1/agent/run</span>
                        <span class="bg-black/40 px-2.5 py-1 rounded border border-cyan-900">POST /api/v1/license/verify</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="pilares" class="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl mb-16">
            <div class="bg-gray-900/50 border border-gray-800 p-6 rounded-xl text-left">
                <h3 class="text-cyan-400 font-bold mb-2">⚖️ Bufetes Legales</h3>
                <p class="text-sm text-gray-400">Confidencialidad absoluta y cumplimiento estricto del secreto profesional mediante procesamiento estrictamente on-premise.</p>
            </div>
            <div class="bg-gray-900/50 border border-gray-800 p-6 rounded-xl text-left">
                <h3 class="text-cyan-400 font-bold mb-2">📈 Consultoras Financieras</h3>
                <p class="text-sm text-gray-400">Soberanía de datos y reducción de hasta un 70% en costos operativos al eliminar las tarifas por token en la nube.</p>
            </div>
            <div class="bg-gray-900/50 border border-gray-800 p-6 rounded-xl text-left">
                <h3 class="text-cyan-400 font-bold mb-2">⚙️ PYMES de Ingeniería</h3>
                <p class="text-sm text-gray-400">Autonomía operativa 24/7 sin dependencia de internet constante ni caídas imprevistas de servidores externos.</p>
            </div>
            <div class="bg-gray-900/50 border border-gray-800 p-6 rounded-xl text-left">
                <h3 class="text-cyan-400 font-bold mb-2">🏫 Comercios y Academias</h3>
                <p class="text-sm text-gray-400">Herramientas internas de auditoría avanzada, control transaccional seguro y enseñanza técnica en ciberseguridad.</p>
            </div>
        </div>

        <div id="licenciamiento" class="w-full max-w-4xl bg-gradient-to-b from-gray-900 to-black border border-cyan-900/50 rounded-2xl p-8 text-center">
            <h2 class="text-2xl font-bold mb-3 text-cyan-300">Pasarela Enterprise & Licenciamiento ($499 USD / Año)</h2>
            <p class="text-gray-400 text-sm mb-6">Modelo de negocio anual corporativo con pagos descentralizados vía Red Base (EOA Contract).</p>
            <div class="max-w-md mx-auto flex flex-col gap-3">
                <input type="email" placeholder="correo@corporativo.com" class="bg-black border border-gray-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-500">
                <input type="text" placeholder="Hash de Transacción (TxID)" class="bg-black border border-gray-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-500">
                <button class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-3 rounded-lg transition text-sm">Generar Clave de Licencia</button>
            </div>
        </div>
    </main>

    <footer class="border-t border-gray-900 py-6 text-center text-xs text-gray-500">
        REMI Enterprise Suite © 2026 — Desarrollado por jramonrivasg (remi.bunker.sys)
    </footer>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_landing():
    return LANDING_PAGE_HTML

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "node": "remi-bunker", "port": 8000, "security": "100% on-premise"}

