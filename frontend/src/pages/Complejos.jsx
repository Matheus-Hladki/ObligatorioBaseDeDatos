import { useState } from "react";
import {api} from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import FormModal from "../components/FormModal.jsx";

const camposComplejo = [
  { name: "nombre", label: "Nombre", requerido: true, maxLength: 100 },
  { name: "direccion", label: "Dirección", requerido: true, maxLength: 150 },
  { name: "departamento", label: "Departamento", requerido: true, maxLength: 50 },
];

export default function Complejos() {
  const { data, error, loading, reload } = useFetch(() => api.get("/complejos"));
  const { data: canchas, reload: reloadCanchas } = useFetch(() => api.get("/canchas"));
  const accion = useAccion(() => { reload(); reloadCanchas(); });
  const [formC, setFormC] = useState(null); // complejo
  const [formCancha, setFormCancha] = useState(null); // { id_complejo, cancha? , editar }

  const camposCancha = [
    { name: "nombre_cancha", label: "Nombre de la cancha", requerido: true, maxLength: 50, disabled: !!formCancha?.editar },
    { name: "superficie", label: "Superficie", type: "select", requerido: true, options: [{ value: "sintético", label: "sintético" }, { value: "parquet", label: "parquet" }] },
    { name: "techada", label: "Techada", type: "checkbox" },
  ];

  return (
    <>
      <div className="barra">
        <h1>Complejos y canchas</h1>
        <button onClick={() => setFormC({})}>+ Nuevo complejo</button>
      </div>
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && data.map((c) => (
        <div key={c.id_complejo} className="card" style={{ marginBottom: "1rem" }}>
          <div className="barra" style={{ margin: 0 }}>
            <div>
              <strong>{c.nombre}</strong> · {c.direccion} ({c.departamento})
            </div>
            <div className="fila-acciones">
              <button className="chico secundario" onClick={() => setFormC(c)}>Editar</button>
              <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/complejos/${c.id_complejo}`), `¿Borrar el complejo ${c.nombre} y sus canchas?`)}>Borrar</button>
              <button className="chico" onClick={() => setFormCancha({ id_complejo: c.id_complejo })}>+ Cancha</button>
            </div>
          </div>
          <table style={{ marginTop: "0.75rem" }}>
            <thead><tr><th>Cancha</th><th>Superficie</th><th>Techada</th><th></th></tr></thead>
            <tbody>
              {(canchas ?? []).filter((x) => x.id_complejo === c.id_complejo).map((x) => (
                <tr key={x.nombre_cancha}>
                  <td>{x.nombre_cancha}</td>
                  <td>{x.superficie}</td>
                  <td>{x.techada ? "Sí" : "No"}</td>
                  <td className="fila-acciones">
                    <button className="chico secundario" onClick={() => setFormCancha({ ...x, editar: true })}>Editar</button>
                    <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/complejos/${c.id_complejo}/canchas/${encodeURIComponent(x.nombre_cancha)}`), `¿Borrar la cancha ${x.nombre_cancha}?`)}>Borrar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      {formC && (
        <FormModal
          titulo={formC.id_complejo ? "Editar complejo" : "Nuevo complejo"}
          campos={camposComplejo}
          inicial={formC}
          onSubmit={(v) => (formC.id_complejo ? api.put(`/complejos/${formC.id_complejo}`, v) : api.post("/complejos", v))}
          onClose={(ok) => { setFormC(null); if (ok) reload(); }}
        />
      )}
      {formCancha && (
        <FormModal
          titulo={formCancha.editar ? "Editar cancha" : "Nueva cancha"}
          campos={camposCancha}
          inicial={formCancha}
          onSubmit={(v) =>
            formCancha.editar
              ? api.put(`/complejos/${formCancha.id_complejo}/canchas/${encodeURIComponent(formCancha.nombre_cancha)}`, { superficie: v.superficie, techada: v.techada })
              : api.post(`/complejos/${formCancha.id_complejo}/canchas`, v)
          }
          onClose={(ok) => { setFormCancha(null); if (ok) reloadCanchas(); }}
        />
      )}
    </>
  );
}