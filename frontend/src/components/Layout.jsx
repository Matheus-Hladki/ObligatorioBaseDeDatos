import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

//común de todas las páginas: barra de arriba y contenido
// <Outlet /> es donde React Router pone la página actual
export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <>
      <header className="topbar">
        <strong>Torneo Interfacultades F5</strong>
        <nav>
          <Link to="/">Inicio</Link>
          <Link to="/posiciones">Posiciones</Link>
          {/* Los dos roles ven partidos; el planillero carga planillas desde acá */}
          <Link to="/partidos">Partidos</Link>
        </nav>
        <div className="user">
          <span>
            {user.correo} · <em>{user.rol}</em>
          </span>
          <button onClick={logout}>Salir</button>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}