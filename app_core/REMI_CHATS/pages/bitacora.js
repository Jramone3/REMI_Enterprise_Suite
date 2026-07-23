import Layout from './layout';
import { useEffect, useState } from 'react';

export default function Bitacora() {
  const [registros, setRegistros] = useState([]);

  useEffect(() => {
    fetch('/api/directivas')
      .then(res => res.json())
      .then(data => setRegistros(data));
  }, []);

  return (
    <Layout>
      <h1>📘 Bitácora de Eventos</h1>
      <table>
        <thead>
          <tr><th>Archivo</th><th>Ruta</th><th>SHA256</th><th>Fecha</th></tr>
        </thead>
        <tbody>
          {registros.map((r, i) => (
            <tr key={i}>
              <td>{r.archivo}</td>
              <td>{r.ruta}</td>
              <td>{r.sha256}</td>
              <td>{r.fecha}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}
