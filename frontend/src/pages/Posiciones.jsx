import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import TorneoSelect from "../components/TorneoSelect.jsx";

export default function Posiciones() {
  const [idTorneo, setIdTorneo] = useState(null);
  const { data, error, loading } = useFetch(
    () => (idTorneo ? api.reporte("posiciones", idTorneo) : Promise.resolve([])),
    [idTorneo]
  );

  return (
    <>
      <h1>Tabla de posiciones</h1>
      <TorneoSelect value={idTorneo} onChange={setIdTorneo} />

      {loading && <p>Cargando...</p>}
      {error && <p className="error">{error}</p>}
      {data && !loading && (
        <table>
          <thead>
            <tr>
              <th>#</th><th>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th>
              <th>GF</th><th>GC</th><th>DG</th><th>Pts</th>
            </tr>
          </thead>
          <tbody>
            {data.map((e, i) => (
              <tr key={e.id_equipo}>
                <td>{i + 1}</td>
                <td>{e.equipo}</td>
                <td>{e.jugados}</td>
                <td>{e.ganados}</td>
                <td>{e.empatados}</td>
                <td>{e.perdidos}</td>
                <td>{e.goles_favor}</td>
                <td>{e.goles_contra}</td>
                <td>{e.diferencia}</td>
                <td><strong>{e.puntos}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}