-- Articles without a list date (openspec/changes/date-undated-articles/design.md).

-- The pick query dates such an article by the dated article with the nearest id, above or below.
CREATE INDEX announcement_dated_article ON announcement (article_id) WHERE listed_on IS NOT NULL;

-- Renditions made before were read against the day of the backfill: drop them once, with their
-- model tags, so the article renders again by its neighbour's day or stays raw. Events stay.
UPDATE announcement SET current_rendition = NULL
    WHERE listed_on IS NULL AND current_rendition IS NOT NULL;
DELETE FROM tag t USING announcement a
    WHERE t.announcement_id = a.id AND a.listed_on IS NULL AND t.set_by = 'model';
DELETE FROM rendition n USING revision r, announcement a
    WHERE n.revision_id = r.id AND r.announcement_id = a.id AND a.listed_on IS NULL;
