import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import TorneoSelect from "../components/TorneoSelect.jsx";

const REPORTES = [
  { id: "posiciones", titulo: "Tabla de posiciones" },
  { id: "goleadores", titulo: "Goleadores (top 10)" },
  { id: "fair-play", titulo: "Fair play por equipo" },
  { id: "promedio-goles", titulo: "Promedio de goles por partido" },
  { id: "canchas", titulo: "Canchas más utilizadas" },
  { id: "turnos", titulo: "Turnos más utilizados" },
  { id: "jugadores-por-facultad", titulo: "Jugadores por facultad y tipo", sinTorneo: true },
  { id: "jugadores-sin-planilla", titulo: "Inscriptos que nunca jugaron" },
  { id: "sanciones", titulo: "Sanciones por equipo y motivo" },
  { id: "estado-partidos", titulo: "Partidos jugados vs postergados o cancelados" },
  { id: "resultados", titulo: "Resultados (extra)" },
  { id: "suspendidos", titulo: "Suspendidos en una fecha (extra)", pideFecha: true },
  { id: "reprogramaciones", titulo: "Historial de reprogramaciones (extra)" },
];

const etiqueta = (k) => k.replaceAll("_", " ");
const celda = (v) => (v === null || v === undefined ? "—" : typeof v === "boolean" ? (v ? "Sí" : "No") : String(v));

// Dibuja cualquier resultado del backend: lista de filas, objeto de una fila u objeto con varias listas
function Resultado({ datos, titulo }) {
  if (datos === null || datos === undefined) return null;
  if (!Array.isArray(datos) && typeof datos === "object") {
    const valores = Object.values(datos);
    if (valores.some((v) => Array.isArray(v) || (v && typeof v === "object"))) {
      return Object.entries(datos).map(([k, v]) => <Resultado key={k} datos={v} titulo={etiqueta(k)} />);
    }
    datos = [datos];
  }
  const columnas = datos.length ? Object.keys(datos[0]) : [];
  return (
    <>
      {titulo && <h3>{titulo}</h3>}
      <div className="tabla-scroll">
        <table>
          <thead><tr>{columnas.map((c) => <th key={c}>{etiqueta(c)}</th>)}</tr></thead>
          <tbody>
            {datos.length === 0 && <tr><td colSpan={Math.max(columnas.length, 1)}>Sin datos</td></tr>}
            {datos.map((fila, i) => (
              <tr key={i}>{columnas.map((c) => <td key={c}>{celda(fila[c])}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function Reportes() {
  const [idTorneo, setIdTorneo] = useState(null);
  const [reporte, setReporte] = useState(REPORTES[0]);
  const [fecha, setFecha] = useState("1");
  const fechaOk = /^\d+$/.test(fecha) && Number(fecha) >= 1 && Number(fecha) <= 127;

  const { data, error, loading } = useFetch(() => {
    if (reporte.sinTorneo) return api.get(`/reportes/${reporte.id}`);
    if (!idTorneo) return Promise.resolve(null);
    if (reporte.pideFecha) return fechaOk ? api.reporte(reporte.id, idTorneo, { numero_fecha: fecha }) : Promise.resolve(null);
    return api.reporte(reporte.id, idTorneo);
  }, [reporte.id, idTorneo, fecha]);

  return (
    <>
      <h1>Reportes</h1>
      <div className="tabs">
        {REPORTES.map((r) => (
          <button key={r.id} className={r.id === reporte.id ? "activo" : ""} onClick={() => setReporte(r)}>{r.titulo}</button>
        ))}
      </div>
      {!reporte.sinTorneo && <TorneoSelect value={idTorneo} onChange={setIdTorneo} />}
      {reporte.pideFecha && (
        <label style={{ maxWidth: 200 }}>
          Número de fecha
          <input value={fecha} onChange={(e) => setFecha(e.target.value)} />
          {!fechaOk && <span className="error">Ingresá un número entre 1 y 127</span>}
        </label>
      )}
      <h2>{reporte.titulo}</h2>
      {loading && <p>Cargando</p>}
      {error && <p className="error">{error}</p>}
      {data && !loading && <Resultado datos={data} />}
    </>
  );
}