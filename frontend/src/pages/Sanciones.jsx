import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import TorneoSelect from "../components/TorneoSelect.jsx";
import FormModal from "../components/FormModal.jsx";

export default function Sanciones() {
  const [idTorneo, setIdTorneo] = useState(null);
  const { data, error, loading, reload } = useFetch(() => (idTorneo ? api.get(`/sanciones/${id_torneo}`, { id_torneo: idTorneo }) : Promise.resolve([])), [idTorneo]);
  const { data: jugadores } = useFetch(() => api.get("/jugadores"));
  const accion = useAccion(reload);
  const [form, setForm] = useState(null);

  const campos = [
    { name: "ci_jugador", label: "Jugador", type: "select", requerido: true, disabled: !!form?.id_sancion, options: (jugadores ?? []).map((j) => ({ value: j.ci, label: `${j.apellido}, ${j.nombre} · ${j.ci}` })) },
    { name: "numero_fecha_inicio", label: "Fecha de inicio (nº de fecha del torneo)", type: "number", requerido: true, min: 1, max: 127 },
    { name: "cantidad_fechas", label: "Cantidad de fechas", type: "number", requerido: true, min: 1, max: 127 },
  ];
  return (
    <>
      <div className="barra">
        <h1>Sanciones</h1>
        <button disabled={!idTorneo} onClick={() => setForm({})}>+ Sanción disciplinaria</button>
      </div>
      <TorneoSelect value={idTorneo} onChange={setIdTorneo} />
      <p>Las sanciones por roja o acumulación de amarillas se generan solas; solo se editan las disciplinarias</p>
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && (
        <table>
          <thead><tr><th>Jugador</th><th>Motivo</th><th>Desde fecha</th><th>Hasta fecha</th><th>Cant </th><th></th></tr></thead>
          <tbody>
            {data.length === 0 && <tr><td colSpan={6}>Sin sanciones</td></tr>}
            {data.map((s) => (
              <tr key={s.id_sancion}>
                <td>{s.apellido}, {s.nombre}</td>
                <td>{s.motivo}</td>
                <td>{s.numero_fecha_inicio}</td>
                <td>{s.numero_fecha_fin}</td>
                <td>{s.cantidad_fechas}</td>
                <td className="fila-acciones">
                  {s.motivo === "disciplinaria" && (
                    <>
                      <button className="chico secundario" onClick={() => setForm(s)}>Editar</button>
                      <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/sanciones/${s.id_sancion}`), "¿Borrar la sanción?")}>Borrar</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {form && (
        <FormModal
          titulo={form.id_sancion ? "Editar sanción" : "Nueva sanción disciplinaria"}
          campos={campos}
          inicial={form}
          onSubmit={(v) =>
            form.id_sancion
              ? api.put(`/sanciones/${form.id_sancion}`, { numero_fecha_inicio: v.numero_fecha_inicio, cantidad_fechas: v.cantidad_fechas })
              : api.post("/sanciones", { ...v, id_torneo: idTorneo })
          }
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
    </>
  );
}