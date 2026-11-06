import { useEffect, useState } from "react";

// Ejecuta una llamada a la API al abrir la página y devuelve { data, error, loading }
//   const { data, error, loading } = useFetch(api.partidos);
export default function useFetch(fn) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fn()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // [] = solo al montar el componente
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, error, loading };
}