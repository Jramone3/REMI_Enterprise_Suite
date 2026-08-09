from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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

        <div class="flex flex-col sm:flex-row gap-4 mb-16">
            <a href="https://github.com/Jramone3/REMI_Enterprise_Suite" target="_blank" class="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-8 py-3.5 rounded-xl transition shadow-lg shadow-cyan-500/20">
                Ver Repositorio Oficial
            </a>
            <a href="#licenciamiento" class="bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-cyan-800/60 font-semibold px-8 py-3.5 rounded-xl transition">
                Licenciamiento Enterprise ($499 USD)
            </a>
        </div>

        <div class="w-full max-w-3xl bg-slate-900/90 border border-cyan-500/30 rounded-2xl p-8 mb-16 text-left relative shadow-2xl">
            <div class="absolute top-0 right-0 bg-cyan-500/10 text-cyan-400 text-xs font-mono px-4 py-1.5 rounded-bl-xl border-l border-b border-cyan-800/50">
                ESTADO: ONLINE
            </div>
            <div class="flex items-center gap-6">
                <div class="w-20 h-20 rounded-full bg-cyan-950 border-2 border-cyan-400/80 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/20">
                    <span class="text-3xl">🤖</span>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-cyan-400 mb-2">Núcleo Interactivo de Remi</h3>
                    <p id="remi-msg" class="text-slate-300 text-sm leading-relaxed mb-4">
                        "Saludos Custodio. Nodo operativo sincronizado correctamente. Operando en modo bilingüe y sin fugas de datos."
                    </p>
                    <div class="flex flex-wrap gap-3">
                        <button onclick="hablarRemi('es')" class="bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-700/60 text-xs px-4 py-2 rounded-lg font-mono transition flex items-center gap-2">
                            🇪🇸 Escuchar en Español
                        </button>
                        <button onclick="hablarRemi('en')" class="bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-700/60 text-xs px-4 py-2 rounded-lg font-mono transition flex items-center gap-2">
                            🇺🇸 Listen in English
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div id="licenciamiento" class="w-full max-w-3xl bg-gradient-to-b from-slate-900 to-slate-950 border border-cyan-900/50 rounded-2xl p-8 text-center">
            <h2 class="text-2xl font-bold mb-3 text-cyan-300">Pasarela Enterprise ($499 USD / Año)</h2>
            <p class="text-slate-400 text-sm mb-6">Modelo de negocio anual corporativo con pagos descentralizados vía Red Base.</p>
            <div class="max-w-md mx-auto flex flex-col gap-3">
                <input type="email" placeholder="correo@corporativo.com" class="bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-500 text-slate-200">
                <input type="text" placeholder="Hash de Transacción (TxID)" class="bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-500 text-slate-200">
                <button class="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold py-3 rounded-lg transition text-sm">Generar Clave de Licencia</button>
            </div>
        </div>
    </main>

    <footer class="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        REMI Enterprise Suite © 2026 — Desarrollado por jramonrivasg (remi.bunker.sys)
    </footer>

    <script>
        function hablarRemi(lang) {
            if (!('speechSynthesis' in window)) {
                alert("Tu navegador no soporta síntesis de voz.");
                return;
            }

            window.speechSynthesis.cancel(); // Detener cualquier audio previo
            
            let texto = lang === 'en' 
                ? "Greetings Custodian. Operational node synchronized successfully. Operating in bilingual mode without data leaks."
                : document.getElementById("remi-msg").innerText;

            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = lang === 'en' ? 'en-US' : 'es-ES';
            utterance.rate = 1.05; // Velocidad fluida y natural
            utterance.pitch = 1.1;  // Tono optimizado para Remi

            // Buscar la mejor voz natural disponible en el dispositivo del usuario
            const voces = window.speechSynthesis.getVoices();
            const vozElegida = voces.find(v => v.lang.startsWith(lang));
            if (vozElegida) {
                utterance.voice = vozElegida;
            }

            window.speechSynthesis.speak(utterance);
        }

        // Precargar voces
        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = () => {
                window.speechSynthesis.getVoices();
            };
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
    return {"status": "online", "runtime": "vercel-bilingual-native"}
