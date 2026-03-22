INSERT INTO room (hostel_id, room_number, capacity, current_occupancy)
SELECT 
    1,
    gs,
    CASE 
        WHEN gs <= 10 THEN 1
        ELSE 2
    END,
    0
FROM generate_series(1, 50) AS gs;

INSERT INTO room (hostel_id, room_number, capacity, current_occupancy)
SELECT 
    2,
    gs,
    CASE 
        WHEN gs <= 15 THEN 1
        ELSE 2
    END,
    0
FROM generate_series(1, 60) AS gs;