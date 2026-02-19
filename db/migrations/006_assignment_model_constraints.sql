CREATE TABLE IF NOT EXISTS room_assignment (
    assignment_id SERIAL PRIMARY KEY,
    room_id INT REFERENCES room(room_id),
    student_id INT REFERENCES student(student_id),
    assigned_date DATE DEFAULT CURRENT_DATE
);

ALTER TABLE room_assignment
ADD COLUMN IF NOT EXISTS assigned_date DATE DEFAULT CURRENT_DATE;

UPDATE room_assignment
SET assigned_date = CURRENT_DATE
WHERE assigned_date IS NULL;

DELETE FROM room_assignment older
USING room_assignment newer
WHERE older.student_id = newer.student_id
  AND older.assignment_id < newer.assignment_id;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'room_assignment_student_id_key'
    ) THEN
        ALTER TABLE room_assignment
        ADD CONSTRAINT room_assignment_student_id_key UNIQUE (student_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_room_assignment_student_id ON room_assignment(student_id);
CREATE INDEX IF NOT EXISTS idx_room_assignment_room_id ON room_assignment(room_id);
