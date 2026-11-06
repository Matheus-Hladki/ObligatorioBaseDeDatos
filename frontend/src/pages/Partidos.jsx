import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import TorneoSelect from "../components/TorneoSelect.jsx";

export default function Partidos() {
  const [idTorneo, setIdTorneo] = useState(null);
  const { data, error, loading } = useFetch(
    () => (idTorneo ? api.partidos(idTorneo) : Promise.resolve([])),
    [idTorneo]
  );

  return (
    <>
      <h1>Partidos</h1>
      <TorneoSelect value={idTorneo} onChange={setIdTorneo} />

      {loading && <p>Cargando...</p>}
      {error && <p className="error">{error}</p>}
      {data && !loading && (
        <table>
          <thead>
            <tr>
              <th>Fecha</th><th>Día</th><th>Hora</th><th>Local</th><th>Visitante</th>
              <th>Cancha</th><th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 && (
              <tr><td colSpan={7}>Este torneo todavía no tiene partidos.</td></tr>
            )}
            {data.map((p) => (
              <tr key={p.id_partido}>
                <td>{p.numero_fecha}</td>
                <td>{p.dia}</td>
                <td>{p.hora_inicio?.slice(0, 5)}–{p.hora_fin?.slice(0, 5)}</td>
                <td>{p.equipo_local}</td>
                <td>{p.equipo_visitante}</td>
                <td>{p.nombre_cancha} · {p.complejo}</td>
                <td><span className={`badge ${p.estado}`}>{p.estado}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}