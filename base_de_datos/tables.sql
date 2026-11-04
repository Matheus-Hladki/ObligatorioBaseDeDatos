DROP DATABASE IF EXISTS campeonato_universitario;

CREATE DATABASE campeonato_universitario CHARACTER
SET
    utf8mb4 COLLATE utf8mb4_spanish_ci;

USE campeonato_universitario;

CREATE TABLE
    login (
        correo VARCHAR(100) NOT NULL,
        contrasena VARCHAR(255) NOT NULL,
        rol ENUM ('administrador', 'planillero') NOT NULL,
        CONSTRAINT pk_login PRIMARY KEY (correo)
    );

CREATE TABLE
    facultad (
        id_facultad INT NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        CONSTRAINT pk_facultad PRIMARY KEY (id_facultad),
        CONSTRAINT uq_facultad_nombre UNIQUE (nombre)
    );

CREATE TABLE
    jugador (
        ci VARCHAR(8) NOT NULL,
        nombre VARCHAR(50) NOT NULL,
        apellido VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        fecha_nacimiento DATE NOT NULL,
        id_facultad INT NOT NULL,
        tipo ENUM ('grado', 'posgrado', 'docente', 'funcionario') NOT NULL,
        CONSTRAINT pk_jugador PRIMARY KEY (ci),
        CONSTRAINT uq_jugador_email UNIQUE (email),
        CONSTRAINT ck_jugador_ci CHECK (ci REGEXP '^[0-9]{7,8}$'),
        CONSTRAINT fk_jugador_facultad FOREIGN KEY (id_facultad) REFERENCES facultad (id_facultad)
    );

CREATE TABLE
    torneo (
        id_torneo INT NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        anio SMALLINT NOT NULL,
        semestre TINYINT NOT NULL,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE NOT NULL,
        estado ENUM ('inscripción', 'en curso', 'finalizado') NOT NULL DEFAULT 'inscripción',
        CONSTRAINT pk_torneo PRIMARY KEY (id_torneo),
        CONSTRAINT uq_torneo_semestre UNIQUE (anio, semestre),
        CONSTRAINT ck_torneo_semestre CHECK (semestre IN (1, 2)),
        CONSTRAINT ck_torneo_fechas CHECK (fecha_fin >= fecha_inicio)
    );

CREATE TABLE
    equipo (
        id_equipo INT NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        id_torneo INT NOT NULL,
        id_facultad INT NOT NULL,
        ci_capitan VARCHAR(8) NULL,
        CONSTRAINT pk_equipo PRIMARY KEY (id_equipo),
        CONSTRAINT uq_equipo_torneo UNIQUE (id_equipo, id_torneo),
        CONSTRAINT uq_equipo_nombre_torneo UNIQUE (nombre, id_torneo),
        CONSTRAINT fk_equipo_torneo FOREIGN KEY (id_torneo) REFERENCES torneo (id_torneo),
        CONSTRAINT fk_equipo_facultad FOREIGN KEY (id_facultad) REFERENCES facultad (id_facultad)
    );

CREATE TABLE
    equipo_jugador_torneo (
        id_equipo INT NOT NULL,
        ci_jugador VARCHAR(8) NOT NULL,
        id_torneo INT NOT NULL,
        numero_camiseta TINYINT NOT NULL,
        CONSTRAINT pk_ejt PRIMARY KEY (ci_jugador, id_torneo),
        CONSTRAINT uq_ejt_equipo_jugador UNIQUE (id_equipo, ci_jugador),
        CONSTRAINT uq_ejt_camiseta UNIQUE (id_equipo, numero_camiseta),
        CONSTRAINT ck_ejt_camiseta CHECK (numero_camiseta BETWEEN 1 AND 99),
        CONSTRAINT fk_ejt_equipo FOREIGN KEY (id_equipo, id_torneo) REFERENCES equipo (id_equipo, id_torneo),
        CONSTRAINT fk_ejt_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci)
    );

ALTER TABLE equipo ADD CONSTRAINT fk_equipo_capitan FOREIGN KEY (id_equipo, ci_capitan) REFERENCES equipo_jugador_torneo (id_equipo, ci_jugador);

CREATE TABLE
    complejo (
        id_complejo INT NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        direccion VARCHAR(150) NOT NULL,
        departamento VARCHAR(50) NOT NULL,
        CONSTRAINT pk_complejo PRIMARY KEY (id_complejo)
    );

CREATE TABLE
    cancha (
        nombre_cancha VARCHAR(50) NOT NULL,
        id_complejo INT NOT NULL,
        superficie ENUM ('sintético', 'parquet') NOT NULL,
        techada BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT pk_cancha PRIMARY KEY (nombre_cancha, id_complejo),
        CONSTRAINT fk_cancha_complejo FOREIGN KEY (id_complejo) REFERENCES complejo (id_complejo) ON DELETE CASCADE
    );

CREATE TABLE
    turno (
        id_turno INT NOT NULL AUTO_INCREMENT,
        hora_inicio TIME NOT NULL,
        hora_fin TIME NOT NULL,
        CONSTRAINT pk_turno PRIMARY KEY (id_turno),
        CONSTRAINT uq_turno UNIQUE (hora_inicio, hora_fin),
        CONSTRAINT ck_turno_horas CHECK (hora_fin > hora_inicio),
        CONSTRAINT ck_turno_rango CHECK (
            hora_inicio >= '18:00:00'
            AND hora_fin <= '23:00:00'
        )
    );

CREATE TABLE
    partido (
        id_partido INT NOT NULL AUTO_INCREMENT,
        id_torneo INT NOT NULL,
        numero_fecha TINYINT NOT NULL,
        id_equipo_local INT NOT NULL,
        id_equipo_visitante INT NOT NULL,
        dia DATE NOT NULL,
        id_turno INT NOT NULL,
        nombre_cancha VARCHAR(50) NOT NULL,
        id_complejo INT NOT NULL,
        estado ENUM ('programado', 'jugado', 'postergado', 'cancelado') NOT NULL DEFAULT 'programado',
        CONSTRAINT pk_partido PRIMARY KEY (id_partido),
        CONSTRAINT uq_partido_cancha_turno UNIQUE (dia, id_turno, nombre_cancha, id_complejo),
        CONSTRAINT ck_partido_equipos CHECK (id_equipo_local <> id_equipo_visitante),
        CONSTRAINT ck_partido_fecha CHECK (numero_fecha >= 1),
        CONSTRAINT fk_partido_torneo FOREIGN KEY (id_torneo) REFERENCES torneo (id_torneo),
        CONSTRAINT fk_partido_local FOREIGN KEY (id_equipo_local, id_torneo) REFERENCES equipo (id_equipo, id_torneo),
        CONSTRAINT fk_partido_visitante FOREIGN KEY (id_equipo_visitante, id_torneo) REFERENCES equipo (id_equipo, id_torneo),
        CONSTRAINT fk_partido_turno FOREIGN KEY (id_turno) REFERENCES turno (id_turno),
        CONSTRAINT fk_partido_cancha FOREIGN KEY (nombre_cancha, id_complejo) REFERENCES cancha (nombre_cancha, id_complejo) ON UPDATE CASCADE
    );

CREATE TABLE
    partido_reprogramacion (
        id_reprogramacion INT NOT NULL AUTO_INCREMENT,
        id_partido INT NOT NULL,
        dia_anterior DATE NOT NULL,
        id_turno_anterior INT NOT NULL,
        nombre_cancha_anterior VARCHAR(50) NOT NULL,
        id_complejo_anterior INT NOT NULL,
        estado_anterior ENUM ('programado', 'jugado', 'postergado', 'cancelado') NOT NULL,
        motivo VARCHAR(200) NULL,
        fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT pk_reprogramacion PRIMARY KEY (id_reprogramacion),
        CONSTRAINT fk_reprog_partido FOREIGN KEY (id_partido) REFERENCES partido (id_partido) ON DELETE CASCADE,
        CONSTRAINT fk_reprog_turno FOREIGN KEY (id_turno_anterior) REFERENCES turno (id_turno),
        CONSTRAINT fk_reprog_cancha FOREIGN KEY (nombre_cancha_anterior, id_complejo_anterior) REFERENCES cancha (nombre_cancha, id_complejo) ON UPDATE CASCADE
    );

CREATE TABLE
    planilla_partido (
        id_partido INT NOT NULL,
        ci_jugador VARCHAR(8) NOT NULL,
        id_equipo INT NOT NULL,
        CONSTRAINT pk_planilla PRIMARY KEY (id_partido, ci_jugador),
        CONSTRAINT fk_planilla_partido FOREIGN KEY (id_partido) REFERENCES partido (id_partido) ON DELETE CASCADE,
        CONSTRAINT fk_planilla_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
        CONSTRAINT fk_planilla_equipo FOREIGN KEY (id_equipo) REFERENCES equipo (id_equipo)
    );

CREATE TABLE
    gol (
        id_gol INT NOT NULL AUTO_INCREMENT,
        id_partido INT NOT NULL,
        ci_jugador VARCHAR(8) NOT NULL,
        minuto TINYINT UNSIGNED NOT NULL,
        autogol BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT pk_gol PRIMARY KEY (id_gol),
        CONSTRAINT ck_gol_minuto CHECK (minuto BETWEEN 0 AND 130),
        CONSTRAINT fk_gol_planilla FOREIGN KEY (id_partido, ci_jugador) REFERENCES planilla_partido (id_partido, ci_jugador) ON DELETE CASCADE
    );

CREATE TABLE
    tarjeta (
        id_tarjeta INT NOT NULL AUTO_INCREMENT,
        id_partido INT NOT NULL,
        ci_jugador VARCHAR(8) NOT NULL,
        minuto TINYINT UNSIGNED NOT NULL,
        color ENUM ('amarilla', 'roja') NOT NULL,
        CONSTRAINT pk_tarjeta PRIMARY KEY (id_tarjeta),
        CONSTRAINT uq_tarjeta_jugador UNIQUE (id_tarjeta, ci_jugador),
        CONSTRAINT ck_tarjeta_minuto CHECK (minuto BETWEEN 0 AND 130),
        CONSTRAINT fk_tarjeta_planilla FOREIGN KEY (id_partido, ci_jugador) REFERENCES planilla_partido (id_partido, ci_jugador) ON DELETE CASCADE
    );

CREATE TABLE
    sancion_jugador (
        id_sancion INT NOT NULL AUTO_INCREMENT,
        ci_jugador VARCHAR(8) NOT NULL,
        id_torneo INT NOT NULL,
        motivo ENUM (
            'roja',
            'acumulación de amarillas',
            'disciplinaria'
        ) NOT NULL,
        numero_fecha_inicio TINYINT NOT NULL,
        cantidad_fechas TINYINT NOT NULL,
        id_tarjeta INT NULL,
        CONSTRAINT pk_sancion PRIMARY KEY (id_sancion),
        CONSTRAINT uq_sancion_tarjeta UNIQUE (id_tarjeta),
        CONSTRAINT ck_sancion_inicio CHECK (numero_fecha_inicio >= 1),
        CONSTRAINT ck_sancion_cantidad CHECK (cantidad_fechas >= 1),
        CONSTRAINT fk_sancion_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
        CONSTRAINT fk_sancion_torneo FOREIGN KEY (id_torneo) REFERENCES torneo (id_torneo),
        CONSTRAINT fk_sancion_tarjeta FOREIGN KEY (id_tarjeta, ci_jugador) REFERENCES tarjeta (id_tarjeta, ci_jugador) ON DELETE CASCADE ON UPDATE CASCADE
    );