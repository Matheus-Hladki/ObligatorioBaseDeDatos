# Bitácora — Obligatorio Bases de Datos I

## 31/10/2026 — Subida de la base de datos al repositorio

### Qué se hizo

Se subió al repositorio la base de datos con la que se va a desarrollar el proyecto. La base ya estaba hecha de antes; hoy se incorporó al repositorio para empezar a llevar el control de versiones a partir de ella.

La base implementa las estructuras que pide la letra (`login`, `facultad`, `jugador`, `torneo`, `equipo`, `equipo_jugador_torneo`, `complejo`, `cancha`, `turno`, `partido`, `planilla_partido`, `gol`, `tarjeta` y `sancion_jugador`).

### Archivos

| Archivo | Contenido |
|---|---|
| `db/01_schema.sql` | Creación de la base y de las tablas, con sus claves y restricciones |
| `db/02_triggers.sql` | Triggers |
| `db/04_seed.sql` | Datos maestros y de prueba |

### Datos de prueba

- 3 torneos: uno finalizado, uno en curso (el que tiene los datos) y uno en etapa de inscripción.
- 6 facultades con 7 jugadores cada una, y 6 equipos en el torneo en curso.
- 3 complejos deportivos con 5 canchas en total.
- Fixture a una rueda: fechas 1 a 3 jugadas, fechas 4 y 5 programadas.
- Planillas, goles, tarjetas y sanciones de los partidos jugados.

---

 
## 31/10/2026 — Revisión de la base contra la letra y corrección
 
### Qué se hizo
 
Se revisó la base contra cada regla de la letra y se encontraron 18 problemas. Se corrigieron en la base todos menos uno (la ventana de 48 horas, que queda en el backend). Los scripts se probaron en MySQL 8.0 desde una base vacía, verificando que cada regla rechace los casos inválidos.
 
Se agregaron los usuarios de MySQL por rol, en un archivo propio.

Además, se reorganizaron los scripts de la base en la carpeta `base_de_datos/`:

| Archivo | Contenido |
|---|---|
| `tables.sql` | Creación de la base y de las tablas, con sus claves y restricciones |
| `triggers.sql` | Triggers y procedimientos con las reglas de negocio |
| `users.sql` | Usuarios de MySQL por rol y sus permisos |
| `data.sql` | Datos maestros y de prueba |

Se separó en un archivo por responsabilidad para que cada parte sea fácil de encontrar y revisar, y para que cada cambio quede aislado en el historial de commits (por ejemplo, agregar un trigger no toca el archivo de las tablas). Los nombres describen el contenido de cada archivo.

 
### Problemas encontrados
 
1. La letra dice que dos equipos no pueden volver a enfrentarse salvo que su partido anterior se haya cancelado. Nosotros teníamos un partido que se volvió a jugar porque se había postergado, cargado como un partido nuevo. Entonces, cuando agregáramos el control de "no se juega dos veces salvo cancelado", nuestros propios datos iban a fallar. Además, esos dos equipos quedaban con dos partidos en la misma fecha.
2. El trigger del capitán chequeaba que el capitán fuera de la misma facultad que el equipo, pero la letra pide que sea uno de los jugadores del plantel. Por ejemplo, se podía poner como capitán de Ingenieros FC a alguien de Ingeniería que jugaba en otro equipo. Y no se podía arreglar solo cambiando el trigger, porque el equipo necesitaba el capitán antes de tener plantel y el plantel necesitaba que el equipo existiera.
3. El control de que el jugador sea de la misma facultad que el equipo estaba solo para el capitán, no para el resto. Un estudiante de Salud podía ser jugador (no capitán) de Ingenieros FC.
4. No había límite de jugadores por plantel (máximo 10) ni del máximo de 2 docentes o funcionarios en total.
5. El plantel se podía editar en cualquier momento, cuando solo debería poder hacerse en la etapa de inscripción.
6. El trigger de la planilla no chequeaba que el jugador no estuviera suspendido. Un jugador con una roja podía figurar en la planilla de la fecha siguiente, que es justamente el problema que el sistema tiene que resolver.
7. Al programar un partido no se chequeaba que los dos equipos tuvieran al menos 5 jugadores.
8. Un equipo podía jugar más de un partido en la misma fecha.
9. Se podía programar un partido entre los mismos dos equipos todas las veces que se quisiera; lo único que se exigía era que fuera en otro día, turno o cancha. En realidad, dos equipos pueden tener como máximo un partido no cancelado por edición.
10. Un partido del año que viene se podía marcar como "jugado" y cargarle planilla y goles. Hay que mirar el día y el turno antes de dejar cambiar el estado.
11. Un partido jugado no debería poder eliminarse, y se podía.
12. Faltaba el control de que el resultado solo se pueda corregir dentro de las 48 horas posteriores al partido.
13. Faltaba la suspensión automática por acumulación de 3 amarillas.
14. Si se ponía una tarjeta roja por error y después se borraba (o se cambiaba a amarilla), la tarjeta desaparecía pero la sanción quedaba.
15. Los triggers eran solo de insert, no de update: con un update se podían ignorar. Algunas reglas también se podían romper desde otra tabla, por ejemplo cambiando la facultad de un jugador que ya estaba en un plantel.
16. No había seguridad a nivel de base como pide la letra: el script no creaba usuarios de MySQL por rol con permisos distintos, así que la base no rechazaba nada de lo que un rol no debería poder hacer.
17. Faltaba el turno de 22:00 a 23:00.
18. Había una sanción por acumulación de amarillas a un jugador que tenía solo 2 amarillas, cuando deberían ser 3. Estaba cargada a mano porque no existía el trigger de acumulación.
### Decisiones tomadas y por qué
 
- **Postergación como cambio del mismo partido.** Un partido postergado no es un enfrentamiento nuevo: se actualizan día, turno y cancha de la misma fila. Para no perder la trazabilidad se agregó la tabla `partido_reprogramacion`, que un trigger completa con los datos anteriores cada vez que cambia el lugar o la hora. El motivo se toma de la variable de sesión `@motivo_reprogramacion`, que setea el backend.
- **Capitán nullable con FK al plantel.** `ci_capitan` pasó a admitir `NULL` y tiene una FK compuesta `(id_equipo, ci_capitan)` hacia el plantel. El equipo se crea sin capitán, se arma el plantel y después se designa. MySQL no tiene constraints diferidas, así que es la forma de exigir que el capitán sea jugador de su equipo. La misma FK impide sacar del plantel al capitán sin designar otro antes. Un equipo sin capitán solo puede existir durante la inscripción: el capitán se exige para programar partidos y para iniciar el torneo, y fuera de la inscripción no se puede dejar a un equipo sin capitán.
- **Reglas en INSERT y UPDATE.** Cada validación se escribió como procedimiento y se llama desde los triggers de inserción y de modificación, para que no se pueda saltear cambiando la fila después. También se controlan cambios en otras tablas que romperían una regla (por ejemplo, cambiar la facultad de un jugador que integra un plantel).
- **Partidos cancelados.** No cuentan para las reglas de rival repetido ni de un partido por fecha, según la excepción de la letra. Un partido cancelado es definitivo: para jugar ese enfrentamiento se programa uno nuevo.
- **Partido jugado cerrado.** Un partido jugado no se puede eliminar ni cambiar de estado, equipos, fecha ni lugar. Las correcciones del resultado se hacen sobre goles y tarjetas.
- **"Ya se jugó" = terminó el turno.** Un partido puede marcarse como jugado cuando pasó la hora de fin de su turno. La hora se calcula como UTC − 3 h, para no depender de la zona horaria del servidor.
- **Sanciones ligadas a su tarjeta.** Se agregó `id_tarjeta` a `sancion_jugador`. Si se borra la tarjeta, la sanción se borra con ella (`ON DELETE CASCADE`). Las sanciones por roja o acumulación solo pueden existir asociadas a una tarjeta del color correcto; las disciplinarias, sin tarjeta.
- **Acumulación cada 3 amarillas.** Se sanciona en la 3.ª, 6.ª, 9.ª amarilla de la edición. Las sanciones por acumulación se recalculan desde cero ante cualquier cambio en las tarjetas del jugador, para que sigan siendo correctas aunque se borre una amarilla del medio.
- **Usuarios de MySQL por rol.** `torneo_auth` solo lee `login` (para el inicio de sesión), `torneo_admin` opera sobre todas las tablas y `torneo_planillero` solo escribe planillas, goles y tarjetas. Los triggers se ejecutan con los permisos de quien los creó, así que la sanción por roja se genera aunque el planillero no tenga permiso sobre `sancion_jugador`.
- **48 horas en el backend.** La ventana de corrección se implementa en el backend: es una regla de proceso más que de consistencia, y en la base impediría cargar los datos históricos.
- **Estados del torneo.** El torneo solo avanza: inscripción → en curso → finalizado. Así los planteles no pueden reabrirse en pleno torneo. Para pasar a "en curso" todos los equipos tienen que tener capitán y al menos 5 jugadores, y para finalizar no pueden quedar partidos programados ni postergados. Solo se inscriben equipos durante la inscripción, los partidos solo se marcan como jugados con el torneo en curso y no se programan partidos en un torneo finalizado.
- **Contraseñas con bcrypt desde el backend.** Las contraseñas de `login` se guardan con bcrypt en lugar de SHA-256 sin sal. El hash lo calcula el backend en Python, así la contraseña en texto plano nunca llega a MySQL. Por eso los datos de prueba no incluyen usuarios: se crean desde el backend.
- **Torneo único por semestre.** Se cambió el `UNIQUE` de `torneo` a `(anio, semestre)`, porque cada edición corresponde a un semestre.
- **Validaciones de formato.** Se agregaron `CHECK` para que los turnos estén entre las 18:00 y las 23:00 y para el formato de la cédula. El minuto de goles y tarjetas pasó a `TINYINT UNSIGNED`, porque con `TINYINT` el tipo no admitía todo el rango que permitía el `CHECK`.
### Cambios en los datos de prueba
 
- Se eliminó el partido duplicado de la postergación; el partido original se reprogramó con un `UPDATE` y quedó registrado en el historial.
- Se canceló un partido de la fecha 4, para que el reporte de cancelados tenga datos.
- Se agregó una tercera amarilla a un jugador; la sanción por acumulación ahora la genera el trigger.
- Se agregaron dos jugadores inscriptos que nunca figuraron en una planilla, para el reporte correspondiente.
- Se agregó el turno de 22:00 a 23:00.
- Facultades, correos y nombres adaptados a la UCU.
- El torneo en curso se carga en estado de inscripción, se arman los planteles y después pasa a "en curso", igual que en el uso real.
- Se quitaron los usuarios de `login`: se van a crear desde el backend con bcrypt.

## 03/11/2026 — Decisiones de diseño del equipo

### Qué se hizo

Se definieron en equipo varios puntos que la letra deja abiertos (consultados con el docente, que indicó que son decisiones de diseño), y se ajustó la base para reflejarlos.

### Decisiones tomadas y por qué

- **Una facultad puede inscribir más de un equipo por edición.** La letra no lo prohíbe. La base ya lo permitía: solo exige que el nombre del equipo no se repita en la edición. Como un jugador puede estar en un solo equipo por edición, dos equipos de la misma facultad nunca comparten jugadores.
- **Un partido postergado sigue bloqueando el cruce entre los dos equipos.** Mientras está postergado, cuenta como partido no cancelado: esos equipos no pueden tener otro partido entre sí ni otro partido en esa fecha del torneo, y conserva su día, turno y cancha originales. Cuando se reprograma, se actualizan esos datos y los anteriores quedan en el historial. No suma para posiciones ni goleadores hasta que se juega. El backend puede sugerir el siguiente turno disponible, pero la reprogramación la confirma el administrador.
- **Los partidos se juegan entre la fecha de inicio y la de fin del torneo.** Se agregó el control en la base. Si un partido se suspende en la última fecha y hay que jugarlo después, el administrador extiende la fecha de fin del torneo y luego lo reprograma; así la regla no tiene excepciones y la extensión queda registrada en los datos. Tampoco se pueden cambiar las fechas del torneo si eso deja partidos fuera del rango.
- **Se puede cambiar la cancha de un partido ya programado**, mientras no se haya jugado y la cancha nueva esté libre en ese día y turno. Para que un cambio de cancha no cuente como postergación, el historial de reprogramaciones ahora guarda el estado que tenía el partido al moverse (`estado_anterior`). El reporte de postergados cuenta solo los partidos que se movieron estando postergados.
- **El login es solo para administradores y planilleros**, que son los dos roles que pide la letra. Los jugadores no tienen usuario y no pueden editar sus datos.

### Cambios en los archivos

- `tables.sql`: columna `estado_anterior` en `partido_reprogramacion`.
- `triggers.sql`: control de que el día del partido esté dentro del rango del torneo (al programar y al modificar), control al cambiar las fechas del torneo, y registro del estado anterior en el historial de reprogramaciones.

## 04/11/2026 — Inicio del backend

### Qué se hizo

- Se mergeó la rama de la base de datos a `main` y se creó la rama `backend`.
- Se estudió cómo estructurar el backend y cómo funciona FastAPI.
- Se configuró el entorno virtual de Python y se creó un endpoint de prueba (`GET /hola`) para verificar que el servidor funciona.
- Se agregó un `.gitignore` para excluir el entorno virtual, la caché de Python y el archivo `.env`.

## 04/11/2026 — Conexión a la base y estructura del backend

### Qué se hizo

- Se conectó el backend a MySQL usando el usuario `torneo_admin`, con las credenciales en un archivo `.env` que no se sube al repositorio (se incluye un `.env.example` con las variables necesarias).
- Se organizó el backend en capas: `db.py` para la conexión, `repositories/` para las consultas SQL y `routes/` para los endpoints.
- Se creó el primer endpoint que lee datos de la base: `GET /facultades`.
- Se configuró VS Code para usar el entorno virtual del proyecto.

## 04/11/2026 — ABM de facultades

### Qué se hizo

- Se completó el ABM de facultades: listar, obtener una, crear, modificar y borrar.
- Se validan los datos recibidos con modelos de Pydantic (respuesta `422` si no son válidos).
- Se traducen los errores de la base a respuestas claras: `404` si la facultad no existe, `409` si el nombre ya está usado o si la facultad tiene jugadores o equipos asociados.
- Se detectó que MySQL informa el error de clave foránea con códigos distintos según los privilegios del usuario (`1451` o `1217`), y se contemplan ambos.

## 04/11/2026 — Usuarios y conexión por rol

### Qué se hizo

- Se creó un script (`crear_admin.py`) para dar de alta el primer administrador, con la contraseña hasheada con bcrypt.
- La conexión a la base ahora usa el usuario de MySQL correspondiente a cada rol (`torneo_auth`, `torneo_admin`, `torneo_planillero`), con las credenciales en el `.env`. Se verificó que cada usuario solo puede hacer lo que sus permisos permiten.
- Se agregó la generación de tokens JWT con vencimiento de 8 horas, firmados con una clave secreta guardada en el `.env`.

## 05/11/2026 — Login y protección de endpoints

### Qué se hizo

- Se implementó el login (`POST /login`): verifica la contraseña con bcrypt y devuelve un token JWT con el correo y el rol. Ante un correo inexistente o una contraseña incorrecta responde lo mismo (`401`), para no revelar qué correos están registrados.
- Se protegieron los endpoints: sin sesión válida responden `401`, y sin el rol necesario, `403`.
- Facultades: cualquier usuario con sesión puede consultarlas, y solo un administrador puede crearlas, modificarlas o borrarlas.
- Cada pedido se conecta a MySQL con el usuario del rol de quien lo hace, así los permisos también los controla la base.
<!-- Plantilla para nuevas entradas:

## DD/MM/AAAA — Título

### Qué se hizo

### Decisiones tomadas y por qué

### Problemas encontrados

-->