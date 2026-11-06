import { createContext, useContext, useState } from "react";
import { api } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  //leemos la sesión guardada para que sobreviva a recargar la página
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  async function login(correo, contrasena) {
    //asumo q el backend responde { token, rol } con rol "administrador" o "planillero"
    const { token, rol } = await api.login(correo, contrasena);
    const nuevoUser = { correo, rol };
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(nuevoUser));
    setUser(nuevoUser);
    return nuevoUser;
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook: const { user, login, logout } = useAuth();
export const useAuth = () => useContext(AuthContext);