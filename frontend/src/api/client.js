// nuico lugar donde el front habla con el backend, si cambia una URL del backend, se toca solo eso

const BASE = "/api"; // en dev lo reenvía Vite, en Docker lo reenvía nginx

// si hay token, lo agrega el token y convierte errores en excepciones
async function request(path, {method = "GET", body} = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json"
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
     //si hay sesión iniciada, el backend sabe quien somos por este header
    body: body ? JSON.stringify(body) : undefined,
  });

  //intentamos leer el JSON; si no hay cuerpo, queda null
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    // Los triggers de MySQL devuelven mensajes claros (ej: "el jugador está suspendido")
    // Si el backend los reenvia q los muestre asi
    throw new Error(data?.detail || data?.error || `Error ${res.status}`);
  }
  return data;
}

//Endpoints, acordarlos con el back
export const api = {
  login: (correo, contrasena) =>
    request("/login", { method: "POST", body: { correo, contrasena } }),

  partidos: () => request("/partidos"),
  posiciones: () => request("/posiciones"),
};