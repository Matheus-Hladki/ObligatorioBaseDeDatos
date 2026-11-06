import { useState } from "react";
import { api } from "../api/client.js";
import FormModal from "../components/FormModal.jsx";

const campos = [
  { name: "correo", label: "Correo", type: "email", requerido: true, maxLength: 100 },
  { name: "contrasena", label: "Contraseña", type: "password", requerido: true, maxLength: 100, validar: (v) => (v.length < 6 ? "Mínimo 6 caracteres" : null) },
  { name: "rol", label: "Rol", type: "select", requerido: true, options: [{ value: "planillero", label: "planillero" }, { value: "administrador", label: "administrador" }] },
];

export default function Usuarios() {
  const [abierto, setAbierto] = useState(false);
  const [creado, setCreado] = useState("");
  return (
    <>
      <h1>Usuarios</h1>
      <p>Creá usuarios que puedan iniciar sesión (planilleros o administradores)</p>
      <button onClick={() => { setCreado(""); setAbierto(true); }}>+ Nuevo usuario</button>
      {creado && <p className="ok">Usuario {creado} creado correctamente</p>}
      {abierto && (
        <FormModal
          titulo="Nuevo usuario"
          campos={campos}
          inicial={{ rol: "planillero" }}
          onSubmit={async (v) => { await api.post("/usuarios", v); setCreado(v.correo); }}
          onClose={() => setAbierto(false)}
        />
      )}
    </>
  );
}
