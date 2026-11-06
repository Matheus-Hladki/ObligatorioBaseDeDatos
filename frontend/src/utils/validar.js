//vlaidaciones de formato del front, replican las reglas del backend y de la bd
export const esCI = (v) => /^\d{7,8}$/.test(String(v ?? ""));
export const esEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v ?? ""));
export const enRango = (v, min, max) => v !== "" && v != null && Number.isInteger(Number(v)) && Number(v) >= min && Number(v) <= max;
export const vacio = (v) => v === "" || v === undefined || v === null || String(v).trim() === "";

export const hoyISO = () => new Date().toISOString().slice(0, 10);
export const aISO = (v) => (v ? String(v).slice(0, 10) : "");
export const hora = (h) => (h ? String(h).slice(0, 5) : "");