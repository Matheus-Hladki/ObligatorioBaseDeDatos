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

<!-- Plantilla para nuevas entradas:

## DD/MM/AAAA — Título

### Qué se hizo

### Decisiones tomadas y por qué

### Problemas encontrados

-->