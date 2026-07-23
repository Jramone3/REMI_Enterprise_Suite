import { useEffect, useState } from 'react';

export default function Grafico() {
  const [datos, setDatos] = useState([]);

  useEffect(() => {
    async function fetchDatos() {
      try {
        const res = await fetch('/api/grafico');
        const json = await res.json();
        setDatos(json.datos || []);
      } catch (e) {
        console.error('⚠️ Error cargando datos de gráfico:', e);
      }
    }
    fetchDatos();
  }, []);

  return (
    <main style={{
      display: 'flex',
      flexDirection: 'row',
      padding: '2rem',
      fontFamily: 'Arial',
      backgroundColor: '#0c0c0c',
      color: '#ffffff',
      minHeight: '100vh'
    }}>
      {/* Columna izquierda */}
      <div style={{ flex: 1 }}>
        <h1 style={{ color: '#00ffff' }}>📊 Visualización Patrimonial</h1>
        <p style={{ color: '#cccccc' }}>Distribución de eventos por módulo patrimonial.</p>
      </div>

      {/* Columna derecha con barras */}
      <div style={{
        flex: 1,
        padding: '2rem',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        boxShadow: '0 0 20px rgba(0,0,0,0.3)',
      }}>
        {datos.length === 0 ? (
          <p style={{ color: '#000000' }}>No hay datos disponibles.</p>
        ) : (
          datos.map((d, idx) => (
            <div key={idx} style={{ marginBottom: '1.5rem' }}>
              <strong style={{ color: '#000000' }}>{d.modulo}</strong>
              <div
                style={{
                  backgroundColor: '#3498db',
                  height: '40px',
                  minWidth: '100px',
                  width: `${d.cantidad * 150}px`,
                  borderRadius: '6px',
                  marginTop: '0.5rem',
                  color: '#fff',
                  textAlign: 'right',
                  paddingRight: '10px',
                  lineHeight: '40px',
                  fontWeight: 'bold'
                }}
              >
                {d.cantidad}
              </div>
            </div>
          ))
        )}
      </div>
    </main>
  );
}
