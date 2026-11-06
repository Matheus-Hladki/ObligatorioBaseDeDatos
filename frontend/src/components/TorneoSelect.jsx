import { useEffect } from "react";
import { api } from "../api/client.js";
import useFetch from "./useFetch.js";

// Desplegable de torneos. Al cargar elige por defecto el que está "en curso" (o el último). 
// Uso: <TorneoSelect value={id} onChange={setId} />
export default function TorneoSelect({ value, onChange }) {
  const { data: torneos, error } = useFetch(api.torneos);

  useEffect(() => {
    if (torneos && torneos.length && value == null) {
      const elegido = torneos.find((t) => t.estado === "en curso") ?? torneos[torneos.length - 1];
      onChange(elegido.id_torneo);
    }
  }, [torneos]);

  if (error) return <p className="error">{error}</p>;
  if (!torneos) return null;

  return (
    <label className="torneo-select">
      Torneo{" "}
      <select value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
        {torneos.map((t) => (
          <option key={t.id_torneo} value={t.id_torneo}>
            {t.nombre} ({t.estado})
          </option>
        ))}
      </select>
    </label>
  );
}