-- Fallbacks that failed on text like a placeholder or on a malformed link target
-- (openspec/changes/archive/2026-11-16-fix-rendering-fallbacks): drop them once, so their
-- announcements render again. Fallbacks hold no model tags; events stay.
UPDATE announcement a SET current_rendition = NULL
    FROM rendition n WHERE n.id = a.current_rendition AND n.fallback;
DELETE FROM rendition WHERE fallback;
