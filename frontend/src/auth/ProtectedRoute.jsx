import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";

// envuelve una página y decide si el usuario puede verla
//   <ProtectedRoute roles={["administrador"]}> </ProtectedRoute>
export default function ProtectedRoute({ roles, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />; // no logueado
  if (roles && !roles.includes(user.rol)) return <Navigate to="/" replace />; // rol sin permiso
  
  return children;
}