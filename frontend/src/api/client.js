//nuico lugar donde el front habla con el backend. Si cambia una URL del backend, se toca solo este archivo.

const BASE = "/api"; // en dev lo reenvía Vite, en Docker lo reenvía nginx

function cerrarSesion() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
}

//Arma "?a=1&b=2" ignorando valores vacíos
function qs(params = {}) {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") p.append(k, v);
  });
  const s = p.toString();
  return s ? `?${s}` : "";
}

// Mensaje legible a partir de la respuesta de error de FastAPI
function mensajeDeError(data, status) {
  const d = data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    // 422 de Pydantic: [{loc:[...], msg:"..."}]
    return d.map((e) => `${e.loc?.slice(-1)[0] ?? "campo"}: ${e.msg}`).join(" · ");
  }
  return `Error ${status}`;
}

async function request(path, { method = "GET", body, params } = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE}${path}${qs(params)}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("No se pudo conectar con el servidor");
  }

  const data = await res.json().catch(() => null); // 204 no trae cuerpo

  if (!res.ok) {
    // Sesión vencida o inválida, mnesos 401
    if (res.status === 401 && path !== "/login") cerrarSesion();
    throw new Error(mensajeDeError(data, res.status));
  }
  return data;
}

export const api = {
  //para las pantallas que se vayan sumando
  get: (path, params) => request(path, { params }),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  del: (path) => request(path, { method: "DELETE" }),

  login: (correo, contrasena) =>
    request("/login", { method: "POST", body: { correo, contrasena } }),

  torneos: () => request("/torneos"),
  partidos: (id_torneo) => request("/partidos", { params: { id_torneo } }),

  // Reportes (solo administrador). nombre = posiciones, goleadores, fair-play, etc
  reporte: (nombre, id_torneo, extra) =>
    request(`/reportes/${nombre}`, { params: { id_torneo, ...extra } }),
};