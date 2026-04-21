-- Run this command in your Supabase SQL Editor
ALTER TABLE claims ADD COLUMN IF NOT EXISTS proof_image_url TEXT;

ALTER TABLE items ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
UPDATE items SET is_verified = TRUE;
