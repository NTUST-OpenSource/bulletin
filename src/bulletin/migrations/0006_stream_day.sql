-- The stream day (openspec/changes/add-public-api/design.md, "Stream day, stored").

-- The list date; else the list date of the dated article with the nearest article id, since ids
-- grow with time across the sites; else the day the announcement was first seen in Taipei.
CREATE FUNCTION stream_day(article bigint, listed date, seen timestamptz) RETURNS date
LANGUAGE sql STABLE AS $$
    SELECT COALESCE(
        listed,
        (SELECT n.listed_on FROM (
            (SELECT b.listed_on, b.article_id - article AS gap FROM announcement b
             WHERE b.listed_on IS NOT NULL AND b.article_id >= article
             ORDER BY b.article_id LIMIT 1)
            UNION ALL
            (SELECT b.listed_on, article - b.article_id FROM announcement b
             WHERE b.listed_on IS NOT NULL AND b.article_id < article
             ORDER BY b.article_id DESC LIMIT 1)
        ) n ORDER BY n.gap LIMIT 1),
        (seen AT TIME ZONE 'Asia/Taipei')::date
    )
$$;

ALTER TABLE announcement ADD COLUMN dated date;
UPDATE announcement SET dated = stream_day(article_id, listed_on, first_seen_at);
ALTER TABLE announcement ALTER COLUMN dated SET NOT NULL;

-- Every stored announcement gets its day here, whichever path stores it; listed_on never changes
-- after the insert, and the nightly upkeep estimates undated ones again (archive.redate).
CREATE FUNCTION announcement_stream_day() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.dated := stream_day(NEW.article_id, NEW.listed_on, NEW.first_seen_at);
    RETURN NEW;
END
$$;
CREATE TRIGGER announcement_stream_day BEFORE INSERT ON announcement
    FOR EACH ROW EXECUTE FUNCTION announcement_stream_day();

CREATE INDEX announcement_stream ON announcement (dated DESC, id DESC) WHERE cross_post_of IS NULL;
CREATE INDEX announcement_cross_post_of ON announcement (cross_post_of);
CREATE INDEX placement_announcement ON placement (announcement_id);
