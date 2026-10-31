USE campeonato_universitario;

DROP USER IF EXISTS 'torneo_auth'@'%';
DROP USER IF EXISTS 'torneo_admin'@'%';
DROP USER IF EXISTS 'torneo_planillero'@'%';

CREATE USER 'torneo_auth'@'%'       IDENTIFIED BY 'auth_dev_2026';
CREATE USER 'torneo_admin'@'%'      IDENTIFIED BY 'admin_dev_2026';
CREATE USER 'torneo_planillero'@'%' IDENTIFIED BY 'planillero_dev_2026';

GRANT SELECT ON campeonato_universitario.login TO 'torneo_auth'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE ON campeonato_universitario.* TO 'torneo_admin'@'%';

GRANT SELECT ON campeonato_universitario.facultad               TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.jugador                TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.torneo                 TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.equipo                 TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.equipo_jugador_torneo  TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.complejo               TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.cancha                 TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.turno                  TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.partido                TO 'torneo_planillero'@'%';
GRANT SELECT ON campeonato_universitario.sancion_jugador        TO 'torneo_planillero'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON campeonato_universitario.planilla_partido TO 'torneo_planillero'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON campeonato_universitario.gol              TO 'torneo_planillero'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON campeonato_universitario.tarjeta          TO 'torneo_planillero'@'%';

FLUSH PRIVILEGES;