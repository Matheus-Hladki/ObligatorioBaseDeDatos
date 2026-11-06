import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";

export default function Partidos() {
  const { data, error, loading } = useFetch(api.partidos);

  if (loading) return <p>Cargando...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <>
      <h1>Partidos</h1>
      <table>
        <thead>
          <tr><th>Fecha</th><th>Día</th><th>Local</th><th>Visitante</th><th>Cancha</th><th>Estado</th></tr>
        </thead>
        <tbody>
          {/* Los nombres de campos son supuestos: ajustarlos a lo que devuelva el backend */}
          {data.map((p) => (
            <tr key={p.id_partido}>
              <td>{p.numero_fecha}</td>
              <td>{p.dia}</td>
              <td>{p.equipo_local}</td>
              <td>{p.equipo_visitante}</td>
              <td>{p.nombre_cancha}</td>
              <td><span className={`badge ${p.estado}`}>{p.estado}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}