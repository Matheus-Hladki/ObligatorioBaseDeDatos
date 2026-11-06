# Obligatorio Base De Datos
## Torneo interfacultades de Fútbol 5

Sistema para gestionar y organizar equipos, planteles, fixture, planillas de juego, sanciones y reportes del torneo.

### Integrantes
- Agustina Berrutti
- Emilio Falcone
- Matheus Hladki

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
**Con Docker**
**Sin Docker**

Requisitos: MySQL 8.0 y Python 3.12.

1. Cargar la base en MySQL ejecutando, en este orden, los scripts de `base_de_datos/`: `tables.sql`, `triggers.sql`, `users.sql` y `data.sql`. Desde la consola de MySQL (conectado como root):
   ```
   source C:/ruta/al/repo/base_de_datos/tables.sql
   source C:/ruta/al/repo/base_de_datos/triggers.sql
   source C:/ruta/al/repo/base_de_datos/users.sql
   source C:/ruta/al/repo/base_de_datos/data.sql
   ```
2. En la carpeta `backend/`, crear el entorno virtual e instalar las dependencias:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Copiar `backend/.env.example` como `backend/.env` y completar las contraseñas de los usuarios de MySQL (están en `base_de_datos/users.sql`). Para `JWT_SECRET`, generar una clave con:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
4. Crear el usuario administrador de la tabla de abajo:
   ```
   python crear_admin.py
   ```
5. Levantar el servidor:
   ```
   uvicorn main:app --reload
   ```
6. Abrir la documentación interactiva en http://localhost:8000/docs. Para usar los endpoints protegidos, iniciar sesión con `POST /login`, copiar el `token` de la respuesta y pegarlo en el botón **Authorize**.
7. Crear el usuario planillero de la tabla de abajo con `POST /usuarios`, autenticado como administrador.

### Usuarios
| **Rol** | **Correo** | **Contraseña** | **Permisos**
| :--- | :--- | :--- | :--- |
| Administrador | admin@correo.ucu.edu.uy | adminUCU | Gestiona toda la información del torneo |
| Planillero | planilleros@correo.ucu.edu.uy | planillerosUCU | Solo registra las planillas, goles y tarjetas de los partidos |

### Preguntas y cosas que faltan
1. Definir las versiones de las tecnologías que vamos a usar
2. Completar bien los requisitos para correrlo
3. Completar mejor el informe, como donde impactan las cosas, ejemplo los datos confirmados y los supuestos
4. Insertar el diagrama entidad-relación
5. Confirmar que las consultas de posiciones y promedios apliquen el criterio de autogoles
6. Implementar `POST /usuarios` para que el administrador cree planilleros