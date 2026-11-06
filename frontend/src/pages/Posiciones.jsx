import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";

export default function Posiciones() {
  const { data, error, loading } = useFetch(api.posiciones);

  if (loading) return <p>Cargando...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <>
      <h1>Tabla de posiciones</h1>
      <table>
        <thead>
          <tr><th>#</th><th>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th><th>GF</th><th>GC</th><th>Pts</th></tr>
        </thead>
        <tbody>
          {data.map((e, i) => (
            <tr key={e.id_equipo}>
              <td>{i + 1}</td><td>{e.equipo}</td><td>{e.pj}</td><td>{e.pg}</td>
              <td>{e.pe}</td><td>{e.pp}</td><td>{e.gf}</td><td>{e.gc}</td><td><strong>{e.pts}</strong></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}