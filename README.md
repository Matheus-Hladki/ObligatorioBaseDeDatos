# Obligatorio Base De Datos
## Torneo interfacultades de Fútbol 5

Sistema para gestionar y organizar equipos, planteles, fixture, planillas de juego, sanciones y reportes del torneo.

### Integrantes
- Agustina Berrutti: responsable del frontend.
- Emilio Falcone: responsable del backend.
- Matheus Hladki: responsable de la base de datos.

### Tecnologías
| **Componentes** | **Tecnologías** |
| :--- | :--- |
| **Base de Datos** | MySQL |
| **Backend** | Python (FastAPI) |
| **Frontend** | React |
| **Contenedores** | Docker |

### Bitácora e Informe
Tanto el informe como la bitácora se encuentran en la carpeta documentos.

### Requisitos para correrlo
#### Con Docker
Requisitos: Docker y Docker Compose.
1. Abrir Docker Compose
2. Desde la raíz del repositorio:
   ```
   docker compose up --build
   ```
La primera vez, MySQL ejecuta solos `tables.sql`, `triggers.sql`, `users.sql` y `data.sql`, y el backend crea los usuarios de la tabla de abajo. Cuando termine de levantar:
- Aplicación: http://localhost:5173
- API y documentación interactiva: http://localhost:8000/docs
- MySQL desde el host: puerto `3307` (usuario `root`, contraseña `root_dev_2026`)

Para apagar: `docker compose down`. Para borrar también los datos y recargar la base desde cero: `docker compose down -v`.

#### Sin Docker
Requisitos: MySQL 8.0, Python 3.12 y Node.js 22 o superior.

1. **Base de Datos en MySQL:** 
Ejecutar, en este orden, los scripts de `base_de_datos/`: `tables.sql`, `triggers.sql`, `users.sql` y `data.sql`. Desde la consola de MySQL (conectado como root):
   ```
   source C:/ruta/al/repo/base_de_datos/tables.sql
   source C:/ruta/al/repo/base_de_datos/triggers.sql
   source C:/ruta/al/repo/base_de_datos/users.sql
   source C:/ruta/al/repo/base_de_datos/data.sql
   ```

2. **Backend:**
1. En la carpeta `backend/`, crear el entorno virtual e instalar las dependencias:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Copiar `backend/.env.example` como `backend/.env` y completar las contraseñas de los usuarios de MySQL (están en `base_de_datos/users.sql`). Para `JWT_SECRET`, generar una clave con:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Crear el usuario administrador de la tabla de abajo:
   ```
   python crear_admin.py
   ```
4. Levantar el servidor:
   ```
   uvicorn main:app --reload
   ```
5. Abrir la documentación interactiva en http://localhost:8000/docs. Para usar los endpoints protegidos, iniciar sesión con `POST /login`, copiar el `token` de la respuesta y pegarlo en el botón **Authorize**.
6. Crear el usuario planillero de la tabla de abajo con `POST /usuarios`, autenticado como administrador.

3. **Frontend:**
En la carpeta `frontend/`, crear e instalar las dependencias, y levantar la aplicación:
   ```
   npm install
   npm run dev
   ```
La aplicación queda en http://localhost:5173. Por defecto llama al backend en `http://localhost:8000`.
En cualquier caso, para cambiarlo, copiar `.env.example` como `.env` y editar `VITE_API_URL`. Con `npm run build` se genera la versión de producción en `dist/`.

### Usuarios
| **Rol** | **Correo** | **Contraseña** | **Permisos**
| :--- | :--- | :--- | :--- |
| Administrador | admin@correo.ucu.edu.uy | adminUCU | Gestiona toda la información del torneo |
| Planillero | planilleros@correo.ucu.edu.uy | planillerosUCU | Solo registra las planillas, goles y tarjetas de los partidos |