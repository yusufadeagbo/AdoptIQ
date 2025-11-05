CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE INDEX IF NOT EXISTS idx_users_wallet_address_trgm ON users USING gin(wallet_address gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_missions_created_at ON missions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_participations_verified_at ON participations(verified_at DESC);
CREATE INDEX IF NOT EXISTS idx_audits_completed_at ON audits(completed_at DESC);
