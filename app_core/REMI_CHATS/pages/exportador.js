export default function Exportador() {
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ color: '#FFD700' }}>📦 Exportador CSV</h1>
      <p>Genera un manifiesto físico de los 100k archivos para auditoría externa.</p>
      <button style={{ backgroundColor: '#00FBFF', color: 'black', padding: '10px', border: 'none', cursor: 'not-allowed' }}>
        GENERAR REPORTE (Bloqueado hasta llegar a 100k)
      </button>
    </div>
  );
}
