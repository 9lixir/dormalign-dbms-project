-- Remove duplicate rows for the same logical pair, including reversed order.
-- Keep the newest score_id row.
DELETE FROM compatibility_score older
USING compatibility_score newer
WHERE LEAST(older.student1_id, older.student2_id) = LEAST(newer.student1_id, newer.student2_id)
  AND GREATEST(older.student1_id, older.student2_id) = GREATEST(newer.student1_id, newer.student2_id)
  AND older.score_id < newer.score_id;

-- Normalize student pair ordering in compatibility_score so student1_id <= student2_id.
UPDATE compatibility_score
SET student1_id = LEAST(student1_id, student2_id),
    student2_id = GREATEST(student1_id, student2_id)
WHERE student1_id IS NOT NULL
  AND student2_id IS NOT NULL
  AND student1_id > student2_id;

-- Enforce pair uniqueness
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'compatibility_score_pair_key'
    ) THEN
        ALTER TABLE compatibility_score
        ADD CONSTRAINT compatibility_score_pair_key UNIQUE (student1_id, student2_id);
    END IF;
END $$;

-- Optional index to support unordered pair lookups.
CREATE UNIQUE INDEX IF NOT EXISTS uq_compatibility_pair
ON compatibility_score (
    LEAST(student1_id, student2_id),
    GREATEST(student1_id, student2_id)
);
