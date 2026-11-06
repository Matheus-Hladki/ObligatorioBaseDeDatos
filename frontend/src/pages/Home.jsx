import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function Home() {
  const { user } = useAuth();
  const esAdmin = user.rol === "administrador";

  return (
    <>
      <h1>Hola</h1>
      <p>
        {esAdmin
          ? "Como administrador podés gestionar toda la información del torneo."
          : "Como planillero podés registrar planillas, goles y tarjetas de los partidos."}
      </p>
      <div className="grid">
        <Link className="card" to="/partidos">Partidos</Link>
        <Link className="card" to="/posiciones"> Posiciones</Link>
        {/* TODO admin: equipos, planteles, fixture, sanciones, reportes */}
      </div>
    </>
  );
}