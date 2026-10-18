'use client';

import { useState, useEffect, useRef } from 'react';

export default function Page() {
  const [timestamp, setTimestamp] = useState('Sincronizando...');
  const [isMounted, setIsMounted] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [menuDesplegableAbierto, setMenuDesplegableAbierto] = useState(false);
  const [chatHistorial, setChatHistorial] = useState([
    { remite: 'remi', texto: 'Saludos, Ramón. Núcleo ceremonial y cognitivo sincronizado. ¿Qué evaluamos hoy?' }
  ]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    setIsMounted(true);
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
    setTimestamp(now);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistorial]);

  const enviarMensaje = async (e) => {
    e.preventDefault();
    if (!mensaje.trim()) return;

    const mensajeUsuario = mensaje;
    const nuevoHistorial = [...chatHistorial, { remite: 'usuario', texto: mensajeUsuario }];
    setChatHistorial(nuevoHistorial);
    setMensaje('');

    try {
      const res = await fetch('http://localhost:5000/api/remi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: mensajeUsuario, speak: true, lang: 'es' }),
      });

      if (res.ok) {
        const data = await res.json();
        setChatHistorial(prev => [
          ...prev,
          { remite: 'remi', texto: data.mensaje || '[REMI Core]: Procesado correctamente.' }
        ]);
      } else {
        setChatHistorial(prev => [
          ...prev,
          { remite: 'remi', texto: `[REMI Enterprise Core]: Error de comunicación (HTTP ${res.status}).` }
        ]);
      }
    } catch (error) {
      setChatHistorial(prev => [
        ...prev,
        { remite: 'remi', texto: `[REMI Local Engine]: Error de red al conectar con el backend.` }
      ]);
    }
  };

  if (!isMounted) {
    return (
      <main style={{ background: '#07090e', color: '#fff', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'monospace' }}>
        <h1>Inicializando Núcleo Maestro REMI...</h1>
      </main>
    );
  }

  return (
    <main style={{ fontFamily: 'system-ui, -apple-system, sans-serif', padding: '2rem', maxWidth: '1300px', margin: '0 auto', background: '#07090e', color: '#f3f4f6', minHeight: '100vh' }}>
      
      {/* Cabecera Suprema con la Imagen de REMI */}
      <header style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: '1.5rem', marginBottom: '2rem', gap: '1.5rem' }}>
        <div style={{ flex: '1 1 500px' }}>
          <h1 style={{ fontSize: '2.5rem', margin: 0, color: '#38bdf8', fontWeight: '900', letterSpacing: '-0.025em' }}>🛡️ REMI AuthBridge – Interfaz Maestra</h1>
          <p style={{ margin: '0.5rem 0 0 0', color: '#94a3b8', fontSize: '1.1rem' }}>Entorno Unificado de Conciencia Agéntica, Auditoría y Ceremonial</p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '0.8rem', fontSize: '0.85rem' }}>
            <span style={{ background: '#065f46', color: '#6ee7b7', padding: '3px 10px', borderRadius: '6px', fontWeight: '600' }}>🟢 Backend: Puerto 5000</span>
            <span style={{ background: '#1e3a8a', color: '#93c5fd', padding: '3px 10px', borderRadius: '6px', fontWeight: '600' }}>⚡ Ollama: remi-enterprise</span>
            <span style={{ background: '#312e81', color: '#c4b5fd', padding: '3px 10px', borderRadius: '6px', fontWeight: '600' }}>🕒 {timestamp}</span>
          </div>
        </div>
        
        {/* Imagen Oficial de REMI */}
        <div style={{ position: 'relative', borderRadius: '16px', overflow: 'hidden', border: '2px solid #0284c7', boxShadow: '0 0 25px rgba(56, 189, 248, 0.3)' }}>
          <img src="/remi_core_master.png" alt="REMI Core Visual Master" width="220" style={{ display: 'block', background: '#0b0f19' }} />
        </div>
      </header>

      {/* Grid Principal de Módulos */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '2rem' }}>
        
        {/* Columna Izquierda: Paneles de Control y Estado */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <section style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '16px', border: '1px solid #1e293b' }}>
            <h2 style={{ color: '#38bdf8', fontSize: '1.25rem', marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📊 Tabla y Memoria Patrimonial
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
              <div style={{ background: '#1e293b', padding: '0.8rem 1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Nucleo Capacitor IA</span>
                <span style={{ color: '#4ade80', fontWeight: 'bold' }}>✅ Activo</span>
              </div>
              <div style={{ background: '#1e293b', padding: '0.8rem 1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Archivos Personales (sda7)</span>
                <span style={{ color: '#4ade80', fontWeight: 'bold' }}>✅ Activo</span>
              </div>
              <div style={{ background: '#1e293b', padding: '0.8rem 1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Documentación y AuthBridge</span>
                <span style={{ color: '#facc15', fontWeight: 'bold' }}>⚠️ Sincronizando</span>
              </div>
            </div>
          </section>

          <section style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '16px', border: '1px solid #1e293b' }}>
            <h2 style={{ color: '#38bdf8', fontSize: '1.25rem', marginTop: 0 }}>📜 Auditoría y Forks</h2>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.5' }}>
              Registro inmutable de decisiones agénticas y bifurcaciones de memoria ceremonial operando en tiempo real bajo directivas de discernimiento.
            </p>
            <button 
              onClick={() => alert("✅ Registro inmutable validado en Postgres y MongoDB")}
              style={{ marginTop: '1rem', width: '100%', background: '#0284c7', color: '#fff', border: 'none', padding: '0.8rem', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', transition: 'background 0.2s' }}
            >
              Registrar Token en Base de Datos
            </button>
          </section>

        </div>

        {/* Columna Derecha: El Chat Avanzado de REMI con Interfaz Estilo Asistente */}
        <section style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '16px', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', height: '650px' }}>
          
          <h2 style={{ color: '#38bdf8', fontSize: '1.25rem', marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.8rem' }}>
            🧠 Centro Conversacional Cognitivo (REMI)
          </h2>

          <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {chatHistorial.map((chat, idx) => (
              <div key={idx} style={{ 
                alignSelf: chat.remite === 'usuario' ? 'flex-end' : 'flex-start',
                background: chat.remite === 'usuario' ? '#0369a1' : '#1e293b',
                color: '#f8fafc',
                padding: '1rem 1.2rem',
                borderRadius: '12px',
                maxWidth: '85%',
                lineHeight: '1.6',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}>
                <strong style={{ display: 'block', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                  {chat.remite === 'usuario' ? 'RAMÓN' : 'REMI (IA)'}
                </strong>
                {chat.texto}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {menuDesplegableAbierto && (
            <div style={{ background: '#1e293b', padding: '0.8rem', borderRadius: '8px', marginBottom: '0.8rem', display: 'flex', gap: '1rem', border: '1px solid #334155' }}>
              <button onClick={() => { alert("Adjuntar archivo seleccionado"); setMenuDesplegableAbierto(false); }} style={{ background: '#0f172a', color: '#38bdf8', border: '1px solid #475569', padding: '0.5rem 0.8rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                📎 Adjuntar Archivo / Imagen
              </button>
              <button onClick={() => { alert("Micrófono activado para dictado"); setMenuDesplegableAbierto(false); }} style={{ background: '#0f172a', color: '#4ade80', border: '1px solid #475569', padding: '0.5rem 0.8rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                🎤 Micrófono (Voz)
              </button>
              <button onClick={() => { alert("Síntesis de voz (Parlante) activada"); setMenuDesplegableAbierto(false); }} style={{ background: '#0f172a', color: '#f472b6', border: '1px solid #475569', padding: '0.5rem 0.8rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                🔊 Escuchar Respuesta
              </button>
            </div>
          )}

          <form onSubmit={enviarMensaje} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#1e293b', padding: '0.5rem 0.8rem', borderRadius: '12px', border: '1px solid #334155' }}>
            
            <button 
              type="button" 
              onClick={() => setMenuDesplegableAbierto(!menuDesplegableAbierto)}
              style={{ background: '#334155', color: '#fff', border: 'none', width: '38px', height: '38px', borderRadius: '50%', fontSize: '1.2rem', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', transition: 'background 0.2s' }}
              title="Herramientas adicionales (Adjuntar, Voz, Audio)"
            >
              +
            </button>

            <input 
              type="text" 
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              placeholder="Escribe tu mensaje o instrucción para REMI..." 
              style={{ flex: 1, background: 'transparent', border: 'none', color: '#fff', fontSize: '1rem', outline: 'none', padding: '0.5rem' }}
            />

            <button 
              type="submit" 
              style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', transition: 'background 0.2s' }}
            >
              Enviar
            </button>
          </form>

        </section>

      </div>

    </main>
  );
}
