DROP DATABASE IF EXISTS campeonato_universitario;
CREATE DATABASE campeonato_universitario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;
USE campeonato_universitario;

CREATE TABLE login (
    correo      VARCHAR(100) NOT NULL,
    contrasena  VARCHAR(255) NOT NULL,
    rol         ENUM('administrador', 'planillero') NOT NULL,
    CONSTRAINT pk_login PRIMARY KEY (correo)
);

CREATE TABLE facultad (
    id_facultad INT          NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT pk_facultad PRIMARY KEY (id_facultad),
    CONSTRAINT uq_facultad_nombre UNIQUE (nombre)
);

CREATE TABLE jugador (
    ci                VARCHAR(8)   NOT NULL,
    nombre            VARCHAR(50)  NOT NULL,
    apellido          VARCHAR(50)  NOT NULL,
    email             VARCHAR(100) NOT NULL,
    fecha_nacimiento  DATE         NOT NULL,
    id_facultad       INT          NOT NULL,
    tipo              ENUM('grado', 'posgrado', 'docente', 'funcionario') NOT NULL,
    CONSTRAINT pk_jugador PRIMARY KEY (ci),
    CONSTRAINT uq_jugador_email UNIQUE (email),
    CONSTRAINT fk_jugador_facultad FOREIGN KEY (id_facultad)
        REFERENCES facultad (id_facultad)
);

CREATE TABLE torneo (
    id_torneo     INT          NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(100) NOT NULL,
    anio          SMALLINT     NOT NULL,
    semestre      TINYINT      NOT NULL,
    fecha_inicio  DATE         NOT NULL,
    fecha_fin     DATE         NOT NULL,
    estado        ENUM('inscripción', 'en curso', 'finalizado') NOT NULL DEFAULT 'inscripción',
    CONSTRAINT pk_torneo PRIMARY KEY (id_torneo),
    CONSTRAINT uq_torneo UNIQUE (nombre, anio, semestre),
    CONSTRAINT ck_torneo_semestre CHECK (semestre IN (1, 2)),
    CONSTRAINT ck_torneo_fechas   CHECK (fecha_fin >= fecha_inicio)
);

CREATE TABLE equipo (
    id_equipo    INT          NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(100) NOT NULL,
    id_torneo    INT          NOT NULL,
    id_facultad  INT          NOT NULL,
    ci_capitan   VARCHAR(8)   NOT NULL,
    CONSTRAINT pk_equipo PRIMARY KEY (id_equipo),
    CONSTRAINT uq_equipo_torneo UNIQUE (id_equipo, id_torneo),
    CONSTRAINT uq_equipo_nombre_torneo UNIQUE (nombre, id_torneo),
    CONSTRAINT fk_equipo_torneo   FOREIGN KEY (id_torneo)   REFERENCES torneo (id_torneo),
    CONSTRAINT fk_equipo_facultad FOREIGN KEY (id_facultad) REFERENCES facultad (id_facultad),
    CONSTRAINT fk_equipo_capitan  FOREIGN KEY (ci_capitan)  REFERENCES jugador (ci)
);

CREATE TABLE equipo_jugador_torneo (
    id_equipo        INT        NOT NULL,
    ci_jugador       VARCHAR(8) NOT NULL,
    id_torneo        INT        NOT NULL,
    numero_camiseta  TINYINT    NOT NULL,
    CONSTRAINT pk_ejt PRIMARY KEY (ci_jugador, id_torneo),
    CONSTRAINT uq_ejt_camiseta UNIQUE (id_equipo, numero_camiseta),
    CONSTRAINT ck_ejt_camiseta CHECK (numero_camiseta BETWEEN 1 AND 99),
    CONSTRAINT fk_ejt_equipo  FOREIGN KEY (id_equipo, id_torneo)
        REFERENCES equipo (id_equipo, id_torneo),
    CONSTRAINT fk_ejt_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci)
);

CREATE TABLE complejo (
    id_complejo   INT          NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(100) NOT NULL,
    direccion     VARCHAR(150) NOT NULL,
    departamento  VARCHAR(50)  NOT NULL,
    CONSTRAINT pk_complejo PRIMARY KEY (id_complejo)
);

CREATE TABLE cancha (
    nombre_cancha  VARCHAR(50) NOT NULL,
    id_complejo    INT         NOT NULL,
    superficie     ENUM('sintético', 'parquet') NOT NULL,
    techada        BOOLEAN     NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_cancha PRIMARY KEY (nombre_cancha, id_complejo),
    CONSTRAINT fk_cancha_complejo FOREIGN KEY (id_complejo)
        REFERENCES complejo (id_complejo)
        ON DELETE CASCADE
);

CREATE TABLE turno (
    id_turno     INT  NOT NULL AUTO_INCREMENT,
    hora_inicio  TIME NOT NULL,
    hora_fin     TIME NOT NULL,
    CONSTRAINT pk_turno PRIMARY KEY (id_turno),
    CONSTRAINT uq_turno UNIQUE (hora_inicio, hora_fin),
    CONSTRAINT ck_turno_horas CHECK (hora_fin > hora_inicio)
);

CREATE TABLE partido (
    id_partido           INT         NOT NULL AUTO_INCREMENT,
    id_torneo            INT         NOT NULL,
    numero_fecha         TINYINT     NOT NULL,
    id_equipo_local      INT         NOT NULL,
    id_equipo_visitante  INT         NOT NULL,
    dia                  DATE        NOT NULL,
    id_turno             INT         NOT NULL,
    nombre_cancha        VARCHAR(50) NOT NULL,
    id_complejo          INT         NOT NULL,
    estado               ENUM('programado', 'jugado', 'postergado', 'cancelado')
                         NOT NULL DEFAULT 'programado',
    CONSTRAINT pk_partido PRIMARY KEY (id_partido),
    CONSTRAINT uq_partido_cancha_turno UNIQUE (dia, id_turno, nombre_cancha, id_complejo),
    CONSTRAINT ck_partido_equipos CHECK (id_equipo_local <> id_equipo_visitante),
    CONSTRAINT ck_partido_fecha   CHECK (numero_fecha >= 1),
    CONSTRAINT fk_partido_torneo  FOREIGN KEY (id_torneo) REFERENCES torneo (id_torneo),
    CONSTRAINT fk_partido_local FOREIGN KEY (id_equipo_local, id_torneo)
        REFERENCES equipo (id_equipo, id_torneo),
    CONSTRAINT fk_partido_visitante FOREIGN KEY (id_equipo_visitante, id_torneo)
        REFERENCES equipo (id_equipo, id_torneo),
    CONSTRAINT fk_partido_turno  FOREIGN KEY (id_turno) REFERENCES turno (id_turno),
    CONSTRAINT fk_partido_cancha FOREIGN KEY (nombre_cancha, id_complejo)
        REFERENCES cancha (nombre_cancha, id_complejo)
        ON UPDATE CASCADE
);

CREATE TABLE planilla_partido (
    id_partido  INT        NOT NULL,
    ci_jugador  VARCHAR(8) NOT NULL,
    id_equipo   INT        NOT NULL,
    CONSTRAINT pk_planilla PRIMARY KEY (id_partido, ci_jugador),
    CONSTRAINT fk_planilla_partido FOREIGN KEY (id_partido)
        REFERENCES partido (id_partido) ON DELETE CASCADE,
    CONSTRAINT fk_planilla_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
    CONSTRAINT fk_planilla_equipo  FOREIGN KEY (id_equipo)  REFERENCES equipo (id_equipo)
);

CREATE TABLE gol (
    id_gol      INT        NOT NULL AUTO_INCREMENT,
    id_partido  INT        NOT NULL,
    ci_jugador  VARCHAR(8) NOT NULL,
    minuto      TINYINT    NOT NULL,
    autogol     BOOLEAN    NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_gol PRIMARY KEY (id_gol),
    CONSTRAINT ck_gol_minuto CHECK (minuto BETWEEN 0 AND 130),
    CONSTRAINT fk_gol_planilla FOREIGN KEY (id_partido, ci_jugador)
        REFERENCES planilla_partido (id_partido, ci_jugador) ON DELETE CASCADE
);

CREATE TABLE tarjeta (
    id_tarjeta  INT        NOT NULL AUTO_INCREMENT,
    id_partido  INT        NOT NULL,
    ci_jugador  VARCHAR(8) NOT NULL,
    minuto      TINYINT    NOT NULL,
    color       ENUM('amarilla', 'roja') NOT NULL,
    CONSTRAINT pk_tarjeta PRIMARY KEY (id_tarjeta),
    CONSTRAINT ck_tarjeta_minuto CHECK (minuto BETWEEN 0 AND 130),
    CONSTRAINT fk_tarjeta_planilla FOREIGN KEY (id_partido, ci_jugador)
        REFERENCES planilla_partido (id_partido, ci_jugador) ON DELETE CASCADE
);

CREATE TABLE sancion_jugador (
    id_sancion           INT        NOT NULL AUTO_INCREMENT,
    ci_jugador           VARCHAR(8) NOT NULL,
    id_torneo            INT        NOT NULL,
    motivo               ENUM('roja', 'acumulación de amarillas', 'disciplinaria') NOT NULL,
    numero_fecha_inicio  TINYINT    NOT NULL,
    cantidad_fechas      TINYINT    NOT NULL,
    CONSTRAINT pk_sancion PRIMARY KEY (id_sancion),
    CONSTRAINT ck_sancion_inicio   CHECK (numero_fecha_inicio >= 1),
    CONSTRAINT ck_sancion_cantidad CHECK (cantidad_fechas >= 1),
    CONSTRAINT fk_sancion_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
    CONSTRAINT fk_sancion_torneo  FOREIGN KEY (id_torneo)  REFERENCES torneo (id_torneo)
);

USE campeonato_universitario;
DELIMITER $$

CREATE TRIGGER campeonato_universitario.trg_planilla_valida
BEFORE INSERT ON planilla_partido
FOR EACH ROW
BEGIN
    DECLARE v_torneo INT;
    DECLARE v_local INT;
    DECLARE v_visitante INT;

    SELECT id_torneo, id_equipo_local, id_equipo_visitante
      INTO v_torneo, v_local, v_visitante
      FROM partido
     WHERE id_partido = NEW.id_partido;

    IF NEW.id_equipo NOT IN (v_local, v_visitante) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El equipo no juega este partido';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM equipo_jugador_torneo
         WHERE ci_jugador = NEW.ci_jugador
           AND id_equipo  = NEW.id_equipo
           AND id_torneo  = v_torneo
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El jugador no está inscripto en ese equipo para este torneo';
    END IF;
END$$

CREATE TRIGGER campeonato_universitario.trg_capitan_facultad
BEFORE INSERT ON equipo
FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM jugador
         WHERE ci = NEW.ci_capitan
           AND id_facultad = NEW.id_facultad
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El capitán debe pertenecer a la facultad del equipo';
    END IF;
END$$

CREATE TRIGGER campeonato_universitario.trg_roja_genera_sancion
AFTER INSERT ON tarjeta
FOR EACH ROW
BEGIN
    DECLARE v_torneo INT;
    DECLARE v_fecha  TINYINT;

    IF NEW.color = 'roja' THEN
        SELECT id_torneo, numero_fecha INTO v_torneo, v_fecha
          FROM partido WHERE id_partido = NEW.id_partido;

        INSERT INTO sancion_jugador
            (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
        VALUES
            (NEW.ci_jugador, v_torneo, 'roja', v_fecha + 1, 1);
    END IF;
END$$

DELIMITER ;