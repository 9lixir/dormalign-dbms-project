-- Align student-to-user mapping with app queries.
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

ALTER TABLE student
ADD COLUMN IF NOT EXISTS user_id INT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'student_user_id_key'
    ) THEN
        ALTER TABLE student
        ADD CONSTRAINT student_user_id_key UNIQUE (user_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'student_user_id_fkey'
    ) THEN
        ALTER TABLE student
        ADD CONSTRAINT student_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;
