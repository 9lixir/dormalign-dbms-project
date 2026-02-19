-- Add email if old DB does not have it
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(200);

-- Add role so we can mark admins
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student';

-- Add optional profile picture path
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255);
