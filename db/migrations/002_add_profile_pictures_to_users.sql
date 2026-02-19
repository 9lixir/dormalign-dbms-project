-- Add a new optional column to store relative image path.
ALTER TABLE users
ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255);
