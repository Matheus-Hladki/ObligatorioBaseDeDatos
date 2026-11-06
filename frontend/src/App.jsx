import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute.jsx";
import Layout from "./components/Layout.jsx";
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";
import Partidos from "./pages/Partidos.jsx";
import Posiciones from "./pages/Posiciones.jsx";

// Mapa de la app: que página se muestra en cada URL.
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
        <Route path="/posiciones" element={<Posiciones />} />

        {/* Ejemplo de ruta solo para admin (cuando exista la página):
        <Route path="/admin/equipos" element={
          <ProtectedRoute roles={["administrador"]}><Equipos /></ProtectedRoute>
        } /> */}
      </Route>

      {/* URL desconocida, inicio */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}