import { useEffect, useState } from "react";

// Ejecuta una llamada a la API y devuelve { data, error, loading }.
// Se vuelve a ejecutar cuando cambia algo de `deps` (ej: el torneo elegido).
export default function useFetch(fn, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let vigente = true; // evita pisar el estado si el componente ya cmabio
    setLoading(true);
    setError("");
    fn()
      .then((d) => vigente && setData(d))
      .catch((e) => vigente && setError(e.message))
      .finally(() => vigente && setLoading(false));
    return () => {
      vigente = false;
    };
  }, deps);

  return { data, error, loading };
}