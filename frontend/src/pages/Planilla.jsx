import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client.js";
import useFetch from "../components/useFetch.js";
import useAccion from "../components/useAccion.js";
import FormModal from "../components/FormModal.jsx";

// Planilla de juego de un partido: jugadores que participaron, goles y tarjetas
export default function Planilla() {
  const { id } = useParams();
  const { data: planilla, error, reload: r1 } = useFetch(() => api.get(`/partidos/${id}/planilla`), [id]);
  const { data: goles, reload: r2 } = useFetch(() => api.get(`/partidos/${id}/goles`), [id]);
  const { data: tarjetas, reload: r3 } = useFetch(() => api.get(`/partidos/${id}/tarjetas`), [id]);
  const { data: partidos } = useFetch(async () => {
    // el partido no tiene GET propio: lo buscamos entre los de su torneo
    const todos = await api.torneos();
    for (const t of todos) {
      const ps = await api.partidos(t.id_torneo);
      const p = ps.find((x) => String(x.id_partido) === String(id));
      if (p) return p;
    }
    return null;
  }, [id]);
  const { data: localEq } = useFetch(() => (partidos ? api.get(`/equipos/${partidos.id_equipo_local}`) : Promise.resolve(null)), [partidos?.id_partido]);
  const { data: visitEq } = useFetch(() => (partidos ? api.get(`/equipos/${partidos.id_equipo_visitante}`) : Promise.resolve(null)), [partidos?.id_partido]);
  const reloadTodo = () => { r1(); r2(); r3(); };
  const accion = useAccion(reloadTodo);
  const [form, setForm] = useState(null); // "jugador" | "gol" | "tarjeta"

  const p = partidos;
  const enPlanilla = new Set((planilla ?? []).map((j) => j.ci_jugador));
  const candidatos = [];
  [localEq, visitEq].forEach((eq) =>
    eq?.jugadores.forEach((j) => !enPlanilla.has(j.ci_jugador) && candidatos.push({ value: `${eq.id_equipo}|${j.ci_jugador}`, label: `${eq.nombre} · #${j.numero_camiseta} ${j.apellido}, ${j.nombre}` }))
  );
  const jugadoresPlanilla = (planilla ?? []).map((j) => ({ value: j.ci_jugador, label: `${j.equipo} · #${j.numero_camiseta} ${j.apellido}, ${j.nombre}` }));

  const golesLocal = p && goles ? goles.filter((g) => (g.id_equipo === p.id_equipo_local) !== !!g.autogol).length : 0;
  const golesVisit = p && goles ? goles.length - golesLocal : 0;

  const campoMinuto = { name: "minuto", label: "Minuto (0-130)", type: "number", requerido: true, min: 0, max: 130 };

  return (
    <>
      <Link to="/partidos">← Volver a partidos</Link>
      <h1>Planilla de juego</h1>
      {p && (
        <p>
          <strong>{p.equipo_local} {golesLocal} – {golesVisit} {p.equipo_visitante}</strong> · Fecha {p.numero_fecha} · {String(p.dia).slice(0, 10)} · <span className={`badge ${p.estado}`}>{p.estado}</span>
        </p>
      )}
      <p>Solo se puede cargar la planilla de un partido jugado, hasta 48 horas después de su disputa. Los jugadores suspendidos no pueden figurar</p>
      {(error || accion.error) && <p className="error">{error || accion.error}</p>}

      <div className="dos-col">
        <div>
          <div className="barra"><h3>Jugadores</h3><button className="chico" onClick={() => setForm("jugador")}>+ Agregar</button></div>
          <table>
            <thead><tr><th>Equipo</th><th>#</th><th>Jugador</th><th></th></tr></thead>
            <tbody>
              {(planilla ?? []).map((j) => (
                <tr key={j.ci_jugador}>
                  <td>{j.equipo}</td><td>{j.numero_camiseta}</td><td>{j.apellido}, {j.nombre}</td>
                  <td><button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/partidos/${id}/planilla/${j.ci_jugador}`), "¿Quitar de la planilla (se borran sus tarjetas)?")}>Quitar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <div className="barra"><h3>Goles</h3><button className="chico" onClick={() => setForm("gol")}>+ Gol</button></div>
          <table>
            <thead><tr><th>Min</th><th>Jugador</th><th></th></tr></thead>
            <tbody>
              {(goles ?? []).map((g) => (
                <tr key={g.id_gol}>
                  <td>{g.minuto}'</td><td>{g.apellido}, {g.nombre}{g.autogol ? " (autogol)" : ""}</td>
                  <td><button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/partidos/${id}/goles/${g.id_gol}`), "¿Quitar el gol?")}>Quitar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="barra"><h3>Tarjetas</h3><button className="chico" onClick={() => setForm("tarjeta")}>+ Tarjeta</button></div>
          <table>
            <thead><tr><th>Min</th><th>Jugador</th><th>Color</th><th></th></tr></thead>
            <tbody>
              {(tarjetas ?? []).map((t) => (
                <tr key={t.id_tarjeta}>
                  <td>{t.minuto}'</td><td>{t.apellido}, {t.nombre}</td><td><span className={`badge ${t.color}`}>{t.color}</span></td>
                  <td><button className="chico peligro" onClick={() => accion.ejecutar(() => api.del(`/partidos/${id}/tarjetas/${t.id_tarjeta}`), "¿Quitar la tarjeta?")}>Quitar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {form === "jugador" && (
        <FormModal
          titulo="Agregar jugador a la planilla"
          campos={[{ name: "jugador", label: "Jugador", type: "select", requerido: true, options: candidatos }]}
          onSubmit={(v) => {
            const [id_equipo, ci_jugador] = v.jugador.split("|");
            return api.post(`/partidos/${id}/planilla`, { id_equipo: Number(id_equipo), ci_jugador });
          }}
          onClose={(ok) => { setForm(null); if (ok) reloadTodo(); }}
        />
      )}
      {form === "gol" && (
        <FormModal
          titulo="Registrar gol"
          campos={[{ name: "ci_jugador", label: "Jugador", type: "select", requerido: true, options: jugadoresPlanilla }, campoMinuto, { name: "autogol", label: "Autogol", type: "checkbox" }]}
          onSubmit={(v) => api.post(`/partidos/${id}/goles`, v)}
          onClose={(ok) => { setForm(null); if (ok) reloadTodo(); }}
        />
      )}
      {form === "tarjeta" && (
        <FormModal
          titulo="Registrar tarjeta"
          campos={[
            { name: "ci_jugador", label: "Jugador", type: "select", requerido: true, options: jugadoresPlanilla },
            campoMinuto,
            { name: "color", label: "Color", type: "select", requerido: true, options: [{ value: "amarilla", label: "amarilla" }, { value: "roja", label: "roja" }] },
          ]}
          onSubmit={(v) => api.post(`/partidos/${id}/tarjetas`, v)}
          onClose={(ok) => { setForm(null); if (ok) reloadTodo(); }}
        />
      )}
    </>
  );
}