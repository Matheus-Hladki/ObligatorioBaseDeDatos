import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import TorneoSelect from "../components/TorneoSelect.jsx";
import FormModal from "../components/FormModal.jsx";
import { aISO, hora } from "../utils/validar.js";

export default function Partidos() {
  const { user } = useAuth();
  const esAdmin = user.rol === "administrador";
  const [idTorneo, setIdTorneo] = useState(null);
  const { data, error, loading, reload } = useFetch(
    () => (idTorneo ? api.partidos(idTorneo) : Promise.resolve([])),
    [idTorneo]
  );
  const { data: equipos } = useFetch(() => (idTorneo ? api.equipos(idTorneo) : Promise.resolve([])), [idTorneo]);
  const { data: turnos } = useFetch(() => api.get("/turnos"));
  const { data: canchas } = useFetch(() => api.get("/canchas"));
  const accion = useAccion(reload);
  const [form, setForm] = useState(null); // {} programar | { reprogramar: partido }

  const optCanchas = (canchas ?? []).map((c) => ({ value: `${c.id_complejo}|${c.nombre_cancha}`, label: `${c.nombre_cancha} · ${c.complejo}` }));
  const optTurnos = (turnos ?? []).map((t) => ({ value: t.id_turno, label: `${t.hora_inicio}–${t.hora_fin}` }));
  const optEquipos = (equipos ?? []).map((e) => ({ value: e.id_equipo, label: e.nombre }));

  const camposProgramar = [
    { name: "numero_fecha", label: "Número de fecha del torneo", type: "number", requerido: true, min: 1, max: 127 },
    { name: "id_equipo_local", label: "Equipo local", type: "select", requerido: true, options: optEquipos },
    {
      name: "id_equipo_visitante", label: "Equipo visitante", type: "select", requerido: true, options: optEquipos,
      validar: (v, vals) => (String(v) === String(vals.id_equipo_local) ? "Un equipo no puede jugar contra sí mismo" : null),
    },
    { name: "dia", label: "Día", type: "date", requerido: true },
    { name: "id_turno", label: "Turno", type: "select", requerido: true, options: optTurnos },
    { name: "cancha", label: "Cancha", type: "select", requerido: true, options: optCanchas },
  ];
  const camposReprog = [
    { name: "dia", label: "Nuevo día", type: "date", requerido: true },
    { name: "id_turno", label: "Nuevo turno", type: "select", requerido: true, options: optTurnos },
    { name: "cancha", label: "Nueva cancha", type: "select", requerido: true, options: optCanchas },
    { name: "motivo", label: "Motivo", requerido: true, maxLength: 200 },
  ];
  const partirCancha = (c) => {
    const [id_complejo, ...resto] = c.split("|");
    return { id_complejo: Number(id_complejo), nombre_cancha: resto.join("|") };
  };

  return (
    <>
      <div className="barra">
        <h1>Partidos</h1>
        {esAdmin && <button disabled={!idTorneo} onClick={() => setForm({})}>+ Programar partido</button>}
      </div>
      <TorneoSelect value={idTorneo} onChange={setIdTorneo} />

      {loading && <p>Cargando</p>}
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}
      {data && !loading && (
        <div className="tabla-scroll">
          <table>
            <thead>
              <tr>
                <th>Fecha</th><th>Día</th><th>Hora</th><th>Local</th><th>Visitante</th>
                <th>Cancha</th><th>Estado</th><th></th>
              </tr>
            </thead>
            <tbody>
              {data.length === 0 && <tr><td colSpan={8}>Este torneo todavía no tiene partidos</td></tr>}
              {data.map((p) => (
                <tr key={p.id_partido}>
                  <td>{p.numero_fecha}</td>
                  <td>{aISO(p.dia)}</td>
                  <td>{hora(p.hora_inicio)}–{hora(p.hora_fin)}</td>
                  <td>{p.equipo_local}</td>
                  <td>{p.equipo_visitante}</td>
                  <td>{p.nombre_cancha} · {p.complejo}</td>
                  <td><span className={`badge ${p.estado}`}>{p.estado}</span></td>
                  <td className="fila-acciones">
                    <Link className="chico" to={`/partidos/${p.id_partido}/planilla`}>
                      <button className="chico">Planilla</button>
                    </Link>
                    {esAdmin && p.estado !== "jugado" && p.estado !== "cancelado" && (
                      <>
                        {p.estado === "programado" && (
                          <button className="chico" onClick={() => accion.ejecutar(() => api.patch(`/partidos/${p.id_partido}/jugado`), "¿Marcar el partido como jugado?")}>Jugado</button>
                        )}
                        {p.estado === "programado" && (
                          <button className="chico secundario" onClick={() => accion.ejecutar(() => api.patch(`/partidos/${p.id_partido}/postergar`), "¿Postergar el partido?")}>Postergar</button>
                        )}
                        <button className="chico secundario" onClick={() => setForm({ reprogramar: p })}>Reprogramar</button>
                        <button className="chico peligro" onClick={() => accion.ejecutar(() => api.patch(`/partidos/${p.id_partido}/cancelar`), "¿Cancelar el partido? No se puede reactivar")}>Cancelar</button>
                      </>
                    )}
                    {esAdmin && p.estado !== "jugado" && (
                      <button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/partidos/${p.id_partido}`), "¿Eliminar el partido?")}>Eliminar</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {form && !form.reprogramar && (
        <FormModal
          titulo="Programar partido"
          campos={camposProgramar}
          onSubmit={(v) => {
            const { cancha, ...resto } = v;
            return api.post("/partidos", {
              ...resto,
              id_equipo_local: Number(v.id_equipo_local),
              id_equipo_visitante: Number(v.id_equipo_visitante),
              id_turno: Number(v.id_turno),
              id_torneo: idTorneo,
              ...partirCancha(cancha),
            });
          }}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
      {form?.reprogramar && (
        <FormModal
          titulo={`Reprogramar ${form.reprogramar.equipo_local} vs ${form.reprogramar.equipo_visitante}`}
          campos={camposReprog}
          inicial={{
            dia: aISO(form.reprogramar.dia),
            id_turno: form.reprogramar.id_turno,
            cancha: `${form.reprogramar.id_complejo}|${form.reprogramar.nombre_cancha}`,
          }}
          onSubmit={(v) => {
            const { cancha, ...resto } = v;
            return api.patch(`/partidos/${form.reprogramar.id_partido}/reprogramar`, { ...resto, id_turno: Number(v.id_turno), ...partirCancha(cancha) });
          }}
          onClose={(ok) => { setForm(null); if (ok) reload(); }}
        />
      )}
    </>
  );
}