BEGIN TRANSACTION;
ALTER TABLE builds RENAME TO builds_old;


CREATE TABLE IF NOT EXISTS builds (
    board_id int,
    phase text,
    player text,
    location text,
    order_type text,
    unit_type text,
    failed_order bool,
    PRIMARY KEY (board_id, phase, player, location),
    FOREIGN KEY (board_id, phase) REFERENCES boards (board_id, phase),
    FOREIGN KEY (board_id, player) REFERENCES players (board_id, player_name),
    FOREIGN KEY (board_id, phase, location) REFERENCES provinces (board_id, phase, province_name)
);

INSERT INTO builds (board_id, phase, player, location, order_type, unit_type, failed_order)
SELECT board_id, phase, player, location, order_type, unit_type, "false" FROM builds_old;

DROP TABLE builds_old;
COMMIT;