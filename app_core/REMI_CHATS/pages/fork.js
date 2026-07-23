import Layout from './layout';
import fs from 'fs';

export default function Fork() {
  let registros = [];
  try {
    const data = fs.readFileSync('/mnt/sda7/REMI/bitacora_eventos.json');
    registros = JSON.parse(data);
  } catch (err) {
    registros = [];
  }

  function activarFork(registro) {
    alert(`Fork activado para ${registro.archivo} · SHA256: ${registro.sha256}`);
    // Aquí podrías duplicar el archivo en otra carpeta para trazabilidad
  }

  return (
    <Layout>
      <h1 style={{ color: '#d4af37', textShadow: '2px 2px 4px #000' }}>
        🔀 Activador de Fork
      </h1>
      <p>Genera una bifurcación de documentos registrados para trazabilidad.</p>

      <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
        {registros.map((r, i) => (
          <li key={i}>
            📄 {r.archivo} · SHA256: {r.sha256}
            <button onClick={() => activarFork(r)} style={{
              marginLeft: '1rem',
              padding: '0.25rem 0.5rem',
              backgroundColor: '#3aa0ff',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
              🔀 Fork
            </button>
          </li>
        ))}
      </ul>
    </Layout>
  );
}
