BEGIN TRANSACTION;
CREATE TABLE start_year_lookup (
    data_file str,
    start_year int
);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('classic', 1901);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('eraofsolitude.b1', 1167);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('eraofsolitude.b1.1', 1167);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('eraofsolitude.chaos', 1167);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('faerundip.0.7', 1371);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('helladip.0.2', -549);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('helladip.0.3', -549);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.0.1', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.0', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.1', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.2', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.2.chaos', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.2.fow', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.4', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.5', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.1.6', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.2.0', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.2.2', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.2.3', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.2.4', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('impdip.2.5', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('maddip.0.2', 1949);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('pelopondip.2.2', -430);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('planiglobii.0.2', 1801);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('seismicimpdip.2.0', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('southernimpdip.0.3', 1642);
INSERT INTO start_year_lookup (data_file, start_year) VALUES ('southernimpdip.0.4', 1642);

CREATE TABLE phase_lookup (
    phase_name str,
    phase_index int
);
INSERT INTO phase_lookup (phase_name, phase_index) VALUES ('Spring Moves', 0);
INSERT INTO phase_lookup (phase_name, phase_index) VALUES ('Spring Retreats', 1);
INSERT INTO phase_lookup (phase_name, phase_index) VALUES ('Fall Moves', 2);
INSERT INTO phase_lookup (phase_name, phase_index) VALUES ('Fall Retreats', 3);
INSERT INTO phase_lookup (phase_name, phase_index) VALUES ('Winter Builds', 4);

UPDATE boards
    SET phase_index = 5 * (sy.start_year + CAST(SUBSTR(boards.phase, 1, INSTR(boards.phase, ' ') - 1) AS INTEGER)) + pl.phase_index
    FROM start_year_lookup AS sy, phase_lookup AS pl
    WHERE sy.data_file = boards.data_file AND pl.phase_name = SUBSTR(boards.phase, INSTR(boards.phase, ' ') + 1);
UPDATE provinces SET phase_index = (SELECT phase_index FROM boards WHERE boards.board_id = provinces.board_id AND boards.phase = provinces.phase);
UPDATE retreat_options SET phase_index = (SELECT phase_index FROM boards WHERE boards.board_id = retreat_options.board_id AND boards.phase = retreat_options.phase);
UPDATE units SET phase_index = (SELECT phase_index FROM boards WHERE boards.board_id = units.board_id AND boards.phase = units.phase);
UPDATE builds SET phase_index = (SELECT phase_index FROM boards WHERE boards.board_id = builds.board_id AND boards.phase = builds.phase);
UPDATE dp_orders SET phase_index = (SELECT phase_index FROM boards WHERE boards.board_id = dp_orders.board_id AND boards.phase = dp_orders.phase);

DROP TABLE start_year_lookup;
DROP TABLE phase_lookup;
COMMIT;