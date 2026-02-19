-- Ensure admin assignment features can track assigned roommate IDs.
-- Safe to run multiple times.

DO $$
BEGIN
    -- Handle legacy typo if it exists in older schemas.
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'roommate_request'
          AND column_name = 'assigned_roomate_id'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'roommate_request'
          AND column_name = 'assigned_roommate_id'
    ) THEN
        ALTER TABLE roommate_request
        RENAME COLUMN assigned_roomate_id TO assigned_roommate_id;
    END IF;
END $$;

ALTER TABLE roommate_request
ADD COLUMN IF NOT EXISTS assigned_roommate_id INT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'roommate_request_assigned_roommate_id_fkey'
    ) THEN
        ALTER TABLE roommate_request
        ADD CONSTRAINT roommate_request_assigned_roommate_id_fkey
        FOREIGN KEY (assigned_roommate_id) REFERENCES student(student_id);
    END IF;
END $$;
