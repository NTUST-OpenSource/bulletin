-- Articles without a list date (openspec/changes/date-undated-articles/design.md).

-- The pick query dates such an article by the dated article with the nearest id, above or below.
CREATE INDEX announcement_dated_article ON announcement (article_id) WHERE listed_on IS NOT NULL;
