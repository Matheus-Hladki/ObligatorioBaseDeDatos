import { useState } from "react";
import Modal from "./Modal.jsx";
import { vacio } from "../utils/validar.js";

// onSubmit(valores) devuelve una promesa; si falla, se muestra el error del backend
export default function FormModal({ titulo, campos, inicial = {}, onSubmit, onClose, textoBoton = "Guardar" }) {
  const [valores, setValores] = useState(() => {
    const v = {};
    campos.forEach((c) => (v[c.name] = inicial[c.name] ?? (c.type === "checkbox" ? false : "")));
    return v;
  });
  const [errores, setErrores] = useState({});
  const [errorApi, setErrorApi] = useState("");
  const [enviando, setEnviando] = useState(false);

  function cambiar(c, valor) {
    setValores((v) => ({ ...v, [c.name]: valor }));
  }

  function validar() {
    const e = {};
    for (const c of campos) {
      const v = valores[c.name];
      if (c.requerido && c.type !== "checkbox" && vacio(v)) {
        e[c.name] = "Obligatorio";
        continue;
      }
      if (vacio(v)) continue;
      if (c.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) e[c.name] = "Email inválido";
      if (c.type === "number") {
        const n = Number(v);
        if (!Number.isInteger(n)) e[c.name] = "Debe ser un número entero";
        else if (c.min !== undefined && n < c.min) e[c.name] = `Mínimo ${c.min}`;
        else if (c.max !== undefined && n > c.max) e[c.name] = `Máximo ${c.max}`;
      }
      if (c.maxLength && String(v).length > c.maxLength) e[c.name] = `Máximo ${c.maxLength} caracteres`;
      if (!e[c.name] && c.validar) {
        const msg = c.validar(v, valores);
        if (msg) e[c.name] = msg;
      }
    }
    setErrores(e);
    return Object.keys(e).length === 0;
  }

  async function enviar(ev) {
    ev.preventDefault();
    setErrorApi("");
    if (!validar()) return;
    const salida = {};
    campos.forEach((c) => {
      const v = valores[c.name];
      salida[c.name] = c.type === "number" && !vacio(v) ? Number(v) : v;
    });
    setEnviando(true);
    try {
      await onSubmit(salida);
      onClose(true);
    } catch (err) {
      setErrorApi(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal titulo={titulo} onClose={() => onClose(false)}>
      <form onSubmit={enviar} noValidate>
        {campos.map((c) => (
          <label key={c.name} className={c.type === "checkbox" ? "check" : ""}>
            {c.type === "checkbox" ? (
              <>
                <input type="checkbox" checked={!!valores[c.name]} onChange={(e) => cambiar(c, e.target.checked)} /> {c.label}
              </>
            ) : (
              <>
                {c.label}
                {c.requerido && " *"}
                {c.type === "select" ? (
                  <select value={valores[c.name]} disabled={c.disabled} onChange={(e) => cambiar(c, e.target.value)}>
                    <option value="">— elegir —</option>
                    {c.options.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={c.type || "text"}
                    value={valores[c.name]}
                    disabled={c.disabled}
                    maxLength={c.maxLength}
                    onChange={(e) => cambiar(c, e.target.value)}
                  />
                )}
              </>
            )}
            {errores[c.name] && <span className="error">{errores[c.name]}</span>}
          </label>
        ))}
        {errorApi && <p className="error">{errorApi}</p>}
        <div className="acciones">
          <button type="button" className="secundario" onClick={() => onClose(false)}>Cancelar</button>
          <button disabled={enviando}>{enviando ? "Guardando" : textoBoton}</button>
        </div>
      </form>
    </Modal>
  );
}