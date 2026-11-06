import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import FormModal from "../components/FormModal.jsx";

const campos = [{ name: "nombre", label: "Nombre", requerido: true, maxLength: 100 }];

export default function Facultades() {
  const { data, error, loading, reload } = useFetch(() => api.get("/facultades"));
  const accion = useAccion(reload);
  const [form, setForm] = useState(null); // null | {} (nuevo) | facultad (editar)

  return (
    <>
      <div className="barra">
        <h1>Facultades</h1>
        <button onClick={() => setForm({})}>+ Nueva facultad</button>
      </div>
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && (
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th></th></tr></thead>
          <tbody>
            {data.map((f) => (
              <tr key={f.id_facultad}>
                <td>{f.id_facultad}</td>
                <td>{f.nombre}</td>
                <td className="fila-acciones">
                  <button className="chico secundario" onClick={() => setForm(f)}>Editar</button>
                  <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/facultades/${f.id_facultad}`), `¿Borrar la facultad ${f.nombre}?`)}>Borrar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {form && (
        <FormModal
          titulo={form.id_facultad ? "Editar facultad" : "Nueva facultad"}
          campos={campos}
          inicial={form}
          onSubmit={(v) => (form.id_facultad ? api.put(`/facultades/${form.id_facultad}`, v) : api.post("/facultades", v))}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
    </>
  );
}