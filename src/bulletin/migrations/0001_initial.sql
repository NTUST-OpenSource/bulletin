-- The collector's tables (openspec/changes/add-collector/design.md, "Schema").

CREATE EXTENSION IF NOT EXISTS pgroonga WITH SCHEMA public;

CREATE TABLE site (
    site_id integer PRIMARY KEY,
    host text NOT NULL,
    unit text NOT NULL
);

CREATE TABLE board (
    site_id integer NOT NULL REFERENCES site,
    rcg integer NOT NULL,
    name text NOT NULL,
    category text NOT NULL
        CHECK (category IN ('announcement', 'news', 'regulation', 'course', 'excluded')),
    tier text NOT NULL CHECK (tier IN ('P1', 'P2', 'P3', 'P4', 'off')),
    pending_review boolean NOT NULL DEFAULT false,
    found_at timestamptz NOT NULL DEFAULT now(),
    fingerprint text,
    last_polled_at timestamptz,
    next_poll_at timestamptz,
    failures integer NOT NULL DEFAULT 0,
    backfill_page integer,
    backfilled_at timestamptz,
    PRIMARY KEY (site_id, rcg)
);
CREATE INDEX board_next_poll_at ON board (next_poll_at);

CREATE TABLE tier_change (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id integer NOT NULL,
    rcg integer NOT NULL,
    old_tier text NOT NULL,
    new_tier text NOT NULL,
    changed_by text NOT NULL,
    changed_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (site_id, rcg) REFERENCES board
);

-- site_id comes from the item's link and may name a site outside the registry, so no foreign key.
CREATE TABLE announcement (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id integer NOT NULL,
    host text NOT NULL,
    article_id bigint,
    link_url text,
    title text NOT NULL,
    publisher text,
    listed_on date,
    first_seen_at timestamptz NOT NULL DEFAULT now(),
    late boolean NOT NULL DEFAULT false,
    cross_post_of bigint REFERENCES announcement,
    withdrawn_at timestamptz,
    body_text text,
    current_revision bigint,
    UNIQUE (site_id, article_id),
    UNIQUE (site_id, link_url),
    CHECK (article_id IS NOT NULL OR link_url IS NOT NULL)
);
CREATE INDEX announcement_listed_on ON announcement (listed_on);
CREATE INDEX announcement_title ON announcement USING pgroonga (title);
CREATE INDEX announcement_body_text ON announcement USING pgroonga (body_text);

CREATE TABLE placement (
    site_id integer NOT NULL,
    rcg integer NOT NULL,
    announcement_id bigint NOT NULL REFERENCES announcement,
    listed_on date,
    first_seen_at timestamptz NOT NULL DEFAULT now(),
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    last_position integer,
    PRIMARY KEY (site_id, rcg, announcement_id),
    FOREIGN KEY (site_id, rcg) REFERENCES board
);

CREATE TABLE revision (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    announcement_id bigint NOT NULL REFERENCES announcement,
    fetched_at timestamptz NOT NULL DEFAULT now(),
    title text NOT NULL,
    body_html text NOT NULL,
    body_text text NOT NULL,
    content_hash text NOT NULL
);
ALTER TABLE announcement ADD FOREIGN KEY (current_revision) REFERENCES revision;

CREATE TABLE attachment (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    revision_id bigint NOT NULL REFERENCES revision,
    name text NOT NULL,
    url text NOT NULL,
    origin text NOT NULL CHECK (origin IN ('module', 'body')),
    size bigint,
    sha256 text
);

CREATE TABLE event (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    announcement_id bigint NOT NULL REFERENCES announcement,
    kind text NOT NULL CHECK (kind IN ('published', 'revised', 'withdrawn', 'restored')),
    notify boolean NOT NULL,
    late boolean NOT NULL DEFAULT false,
    at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE job (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind text NOT NULL CHECK (kind IN ('article', 'recheck', 'attachment', 'discovery', 'backfill')),
    ref text NOT NULL,
    run_after timestamptz NOT NULL DEFAULT now(),
    attempts integer NOT NULL DEFAULT 0,
    last_error text
);
CREATE INDEX job_run_after ON job (run_after);

CREATE TABLE poll (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purpose text NOT NULL,
    site_id integer,
    rcg integer,
    at timestamptz NOT NULL DEFAULT now(),
    status integer,
    bytes integer,
    ms integer,
    changed boolean,
    new_ids bigint[]
);
CREATE INDEX poll_at ON poll (at);

CREATE TABLE frontier (
    at timestamptz PRIMARY KEY,
    max_article_id bigint NOT NULL
);
