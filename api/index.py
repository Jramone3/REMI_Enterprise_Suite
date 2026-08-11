from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from gtts import gTTS
import io

app = FastAPI(title="REMI Enterprise Suite", version="1.0.0")

@app.get("/api/v1/tts")
def text_to_speech(text: str = "Saludos Custodio.", lang: str = "es"):
    try:
        # Generar audio al vuelo en memoria RAM (evita problemas de escritura en disco en Vercel)
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(content=fp.read(), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REMI Enterprise Suite - IA Soberana y 100% Local</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-black">
    <header class="border-b border-cyan-900/40 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-cyan-400 rounded-full animate-ping"></div>
            <span class="font-bold text-lg tracking-wider text-cyan-400 font-mono">REMI_BUNKER.SYS</span>
        </div>
        <div class="flex items-center space-x-4">
            <span class="text-xs px-3 py-1 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono">v1.0.0 ENTERPRISE</span>
            <a href="https://github.com/Jramone3/REMI_Enterprise_Suite" target="_blank" class="text-sm bg-slate-900 hover:bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg transition">GitHub</a>
        </div>
    </header>

    <main class="flex-1 max-w-5xl mx-auto px-6 py-16 flex flex-col items-center text-center">
        <div class="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-mono mb-8">
            <span>🛡️ Ciberseguridad y Soberanía Local Garantizada · Vercel Cloud Native</span>
        </div>
        
        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight max-w-4xl mb-6 leading-tight">
            Inteligencia Artificial Soberana, Segura y <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">100% Local</span> para tu Empresa
        </h1>
        
        <p class="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 font-light">
            Despliega agentes autónomos y herramientas de auditoría en tu propia infraestructura sin pagar tarifas por token ni arriesgar la confidencialidad de tus datos.
        </p>

        <div class="w-full max-w-3xl bg-slate-900/90 border border-cyan-500/30 rounded-2xl p-8 mb-16 text-left relative shadow-2xl">
            <div class="absolute top-0 right-0 bg-cyan-500/10 text-cyan-400 text-xs font-mono px-4 py-1.5 rounded-bl-xl border-l border-b border-cyan-800/50">
                ESTADO: ONLINE (DYNAMIC TTS STREAM)
            </div>
            <div class="flex items-center gap-6">
                <div class="w-20 h-20 rounded-full bg-cyan-950 border-2 border-cyan-400/80 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/20">
                    <span class="text-3xl">🤖</span>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-cyan-400 mb-2">Núcleo Interactivo de Remi</h3>
                    <p id="remi-msg" class="text-slate-300 text-sm leading-relaxed mb-4">
                        "Saludos Custodio. Nodo operativo sincronizado correctamente. Operando en modo bilingüe y dinámico."
                    </p>
                    <div class="flex flex-wrap gap-3">
                        <button onclick="reproducirDinamico('es')" class="bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-700/60 text-xs px-4 py-2 rounded-lg font-mono transition flex items-center gap-2">
                            🇪🇸 Escuchar voz dinámica (Español)
                        </button>
                        <button onclick="reproducirDinamico('en')" class="bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-700/60 text-xs px-4 py-2 rounded-lg font-mono transition flex items-center gap-2">
                            🇺🇸 Listen dynamic voice (English)
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        REMI Enterprise Suite © 2026 — Desarrollado por jramonrivasg (remi.bunker.sys)
    </footer>

    <script>
        function reproducirDinamico(lang) {
            const texto = lang === 'en' 
                ? "Greetings Custodian. Operational node synchronized successfully with dynamic backend." 
                : document.getElementById("remi-msg").innerText;
            
            const audioUrl = `/api/v1/tts?text=${encodeURIComponent(texto)}&lang=${lang}`;
            const audio = new Audio(audioUrl);
            audio.play().catch(err => {
                console.error("Error al reproducir audio dinámico:", err);
                alert("Haz clic en la página primero para habilitar el audio.");
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return LANDING_HTML

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "runtime": "vercel-dynamic-tts", "bunker": "synchronized"}
