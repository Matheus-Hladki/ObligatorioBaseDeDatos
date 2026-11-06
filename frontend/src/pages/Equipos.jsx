import { useState } from "react";
import {api} from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import TorneoSelect from "../components/TorneoSelect.jsx";
import FormModal from "../components/FormModal.jsx";
import Modal from "../components/Modal.jsx";

// Plantel de un equipo: alta o baja de jugadores y designación del capitán
function Plantel({ idEquipo, onClose }) {
  const { data: equipo, error, reload } = useFetch(() => api.get(`/equipos/${idEquipo}`), [idEquipo]);
  const { data: jugadores } = useFetch(() => api.get("/jugadores"));
  const accion = useAccion(reload);
  const [alta, setAlta] = useState(false);

  if (!equipo) return <Modal titulo="Plantel" onClose={onClose}>{error ? <p className="error">{error}</p> : <p>Cargando</p>}</Modal>;

  const enPlantel = new Set(equipo.jugadores.map((j) => j.ci_jugador));
  const candidatos = (jugadores ?? []).filter((j) => j.id_facultad === equipo.id_facultad && !enPlantel.has(j.ci));
  const campos = [
    { name: "ci_jugador", label: "Jugador (de la facultad del equipo)", type: "select", requerido: true, options: candidatos.map((j) => ({ value: j.ci, label: `${j.apellido}, ${j.nombre} (${j.tipo}) · ${j.ci}` })) },
    { name: "numero_camiseta", label: "Número de camiseta", type: "number", requerido: true, min: 1, max: 99 },
  ];

  return (
    <Modal titulo={`Plantel · ${equipo.nombre}`} onClose={onClose}>
      <p>{equipo.facultad} · {equipo.torneo} · {equipo.cantidad_jugadores} jugadores (entre 5 y 10, máx. 2 docentes/funcionarios)</p>
      <p>Capitán: <strong>{equipo.capitan ?? "sin designar"}</strong></p>
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      <table>
        <thead><tr><th>#</th><th>Jugador</th><th>Tipo</th><th></th></tr></thead>
        <tbody>
          {equipo.jugadores.map((j) => (
            <tr key={j.ci_jugador}>
              <td>{j.numero_camiseta}</td>
              <td>{j.apellido}, {j.nombre}</td>
              <td>{j.tipo}</td>
              <td className="fila-acciones">
                {equipo.ci_capitan !== j.ci_jugador && (
                  <button className="chico secundario" onClick={() => accion.ejecutar(() => api.patch(`/equipos/${idEquipo}/capitan`, { ci_capitan: j.ci_jugador }))}>Hacer capitán</button>
                )}
                <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/equipos/${idEquipo}/jugadores/${j.ci_jugador}`), `¿Quitar a ${j.nombre} del plantel?`)}>Quitar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="acciones">
        <button onClick={() => setAlta(true)}>+ Agregar jugador</button>
      </div>
      {alta && (
        <FormModal
          titulo="Agregar jugador al plantel"
          campos={campos}
          onSubmit={(v) => api.post(`/equipos/${idEquipo}/jugadores`, v)}
          onClose={(ok) => { setAlta(false); if (ok) reload(); }}
        />
      )}
    </Modal>
  );
}

export default function Equipos() {
  const [idTorneo, setIdTorneo] = useState(null);
  const { data, error, loading, reload } = useFetch(() => (idTorneo ? api.equipos(idTorneo) : Promise.resolve([])), [idTorneo]);
  const { data: facultades } = useFetch(() => api.get("/facultades"));
  const accion = useAccion(reload);
  const [form, setForm] = useState(null);
  const [plantel, setPlantel] = useState(null);

  const campos = [
    { name: "nombre", label: "Nombre del equipo", requerido: true, maxLength: 100 },
    { name: "id_facultad", label: "Facultad", type: "select", requerido: true, options: (facultades ?? []).map((f) => ({ value: f.id_facultad, label: f.nombre })) },
  ];

  return (
    <>
      <div className="barra">
        <h1>Equipos y planteles</h1>
        <button disabled={!idTorneo} onClick={() => setForm({})}>+ Nuevo equipo</button>
      </div>
      <TorneoSelect value={idTorneo} onChange={setIdTorneo} />
      <p>Los equipos y planteles solo se pueden modificar con el torneo en etapa de inscripción</p>
      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && (
        <table>
          <thead><tr><th>Equipo</th><th>Facultad</th><th>Capitán</th><th>Jugadores</th><th></th></tr></thead>
          <tbody>
            {data.length === 0 && <tr><td colSpan={5}>Sin equipos</td></tr>}
            {data.map((e) => (
              <tr key={e.id_equipo}>
                <td>{e.nombre}</td>
                <td>{e.facultad}</td>
                <td>{e.capitan ?? "—"}</td>
                <td>{e.cantidad_jugadores}</td>
                <td className="fila-acciones">
                  <button className="chico" onClick={() => setPlantel(e.id_equipo)}>Plantel</button>
                  <button className="chico secundario" onClick={() => setForm(e)}>Editar</button>
                  <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/equipos/${e.id_equipo}`), `¿Borrar el equipo ${e.nombre}?`)}>Borrar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {form && (
        <FormModal
          titulo={form.id_equipo ? "Editar equipo" : "Nuevo equipo"}
          campos={campos}
          inicial={form}
          onSubmit={(v) => {
            const cuerpo = { ...v, id_facultad: Number(v.id_facultad) };
            return form.id_equipo ? api.put(`/equipos/${form.id_equipo}`, cuerpo) : api.post("/equipos", { ...cuerpo, id_torneo: idTorneo });
          }}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
      {plantel && <Plantel idEquipo={plantel} onClose={() => { setPlantel(null); reload(); }} />}
    </>
  );
}