-- Cross-post pointers (`450` pages) and the article each one redirected to, resolved once. A
-- pointer that did not redirect to an article has no target and stays a link item.
CREATE TABLE pointer (
    url text PRIMARY KEY,
    target text,
    resolved_at timestamptz NOT NULL
);
