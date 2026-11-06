import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import FormModal from "../components/FormModal.jsx";
import { aISO } from "../utils/validar.js";

const SIGUIENTE = { "inscripción": "en curso", "en curso": "finalizado" };

const campos = [
  { name: "nombre", label: "Nombre", requerido: true, maxLength: 100 },
  { name: "anio", label: "Año", type: "number", requerido: true, min: 2000, max: 2100 },
  { name: "semestre", label: "Semestre", type: "select", requerido: true, options: [{ value: 1, label: "1" }, { value: 2, label: "2" }] },
  { name: "fecha_inicio", label: "Fecha de inicio", type: "date", requerido: true },
  {
    name: "fecha_fin", label: "Fecha de fin", type: "date", requerido: true,
    validar: (v, vals) => (vals.fecha_inicio && v < vals.fecha_inicio ? "No puede ser anterior al inicio" : null),
  },
];

export default function Torneos() {
  const { data, error, loading, reload } = useFetch(() => api.torneos());
  const accion = useAccion(reload);
  const [form, setForm] = useState(null);

  return (
    <>
      <div className="barra">
        <h1>Torneos</h1>
        <button onClick={() => setForm({})}>+ Nuevo torneo</button>
      </div>
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && (
        <table>
          <thead><tr><th>Nombre</th><th>Año/Sem</th><th>Inicio</th><th>Fin</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            {data.map((t) => (
              <tr key={t.id_torneo}>
                <td>{t.nombre}</td>
                <td>{t.anio} / {t.semestre}</td>
                <td>{aISO(t.fecha_inicio)}</td>
                <td>{aISO(t.fecha_fin)}</td>
                <td><span className="badge">{t.estado}</span></td>
                <td className="fila-acciones">
                  <button className="chico secundario" onClick={() => setForm({ ...t, fecha_inicio: aISO(t.fecha_inicio), fecha_fin: aISO(t.fecha_fin) })}>Editar</button>
                  {SIGUIENTE[t.estado] && (
                    <button className="chico" onClick={() => accion.ejecutar(() => api.patch(`/torneos/${t.id_torneo}/estado`, { estado: SIGUIENTE[t.estado] }), `¿Pasar "${t.nombre}" a "${SIGUIENTE[t.estado]}"? No se puede volver atrás`)}>
                      Pasar a {SIGUIENTE[t.estado]}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {form && (
        <FormModal
          titulo={form.id_torneo ? "Editar torneo" : "Nuevo torneo"}
          campos={campos}
          inicial={form}
          onSubmit={(v) => {
            const cuerpo = { ...v, semestre: Number(v.semestre) };
            return form.id_torneo ? api.put(`/torneos/${form.id_torneo}`, cuerpo) : api.post("/torneos", cuerpo);
          }}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
    </>
  );
}