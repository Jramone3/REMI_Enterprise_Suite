"use client";

import React, { useState } from "react";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string>("Iniciando visor de telemetría...");

  // Función para obtener logs del servidor
  const fetchLogs = async () => {
    setLogs("Actualizando telemetría...");
    try {
      const response = await fetch("http://127.0.0.1:5000/obtener-logs");
      const data = await response.json();
      setLogs(data.contenido || "No hay logs disponibles.");
    } catch (err) {
      setLogs("[ERROR] No se pudo conectar con el motor de telemetría en el puerto 5000.");
    }
  };

  const handleConsultar = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setStatus(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/remi", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: prompt }),
      });

      if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.statusText}`);
      }

      const data = await response.json();
      setStatus(data);
    } catch (err: any) {
      setError(err.message || "No se pudo conectar con el API Gateway de REMI.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-green-400 font-mono p-8 flex flex-col items-center">
      {/* Cabecera del Búnker */}
      <header className="w-full max-w-4xl border-b border-green-800 pb-4 mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black tracking-widest text-green-500">REMI_CORE OS</h1>
          <p className="text-xs text-green-600">SISTEMA CUSTODIO INTELIGENTE — ONLINE</p>
        </div>
        <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
      </header>

      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Panel Izquierdo: Formulario de Control */}
        <section className="border border-green-900 bg-zinc-950 p-6 rounded-lg shadow-lg shadow-green-950/20">
          <h2 className="text-xl font-bold mb-4 text-green-500 border-b border-green-900 pb-2">🕹️ PANEL DE MANDO</h2>
          
          <form onSubmit={handleConsultar} className="space-y-4">
            <div>
              <label className="block text-xs uppercase tracking-wider mb-2 text-green-600">
                Instrucción al Orquestador
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ej. Hola REMI, necesito que valides y limpies la lista de leads..."
                className="w-full h-32 bg-black border border-green-900 rounded p-3 text-sm focus:outline-none focus:border-green-500 text-green-400 placeholder-green-800"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 font-bold uppercase tracking-widest text-sm border ${
                loading
                  ? "bg-zinc-900 border-zinc-700 text-zinc-500 cursor-not-allowed"
                  : "bg-green-950 hover:bg-green-900 border-green-500 hover:text-white transition-all duration-300"
              }`}
            >
              {loading ? "PROCESANDO CON G-IA..." : "DISPARAR ORQUESTADOR"}
            </button>
          </form>

          {status && (
            <div className="mt-6 p-4 bg-black border border-green-700 rounded-md text-xs space-y-2">
              <p className="text-green-500 font-bold uppercase">📥 Respuesta del Cerebro:</p>
              <div><span className="text-green-600">STATUS:</span> {status.status}</div>
              <div><span className="text-green-600">DECISIÓN IA:</span> {status.decision_ia}</div>
              <div><span className="text-cast-green-600">SCRIPT EJECUTADO:</span> {status.ejecutado}</div>
              <p className="italic text-zinc-400 mt-2">{status.mensaje}</p>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-950/20 border border-red-700/50 rounded-md text-xs text-red-400">
              <p className="font-bold uppercase mb-1">❌ ERROR DE ACCESO:</p>
              {error}
            </div>
          )}
        </section>

        {/* Panel Derecho: Consola de logs y telemetría */}
        <section className="border border-green-900 bg-zinc-950 p-6 rounded-lg flex flex-col h-[500px]">
          <div className="flex justify-between items-center mb-4 border-b border-green-900 pb-2">
            <h2 className="text-xl font-bold text-green-500">📊 TELEMETRÍA DEL BÚNKER</h2>
            <button 
              onClick={fetchLogs}
              className="text-[10px] bg-green-900 hover:bg-green-700 text-white px-2 py-1 rounded uppercase"
            >
              Actualizar
            </button>
          </div>
          <pre className="flex-1 bg-black p-4 rounded border border-green-950 text-[10px] text-green-400/90 overflow-y-auto whitespace-pre-wrap font-mono scrollbar-thin scrollbar-thumb-green-900 scrollbar-track-transparent">
            {logs}
          </pre>
        </section>
      </div>
    </main>
  );
}
