import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function Home() {
  const { user } = useAuth();
  const esAdmin = user.rol === "administrador";

  return (
    <>
      <h1>Bienvenido</h1>
      <p>
        {esAdmin
          ? "Como administrador podés gestionar toda la información del torneo"
          : "Como planillero podés registrar planillas, goles y tarjetas de los partidos"}
      </p>
      <div className="grid">
        <Link className="card" to="/partidos">Partidos</Link>
        {esAdmin && (
          <>
            <Link className="card" to="/torneos">Torneos</Link>
            <Link className="card" to="/equipos">Equipos y planteles</Link>
            <Link className="card" to="/jugadores">Jugadores</Link>
            <Link className="card" to="/facultades">Facultades</Link>
            <Link className="card" to="/complejos">Complejos y canchas</Link>
            <Link className="card" to="/sanciones">Sanciones</Link>
            <Link className="card" to="/reportes">Reportes</Link>
            <Link className="card" to="/posiciones">Tabla de posiciones</Link>
            <Link className="card" to="/usuarios">Usuarios</Link>
          </>
        )}
      </div>
    </>
  );
}