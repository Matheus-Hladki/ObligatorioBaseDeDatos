import { useState } from "react";

// Ejecuta una acción contra la API (borrar, cancelar, etc) pide confirmación opcional, 
// muestra el error del backend y recarga la lista al terminar
export default function useAccion(reload) {
  const [error, setError] = useState("");
  async function ejecutar(fn, confirmacion) {
    if (confirmacion && !window.confirm(confirmacion)) return;
    setError("");
    try {
      await fn();
      reload?.();
    } catch (e) {
      setError(e.message);
    }
  }
  return { error, setError, ejecutar };
}