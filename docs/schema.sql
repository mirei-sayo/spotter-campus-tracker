-- ============================================================
-- Spotter: Campus Lost & Found Tracker
-- Supabase PostgreSQL Schema
-- Run this in your Supabase SQL Editor (Project > SQL Editor > New query)
-- ============================================================


-- ─────────────────────────────────────────
-- 1. PROFILES TABLE
-- Stores user details and role after Supabase Auth signup
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT NOT NULL,
  full_name   TEXT NOT NULL,
  role        TEXT NOT NULL CHECK (role IN ('student', 'finder', 'faculty')),
  student_id  TEXT,
  department  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────
-- 2. ITEMS TABLE
-- Stores both lost and found item reports
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS items (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id    UUID REFERENCES profiles(id) ON DELETE SET NULL,
  type           TEXT NOT NULL CHECK (type IN ('lost', 'found')),
  title          TEXT NOT NULL,
  description    TEXT,
  category       TEXT NOT NULL,
  brand          TEXT,
  color          TEXT,
  location_found TEXT,
  image_url      TEXT,
  status         TEXT NOT NULL DEFAULT 'reported'
                   CHECK (status IN ('reported', 'found', 'reserved', 'claimed', 'closed')),
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_items_updated_at
  BEFORE UPDATE ON items
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ─────────────────────────────────────────
-- 3. CLAIMS TABLE
-- Links a Student claimant to a found Item
-- 48-hour reservation window
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claims (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id             UUID REFERENCES items(id) ON DELETE CASCADE,
  claimant_id         UUID REFERENCES profiles(id) ON DELETE CASCADE,
  status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
  proof_description   TEXT,
  reserved_at         TIMESTAMPTZ DEFAULT NOW(),
  expires_at          TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '48 hours'),
  resolved_by         UUID REFERENCES profiles(id),
  resolved_at         TIMESTAMPTZ
);


-- ─────────────────────────────────────────
-- 4. AUDIT LOG TABLE
-- Immutable record of all faculty/system actions
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id     UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action       TEXT NOT NULL,
  target_type  TEXT NOT NULL,
  target_id    UUID,
  details      JSONB DEFAULT '{}',
  created_at   TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────
-- 5. ROW LEVEL SECURITY (RLS)
-- ─────────────────────────────────────────

-- Enable RLS on all tables
ALTER TABLE profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE items      ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims     ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log  ENABLE ROW LEVEL SECURITY;


-- profiles: users can read any profile, but only edit their own
CREATE POLICY "Public profiles are viewable"
  ON profiles FOR SELECT USING (true);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE USING (auth.uid() = id);


-- items: everyone can read; authenticated users can insert; faculty/owner can update
CREATE POLICY "Items are publicly readable"
  ON items FOR SELECT USING (true);

CREATE POLICY "Authenticated users can report items"
  ON items FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Owner or faculty can update items"
  ON items FOR UPDATE USING (
    auth.uid() = reporter_id
    OR EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'faculty'
    )
  );

CREATE POLICY "Faculty can delete items"
  ON items FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'faculty'
    )
  );


-- claims: students see own; faculty sees all
CREATE POLICY "Students see own claims"
  ON claims FOR SELECT USING (
    auth.uid() = claimant_id
    OR EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'faculty'
    )
  );

CREATE POLICY "Students can create claims"
  ON claims FOR INSERT WITH CHECK (auth.uid() = claimant_id);

CREATE POLICY "Faculty can update claims"
  ON claims FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'faculty'
    )
  );


-- audit_log: faculty can read; server inserts via service role (bypasses RLS)
CREATE POLICY "Faculty can read audit log"
  ON audit_log FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'faculty'
    )
  );
