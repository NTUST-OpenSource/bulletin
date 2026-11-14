-- When re-discovery last walked each site's site map. Sites already held count as walked now: the
-- seed came from a survey of their site maps.
ALTER TABLE site ADD COLUMN discovered_at timestamptz NOT NULL DEFAULT now();
