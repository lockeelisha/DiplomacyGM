BEGIN TRANSACTION;
ALTER TABLE units RENAME TO units_old;

CREATE TABLE IF NOT EXISTS units (
    board_id int,
    phase text,
    location text,
    is_dislodged boolean,
    owner text,
    unit_type text,
    order_type text,
    order_destination text,
    order_source text,
    failed_order boolean,
    PRIMARY KEY (board_id, phase, location, is_dislodged),
    FOREIGN KEY (board_id, phase) REFERENCES boards (board_id, phase),
    FOREIGN KEY (board_id, phase, location) REFERENCES provinces (board_id, phase, province_name),
    FOREIGN KEY (board_id, owner) REFERENCES players (board_id, player_name),
    FOREIGN KEY (board_id, phase, location) REFERENCES retreat_options (board_id, phase, origin));

INSERT INTO units (board_id, phase, location, is_dislodged, owner, unit_type, order_type, order_destination, order_source, failed_order)
SELECT board_id, phase, location, is_dislodged, owner,
    CASE WHEN is_army = 1 THEN 'A' ELSE 'F' END,
    order_type, order_destination, order_source, failed_order
FROM units_old;

DROP TABLE units_old;
COMMIT;
