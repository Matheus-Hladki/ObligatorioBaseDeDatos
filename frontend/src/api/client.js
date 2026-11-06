// nuico lugar donde el front habla con el backend; si cambia una URL del backend, se toca solo eso

const BASE = "http://127.0.0.1:8000";

// agrega el token si hay sesión y convierte los errores en excepciones
async function request(path, { method = "GET", body } = {}) {
  const token = localStorage.getItem("token");

  const headers = { "Content-Type": "application/json" };
  if (token) {
    // con este header el backend sabe quién somos
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // intentamos leer el JSON; si no hay cuerpo (ej: 204), queda null
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    // los triggers de MySQL devuelven mensajes claros (ej: "el jugador está suspendido")
    throw new Error(data?.detail || data?.error || `Error ${res.status}`);
  }
  return data;
}

// arma "?a=1&b=2" ignorando valores vacíos
function query(params = {}) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") q.append(k, v);
  });
  const s = q.toString();
  return s ? `?${s}` : "";
}

export const api = {
  // métodos genéricos (los usan casi todas las páginas)
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  del: (path) => request(path, { method: "DELETE" }),

  // atajos específicos
  login: (correo, contrasena) =>
    request("/login", { method: "POST", body: { correo, contrasena } }),

  torneos: () => request("/torneos"),
  equipos: (idTorneo) => request(`/equipos${query({ id_torneo: idTorneo })}`),
  partidos: (idTorneo) => request(`/partidos${query({ id_torneo: idTorneo })}`),

  // reportes: api.reporte("posiciones", idTorneo) o con extra: { numero_fecha: 3 }
  reporte: (nombre, idTorneo, extra = {}) =>
    request(`/reportes/${nombre}${query({ id_torneo: idTorneo, ...extra })}`),
};