import Layout from './layout';
import { useEffect, useState } from 'react';

export default function Publicador() {
  const [registros, setRegistros] = useState([]);

  useEffect(() => {
    fetch('/api/directivas')
      .then(res => res.json())
      .then(data => setRegistros(data));
  }, []);

  function verificar(r) {
    const encontrado = registros.find(ev => ev.sha256 === r.sha256);
    if (encontrado) {
      alert(`Documento ${r.archivo} verificado correctamente.`);
    } else {
      alert("Documento no encontrado en bitácora.");
    }
  }

  return (
    <Layout>
      <h1>📜 Publicador y Verificador</h1>
      <ul>
        {registros.map((r, i) => (
          <li key={i}>
            {r.archivo} · {r.sha256}
            <button onClick={() => verificar(r)}>✅ Verificar</button>
          </li>
        ))}
      </ul>
    </Layout>
  );
}
