import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute.jsx";
import Layout from "./components/Layout.jsx";
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";
import Partidos from "./pages/Partidos.jsx";
import Posiciones from "./pages/Posiciones.jsx";
import Planilla from "./pages/Planilla.jsx";
import Torneos from "./pages/Torneos.jsx";
import Equipos from "./pages/Equipos.jsx";
import Jugadores from "./pages/Jugadores.jsx";
import Facultades from "./pages/Facultades.jsx";
import Complejos from "./pages/Complejos.jsx";
import Sanciones from "./pages/Sanciones.jsx";
import Reportes from "./pages/Reportes.jsx";
import Usuarios from "./pages/Usuarios.jsx";

const soloAdmin = (el) => <ProtectedRoute roles={["administrador"]}>{el}</ProtectedRoute>;

// Mapa de la app: que página se muestra en cada URL
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Todo lo de adentro exige estar logueado y usa el Layout (barra superior) */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Home />} />
        <Route path="/partidos" element={<Partidos />} />
        {/* Los reportes son solo para administradores (así lo exige el backend) */}
        <Route
          path="/posiciones"
          element={
            <ProtectedRoute roles={["administrador"]}>
              <Posiciones />
            </ProtectedRoute>
          }
        />

        {/* La planilla la cargan planilleros y administradores */}
        <Route path="/partidos/:id/planilla" element={<Planilla />} />
        <Route path="/torneos" element={soloAdmin(<Torneos />)} />
        <Route path="/equipos" element={soloAdmin(<Equipos />)} />
        <Route path="/jugadores" element={soloAdmin(<Jugadores />)} />
        <Route path="/facultades" element={soloAdmin(<Facultades />)} />
        <Route path="/complejos" element={soloAdmin(<Complejos />)} />
        <Route path="/sanciones" element={soloAdmin(<Sanciones />)} />
        <Route path="/reportes" element={soloAdmin(<Reportes />)} />
        <Route path="/usuarios" element={soloAdmin(<Usuarios />)} />
      </Route>

      {/* URL desconocida, inicio */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}