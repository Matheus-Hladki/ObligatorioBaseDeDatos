USE campeonato_universitario;

DELIMITER $$

CREATE PROCEDURE sp_validar_plantel(
    IN p_id_equipo  INT,
    IN p_ci_jugador VARCHAR(8),
    IN p_id_torneo  INT,
    IN p_excluir_ci VARCHAR(8)
)
BEGIN
    DECLARE v_estado        VARCHAR(20);
    DECLARE v_fac_equipo    INT;
    DECLARE v_fac_jugador   INT;
    DECLARE v_tipo          VARCHAR(20);
    DECLARE v_cant          INT;
    DECLARE v_cant_doc_func INT;

    SELECT estado INTO v_estado FROM torneo WHERE id_torneo = p_id_torneo;
    IF v_estado <> 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El plantel solo puede modificarse con el torneo en etapa de inscripción';
    END IF;

    SELECT id_facultad INTO v_fac_equipo FROM equipo WHERE id_equipo = p_id_equipo;
    SELECT id_facultad, tipo INTO v_fac_jugador, v_tipo FROM jugador WHERE ci = p_ci_jugador;
    IF v_fac_equipo <> v_fac_jugador THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El jugador debe pertenecer a la facultad que representa el equipo';
    END IF;

    SELECT COUNT(*),
           COALESCE(SUM(j.tipo IN ('docente', 'funcionario')), 0)
      INTO v_cant, v_cant_doc_func
      FROM equipo_jugador_torneo e
      JOIN jugador j ON j.ci = e.ci_jugador
     WHERE e.id_equipo = p_id_equipo
       AND e.ci_jugador <> COALESCE(p_excluir_ci, '');

    IF v_cant >= 10 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El plantel no puede tener más de 10 jugadores';
    END IF;

    IF v_tipo IN ('docente', 'funcionario') AND v_cant_doc_func >= 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El plantel admite como máximo 2 docentes o funcionarios';
    END IF;
END$$

CREATE TRIGGER trg_plantel_insert
BEFORE INSERT ON equipo_jugador_torneo
FOR EACH ROW
BEGIN
    CALL sp_validar_plantel(NEW.id_equipo, NEW.ci_jugador, NEW.id_torneo, NULL);
END$$

CREATE TRIGGER trg_plantel_update
BEFORE UPDATE ON equipo_jugador_torneo
FOR EACH ROW
BEGIN
    DECLARE v_estado_viejo VARCHAR(20);

    SELECT estado INTO v_estado_viejo FROM torneo WHERE id_torneo = OLD.id_torneo;
    IF v_estado_viejo <> 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El plantel solo puede modificarse con el torneo en etapa de inscripción';
    END IF;

    CALL sp_validar_plantel(NEW.id_equipo, NEW.ci_jugador, NEW.id_torneo, OLD.ci_jugador);
END$$

CREATE TRIGGER trg_plantel_delete
BEFORE DELETE ON equipo_jugador_torneo
FOR EACH ROW
BEGIN
    IF (SELECT estado FROM torneo WHERE id_torneo = OLD.id_torneo) <> 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El plantel solo puede modificarse con el torneo en etapa de inscripción';
    END IF;
END$$

CREATE TRIGGER trg_equipo_insert
BEFORE INSERT ON equipo
FOR EACH ROW
BEGIN
    IF (SELECT estado FROM torneo WHERE id_torneo = NEW.id_torneo) <> 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Solo se pueden inscribir equipos con el torneo en etapa de inscripción';
    END IF;
END$$

CREATE TRIGGER trg_equipo_update
BEFORE UPDATE ON equipo
FOR EACH ROW
BEGIN
    IF NEW.ci_capitan IS NULL
       AND (SELECT estado FROM torneo WHERE id_torneo = NEW.id_torneo) <> 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Fuera de la etapa de inscripción todo equipo debe tener capitán';
    END IF;

    IF NEW.id_facultad <> OLD.id_facultad
       AND EXISTS (SELECT 1 FROM equipo_jugador_torneo WHERE id_equipo = OLD.id_equipo) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede cambiar la facultad de un equipo que ya tiene plantel';
    END IF;
END$$

CREATE TRIGGER trg_jugador_update
BEFORE UPDATE ON jugador
FOR EACH ROW
BEGIN
    IF NEW.id_facultad <> OLD.id_facultad
       AND EXISTS (SELECT 1 FROM equipo_jugador_torneo WHERE ci_jugador = OLD.ci) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede cambiar la facultad de un jugador que integra un plantel';
    END IF;

    IF NEW.tipo IN ('docente', 'funcionario')
       AND OLD.tipo NOT IN ('docente', 'funcionario')
       AND EXISTS (
           SELECT 1
             FROM equipo_jugador_torneo e
            WHERE e.ci_jugador = OLD.ci
              AND (SELECT COUNT(*)
                     FROM equipo_jugador_torneo e2
                     JOIN jugador j ON j.ci = e2.ci_jugador
                    WHERE e2.id_equipo = e.id_equipo
                      AND e2.ci_jugador <> OLD.ci
                      AND j.tipo IN ('docente', 'funcionario')) >= 2
       ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El cambio de tipo deja un plantel con más de 2 docentes o funcionarios';
    END IF;
END$$

CREATE TRIGGER trg_torneo_update
BEFORE UPDATE ON torneo
FOR EACH ROW
BEGIN
    IF NEW.estado <> OLD.estado AND NOT (
           (OLD.estado = 'inscripción' AND NEW.estado = 'en curso')
        OR (OLD.estado = 'en curso'    AND NEW.estado = 'finalizado')
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El torneo solo avanza de inscripción a en curso y de en curso a finalizado';
    END IF;

    IF OLD.estado = 'inscripción' AND NEW.estado = 'en curso' THEN
        IF EXISTS (SELECT 1 FROM equipo
                    WHERE id_torneo = OLD.id_torneo AND ci_capitan IS NULL) THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'No se puede iniciar el torneo: hay equipos sin capitán';
        END IF;
        IF EXISTS (SELECT 1 FROM equipo e
                    WHERE e.id_torneo = OLD.id_torneo
                      AND (SELECT COUNT(*) FROM equipo_jugador_torneo x
                            WHERE x.id_equipo = e.id_equipo) < 5) THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'No se puede iniciar el torneo: hay equipos con menos de 5 jugadores';
        END IF;
    END IF;

    IF OLD.estado = 'en curso' AND NEW.estado = 'finalizado'
       AND EXISTS (SELECT 1 FROM partido
                    WHERE id_torneo = OLD.id_torneo
                      AND estado IN ('programado', 'postergado')) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede finalizar el torneo: quedan partidos programados o postergados';
    END IF;


    IF (NEW.fecha_inicio <> OLD.fecha_inicio OR NEW.fecha_fin <> OLD.fecha_fin)
       AND EXISTS (SELECT 1 FROM partido
                    WHERE id_torneo = OLD.id_torneo
                      AND dia NOT BETWEEN NEW.fecha_inicio AND NEW.fecha_fin) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Las nuevas fechas del torneo dejan partidos fuera de su rango';
    END IF;
END$$

CREATE PROCEDURE sp_validar_partido(
    IN p_id_partido INT,
    IN p_id_torneo  INT,
    IN p_fecha      TINYINT,
    IN p_local      INT,
    IN p_visitante  INT,
    IN p_estado     VARCHAR(20)
)
BEGIN
    IF (SELECT estado FROM torneo WHERE id_torneo = p_id_torneo) = 'finalizado' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se pueden programar ni modificar partidos de un torneo finalizado';
    END IF;

    IF p_estado <> 'cancelado' THEN

        IF EXISTS (SELECT 1 FROM equipo
                    WHERE id_equipo IN (p_local, p_visitante)
                      AND ci_capitan IS NULL) THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Ambos equipos deben tener capitán designado';
        END IF;

        IF (SELECT COUNT(*) FROM equipo_jugador_torneo WHERE id_equipo = p_local) < 5
           OR (SELECT COUNT(*) FROM equipo_jugador_torneo WHERE id_equipo = p_visitante) < 5 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Ambos equipos deben tener al menos 5 jugadores en su plantel';
        END IF;

        IF EXISTS (
            SELECT 1 FROM partido
             WHERE id_torneo = p_id_torneo
               AND id_partido <> p_id_partido
               AND estado <> 'cancelado'
               AND LEAST(id_equipo_local, id_equipo_visitante)    = LEAST(p_local, p_visitante)
               AND GREATEST(id_equipo_local, id_equipo_visitante) = GREATEST(p_local, p_visitante)
        ) THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Estos equipos ya tienen un partido en esta edición (no cancelado)';
        END IF;

        IF EXISTS (
            SELECT 1 FROM partido
             WHERE id_torneo = p_id_torneo
               AND numero_fecha = p_fecha
               AND id_partido <> p_id_partido
               AND estado <> 'cancelado'
               AND (id_equipo_local     IN (p_local, p_visitante)
                 OR id_equipo_visitante IN (p_local, p_visitante))
        ) THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Uno de los equipos ya tiene un partido en esta fecha del torneo';
        END IF;

    END IF;
END$$

CREATE PROCEDURE sp_validar_jugado(IN p_id_torneo INT, IN p_dia DATE, IN p_id_turno INT)
BEGIN
    DECLARE v_fin TIME;

    IF (SELECT estado FROM torneo WHERE id_torneo = p_id_torneo) <> 'en curso' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un partido solo puede marcarse como jugado con el torneo en curso';
    END IF;

    SELECT hora_fin INTO v_fin FROM turno WHERE id_turno = p_id_turno;
    IF TIMESTAMP(p_dia, v_fin) > UTC_TIMESTAMP() - INTERVAL 3 HOUR THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un partido solo puede marcarse como jugado después de su día y turno';
    END IF;
END$$

CREATE PROCEDURE sp_validar_dia_torneo(IN p_id_torneo INT, IN p_dia DATE)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM torneo
                    WHERE id_torneo = p_id_torneo
                      AND p_dia BETWEEN fecha_inicio AND fecha_fin) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El partido debe jugarse entre la fecha de inicio y la de fin del torneo';
    END IF;
END$$

CREATE TRIGGER trg_partido_insert
BEFORE INSERT ON partido
FOR EACH ROW
BEGIN
    CALL sp_validar_dia_torneo(NEW.id_torneo, NEW.dia);
    CALL sp_validar_partido(0, NEW.id_torneo, NEW.numero_fecha,
                            NEW.id_equipo_local, NEW.id_equipo_visitante, NEW.estado);
    IF NEW.estado = 'jugado' THEN
        CALL sp_validar_jugado(NEW.id_torneo, NEW.dia, NEW.id_turno);
    END IF;
END$$

CREATE TRIGGER trg_partido_update
BEFORE UPDATE ON partido
FOR EACH ROW
BEGIN
    IF OLD.estado = 'jugado' AND (
           NEW.estado <> 'jugado'
        OR NEW.id_torneo <> OLD.id_torneo
        OR NEW.numero_fecha <> OLD.numero_fecha
        OR NEW.id_equipo_local <> OLD.id_equipo_local
        OR NEW.id_equipo_visitante <> OLD.id_equipo_visitante
        OR NEW.dia <> OLD.dia
        OR NEW.id_turno <> OLD.id_turno
        OR NEW.nombre_cancha <> OLD.nombre_cancha
        OR NEW.id_complejo <> OLD.id_complejo
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un partido jugado no puede modificarse';
    END IF;

    IF OLD.estado = 'cancelado' AND NEW.estado <> 'cancelado' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un partido cancelado no puede reactivarse; programe un partido nuevo';
    END IF;

    CALL sp_validar_dia_torneo(NEW.id_torneo, NEW.dia);
    CALL sp_validar_partido(OLD.id_partido, NEW.id_torneo, NEW.numero_fecha,
                            NEW.id_equipo_local, NEW.id_equipo_visitante, NEW.estado);

    IF NEW.estado = 'jugado' AND OLD.estado <> 'jugado' THEN
        CALL sp_validar_jugado(NEW.id_torneo, NEW.dia, NEW.id_turno);
    END IF;
END$$

CREATE TRIGGER trg_partido_reprogramacion
AFTER UPDATE ON partido
FOR EACH ROW
BEGIN
    IF NOT (OLD.dia = NEW.dia
            AND OLD.id_turno = NEW.id_turno
            AND OLD.nombre_cancha = NEW.nombre_cancha
            AND OLD.id_complejo = NEW.id_complejo) THEN
        INSERT INTO partido_reprogramacion
            (id_partido, dia_anterior, id_turno_anterior,
             nombre_cancha_anterior, id_complejo_anterior, estado_anterior, motivo)
        VALUES
            (OLD.id_partido, OLD.dia, OLD.id_turno,
             OLD.nombre_cancha, OLD.id_complejo, OLD.estado, @motivo_reprogramacion);
        SET @motivo_reprogramacion = NULL;
    END IF;
END$$

CREATE TRIGGER trg_partido_delete
BEFORE DELETE ON partido
FOR EACH ROW
BEGIN
    IF OLD.estado = 'jugado' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un partido jugado no puede eliminarse';
    END IF;
END$$

CREATE PROCEDURE sp_validar_planilla(
    IN p_id_partido INT,
    IN p_ci_jugador VARCHAR(8),
    IN p_id_equipo  INT
)
BEGIN
    DECLARE v_torneo    INT;
    DECLARE v_fecha     TINYINT;
    DECLARE v_local     INT;
    DECLARE v_visitante INT;
    DECLARE v_estado    VARCHAR(20);

    SELECT id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante, estado
      INTO v_torneo, v_fecha, v_local, v_visitante, v_estado
      FROM partido
     WHERE id_partido = p_id_partido;

    IF v_estado <> 'jugado' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Solo se puede registrar la planilla de un partido jugado';
    END IF;

    IF p_id_equipo NOT IN (v_local, v_visitante) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El equipo no juega este partido';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM equipo_jugador_torneo
         WHERE ci_jugador = p_ci_jugador
           AND id_equipo  = p_id_equipo
           AND id_torneo  = v_torneo
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El jugador no está inscripto en ese equipo para este torneo';
    END IF;

    IF EXISTS (
        SELECT 1 FROM sancion_jugador
         WHERE ci_jugador = p_ci_jugador
           AND id_torneo  = v_torneo
           AND v_fecha BETWEEN numero_fecha_inicio
                           AND numero_fecha_inicio + cantidad_fechas - 1
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El jugador está suspendido para esta fecha del torneo';
    END IF;
END$$

CREATE TRIGGER trg_planilla_insert
BEFORE INSERT ON planilla_partido
FOR EACH ROW
BEGIN
    CALL sp_validar_planilla(NEW.id_partido, NEW.ci_jugador, NEW.id_equipo);
END$$

CREATE TRIGGER trg_planilla_update
BEFORE UPDATE ON planilla_partido
FOR EACH ROW
BEGIN
    CALL sp_validar_planilla(NEW.id_partido, NEW.ci_jugador, NEW.id_equipo);
END$$

CREATE PROCEDURE sp_recalcular_acumulacion(IN p_ci VARCHAR(8), IN p_id_torneo INT)
BEGIN
    DELETE FROM sancion_jugador
     WHERE ci_jugador = p_ci
       AND id_torneo  = p_id_torneo
       AND motivo     = 'acumulación de amarillas';

    INSERT INTO sancion_jugador
        (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas, id_tarjeta)
    SELECT p_ci, p_id_torneo, 'acumulación de amarillas', x.numero_fecha + 1, 1, x.id_tarjeta
      FROM (
            SELECT t.id_tarjeta,
                   p.numero_fecha,
                   ROW_NUMBER() OVER (ORDER BY p.numero_fecha, p.dia, tu.hora_inicio,
                                               t.minuto, t.id_tarjeta) AS n
              FROM tarjeta t
              JOIN partido p ON p.id_partido = t.id_partido
              JOIN turno tu  ON tu.id_turno  = p.id_turno
             WHERE t.ci_jugador = p_ci
               AND p.id_torneo  = p_id_torneo
               AND t.color      = 'amarilla'
           ) x
     WHERE x.n % 3 = 0;
END$$

CREATE PROCEDURE sp_sancion_roja(IN p_id_tarjeta INT, IN p_ci VARCHAR(8), IN p_id_partido INT)
BEGIN
    DECLARE v_torneo INT;
    DECLARE v_fecha  TINYINT;

    SELECT id_torneo, numero_fecha INTO v_torneo, v_fecha
      FROM partido WHERE id_partido = p_id_partido;

    INSERT INTO sancion_jugador
        (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas, id_tarjeta)
    VALUES
        (p_ci, v_torneo, 'roja', v_fecha + 1, 1, p_id_tarjeta);
END$$

CREATE TRIGGER trg_tarjeta_insert
AFTER INSERT ON tarjeta
FOR EACH ROW
BEGIN
    IF NEW.color = 'roja' THEN
        CALL sp_sancion_roja(NEW.id_tarjeta, NEW.ci_jugador, NEW.id_partido);
    ELSE
        CALL sp_recalcular_acumulacion(NEW.ci_jugador,
            (SELECT id_torneo FROM partido WHERE id_partido = NEW.id_partido));
    END IF;
END$$

CREATE TRIGGER trg_tarjeta_update
AFTER UPDATE ON tarjeta
FOR EACH ROW
BEGIN
    DELETE FROM sancion_jugador
     WHERE id_tarjeta = NEW.id_tarjeta AND motivo = 'roja';
    IF NEW.color = 'roja' THEN
        CALL sp_sancion_roja(NEW.id_tarjeta, NEW.ci_jugador, NEW.id_partido);
    END IF;

    CALL sp_recalcular_acumulacion(OLD.ci_jugador,
        (SELECT id_torneo FROM partido WHERE id_partido = OLD.id_partido));
    CALL sp_recalcular_acumulacion(NEW.ci_jugador,
        (SELECT id_torneo FROM partido WHERE id_partido = NEW.id_partido));
END$$

CREATE TRIGGER trg_tarjeta_delete
AFTER DELETE ON tarjeta
FOR EACH ROW
BEGIN
    IF OLD.color = 'amarilla' THEN
        CALL sp_recalcular_acumulacion(OLD.ci_jugador,
            (SELECT id_torneo FROM partido WHERE id_partido = OLD.id_partido));
    END IF;
END$$

CREATE PROCEDURE sp_validar_sancion(
    IN p_motivo     VARCHAR(30),
    IN p_id_tarjeta INT
)
BEGIN
    DECLARE v_color VARCHAR(10);

    IF p_motivo = 'disciplinaria' THEN
        IF p_id_tarjeta IS NOT NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Una sanción disciplinaria no se asocia a una tarjeta';
        END IF;
    ELSE
        IF p_id_tarjeta IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Las sanciones por roja o acumulación se generan automáticamente a partir de las tarjetas';
        END IF;
        SELECT color INTO v_color FROM tarjeta WHERE id_tarjeta = p_id_tarjeta;
        IF (p_motivo = 'roja' AND v_color <> 'roja')
           OR (p_motivo = 'acumulación de amarillas' AND v_color <> 'amarilla') THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El motivo de la sanción no coincide con el color de la tarjeta';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_sancion_insert
BEFORE INSERT ON sancion_jugador
FOR EACH ROW
BEGIN
    CALL sp_validar_sancion(NEW.motivo, NEW.id_tarjeta);
END$$

CREATE TRIGGER trg_sancion_update
BEFORE UPDATE ON sancion_jugador
FOR EACH ROW
BEGIN
    CALL sp_validar_sancion(NEW.motivo, NEW.id_tarjeta);
END$$

DELIMITER ;