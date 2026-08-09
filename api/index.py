from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REMI Enterprise Suite - Nodo Operativo Vercel</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-center items-center p-6 font-sans">
    <div class="max-w-2xl w-full bg-slate-900 border border-cyan-500/30 rounded-2xl p-8 shadow-2xl text-center">
        <div class="inline-block px-4 py-1.5 rounded-full bg-cyan-950/80 text-cyan-400 text-xs font-mono mb-4 border border-cyan-800">
            🛡️ NODO BÚNKER EN VERCEL CLOUD · ONLINE
        </div>
        <h1 class="text-3xl font-bold mb-3 text-cyan-400">REMI Enterprise Suite</h1>
        <p class="text-slate-300 mb-6 text-sm">
            Inteligencia artificial soberana, segura y 100% optimizada. Los parámetros de infraestructura en Vercel han sido sincronizados con éxito.
        </p>
        <div class="bg-black/40 p-4 rounded-xl border border-slate-800 text-left font-mono text-xs text-cyan-300 mb-6 space-y-1">
            <p>✓ Estado: Despliegue Producción Activo</p>
            <p>✓ Motor: FastAPI Serverless Runtime</p>
            <p>✓ Pasarela: Licenciamiento Enterprise ($499 USD)</p>
        </div>
        <a href="https://github.com/Jramone3/REMI_Enterprise_Suite" target="_blank" class="inline-block bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-6 py-3 rounded-xl transition text-sm shadow-lg shadow-cyan-500/20">
            Ver Repositorio Oficial
        </a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return LANDING_HTML

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "environment": "vercel-production"}
