-- Renditions and tags (openspec/changes/add-rendering/design.md, "Renditions and tags").

CREATE TABLE rendition (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    revision_id bigint NOT NULL REFERENCES revision,
    prompt_version integer NOT NULL,
    model text NOT NULL,
    rendered_at timestamptz NOT NULL DEFAULT now(),
    fallback boolean NOT NULL,
    title text NOT NULL,
    markdown text NOT NULL,
    summary text,
    deadline date,
    UNIQUE (revision_id, prompt_version)
);

ALTER TABLE announcement ADD COLUMN current_rendition bigint REFERENCES rendition;

CREATE TABLE tag (
    announcement_id bigint NOT NULL REFERENCES announcement,
    dimension text NOT NULL CHECK (dimension IN ('topic', 'audience', 'nature', 'source')),
    tag text NOT NULL,
    set_by text NOT NULL CHECK (set_by IN ('model', 'manual')),
    PRIMARY KEY (announcement_id, dimension, tag)
);
CREATE INDEX tag_tag ON tag (dimension, tag);

ALTER TABLE event DROP CONSTRAINT event_kind_check;
ALTER TABLE event ADD CONSTRAINT event_kind_check
    CHECK (kind IN ('published', 'revised', 'withdrawn', 'restored', 'rendered'));
