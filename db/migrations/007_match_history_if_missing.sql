CREATE TABLE IF NOT EXISTS match_history (
    match_id SERIAL PRIMARY KEY,
    student1_id INT,
    student2_id INT,
    room_id INT,
    compatibility_score INT,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    success_rating INT
);

ALTER TABLE match_history ADD COLUMN IF NOT EXISTS room_id INT;
ALTER TABLE match_history ADD COLUMN IF NOT EXISTS compatibility_score INT;
ALTER TABLE match_history ADD COLUMN IF NOT EXISTS start_date DATE DEFAULT CURRENT_DATE;
ALTER TABLE match_history ADD COLUMN IF NOT EXISTS end_date DATE;
ALTER TABLE match_history ADD COLUMN IF NOT EXISTS success_rating INT;

ALTER TABLE match_history
ALTER COLUMN start_date SET DEFAULT CURRENT_DATE;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'match_history_student1_id_fkey'
    ) THEN
        ALTER TABLE match_history
        ADD CONSTRAINT match_history_student1_id_fkey FOREIGN KEY (student1_id) REFERENCES student(student_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'match_history_student2_id_fkey'
    ) THEN
        ALTER TABLE match_history
        ADD CONSTRAINT match_history_student2_id_fkey FOREIGN KEY (student2_id) REFERENCES student(student_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'match_history_room_id_fkey'
    ) THEN
        ALTER TABLE match_history
        ADD CONSTRAINT match_history_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(room_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_match_history_pair_open ON match_history(student1_id, student2_id, end_date);
