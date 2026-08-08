from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REMI Enterprise Suite v1.0.0 - AI Soberana</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex flex-col justify-center items-center p-6">
    <div class="max-w-3xl w-full bg-gray-900 border border-cyan-500/40 rounded-2xl p-8 shadow-2xl text-center">
        <div class="inline-block px-4 py-1.5 rounded-full bg-cyan-950 text-cyan-400 text-xs font-mono mb-4 border border-cyan-800">
            🛡️ BÚNKERO OPERATIVO · VERCEL CLOUD
        </div>
        <h1 class="text-3xl font-bold mb-4 text-cyan-400">REMI Enterprise Suite v1.0.0</h1>
        <p class="text-gray-300 mb-6 text-sm">
            La inteligencia artificial soberana y 100% local está desplegada y conectada de forma segura.
        </p>
        <div class="bg-black/50 p-4 rounded-xl border border-gray-800 text-left font-mono text-xs text-cyan-300 mb-6">
            <p> Estado del Nodo: ONLINE</p>
            <p> Seguridad: Encriptación On-Premise Activa</p>
            <p> Licenciamiento: Pasarela Red Base ($499 USD)</p>
        </div>
        <a href="https://github.com/Jramone3/REMI_Enterprise_Suite" target="_blank" class="inline-block bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-6 py-3 rounded-xl transition text-sm">
            Ver Repositorio en GitHub
        </a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "system": "REMI Enterprise Suite"}
