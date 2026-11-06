import { useState } from "react";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import FormModal from "../components/FormModal.jsx";
import { esCI, aISO, hoyISO } from "../utils/validar.js";

const TIPOS = ["grado", "posgrado", "docente", "funcionario"];

export default function Jugadores() {
  const { data, error, loading, reload } = useFetch(() => api.get("/jugadores"));
  const { data: facultades } = useFetch(() => api.get("/facultades"));
  const accion = useAccion(reload);
  const [form, setForm] = useState(null);
  const [filtro, setFiltro] = useState("");

  const editando = form && form.ci;
  const campos = [
    { name: "ci", label: "Cédula (7 u 8 dígitos)", requerido: true, disabled: !!editando, maxLength: 8, validar: (v) => (esCI(v) ? null : "La cédula debe tener 7 u 8 dígitos") },
    { name: "nombre", label: "Nombre", requerido: true, maxLength: 50 },
    { name: "apellido", label: "Apellido", requerido: true, maxLength: 50 },
    { name: "email", label: "Email", type: "email", requerido: true, maxLength: 100 },
    { name: "fecha_nacimiento", label: "Fecha de nacimiento", type: "date", requerido: true, validar: (v) => (v >= hoyISO() ? "Debe ser anterior a hoy" : null) },
    { name: "id_facultad", label: "Facultad", type: "select", requerido: true, options: (facultades ?? []).map((f) => ({ value: f.id_facultad, label: f.nombre })) },
    { name: "tipo", label: "Tipo", type: "select", requerido: true, options: TIPOS.map((t) => ({ value: t, label: t })) },
  ];

  const lista = (data ?? []).filter((j) =>
    `${j.ci} ${j.nombre} ${j.apellido} ${j.facultad}`.toLowerCase().includes(filtro.toLowerCase())
  );

  return (
    <>
      <div className="barra">
        <h1>Jugadores</h1>
        <button onClick={() => setForm({})}>+ Nuevo jugador</button>
      </div>
      <input placeholder="Buscar por cédula, nombre o facultad" value={filtro} onChange={(e) => setFiltro(e.target.value)} />
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && (
        <div className="tabla-scroll">
          <table>
            <thead><tr><th>CI</th><th>Nombre</th><th>Email</th><th>Nacimiento</th><th>Facultad</th><th>Tipo</th><th></th></tr></thead>
            <tbody>
              {lista.map((j) => (
                <tr key={j.ci}>
                  <td>{j.ci}</td>
                  <td>{j.apellido}, {j.nombre}</td>
                  <td>{j.email}</td>
                  <td>{aISO(j.fecha_nacimiento)}</td>
                  <td>{j.facultad}</td>
                  <td>{j.tipo}</td>
                  <td className="fila-acciones">
                    <button className="chico secundario" onClick={() => setForm({ ...j, fecha_nacimiento: aISO(j.fecha_nacimiento) })}>Editar</button>
                    <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/jugadores/${j.ci}`), `¿Borrar a ${j.nombre} ${j.apellido}?`)}>Borrar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {form && (
        <FormModal
          titulo={editando ? "Editar jugador" : "Nuevo jugador"}
          campos={campos}
          inicial={form}
          onSubmit={(v) => {
            const cuerpo = { ...v, id_facultad: Number(v.id_facultad) };
            if (editando) {
              delete cuerpo.ci;
              return api.put(`/jugadores/${form.ci}`, cuerpo);
            }
            return api.post("/jugadores", cuerpo);
          }}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
    </>
  );
}