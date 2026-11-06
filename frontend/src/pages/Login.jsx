import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Cada input tiene su estado: React "controla" lo que se escribe
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault(); // evita que el navegador recargue la página
    setError("");
    setCargando(true);
    try {
      await login(correo, contrasena);
      navigate("/"); // login OK, al inicio
    } catch (err) {
      setError(err.message); // ej: credenciales inválidas
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={handleSubmit}>
        <h1>Iniciar sesión</h1>
        <label>
          Correo
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={cargando}>{cargando ? "Entrando..." : "Entrar"}</button>
      </form>
    </div>
  );
}
