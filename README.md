# bulletin

NTUST announcements in one place. bulletin polls the announcement boards of the university's
offices and departments, keeps every announcement for ten years (also after the school withdraws
it), and serves them at `bulletin.ntust.org` through a public API and a web frontend with search.

It is an unofficial service, not run by the university.

Status: the collector (`add-collector`, under `openspec/changes/`) is being built; the public API
and the frontend follow. The plan is in `docs/roadmap.md`.

Contributors start with `AGENTS.md`.

## Deployment

The Compose project `bulletin` (`compose.yaml`) runs two containers: `bulletin-db`, PostgreSQL 18
with PGroonga, and `bulletin-internal`, one process that serves the public listener (`:8000`), the
admin listener (`bulletin-internal-admin:8001`) and the worker that polls the school. No ports are
published; nginx-proxy-manager reaches the public listener over the external network `proxy-net`.

1. Create `proxy-net` once if the host does not have it: `docker network create proxy-net`.
2. `cp .env.example .env`, then set `POSTGRES_PASSWORD` and `BULLETIN_ADMIN_TOKENS`.
3. `docker compose up -d --build`. The first start applies the migrations and adds the boards of
   `seeds/boards.json`; later starts add only boards the registry does not hold.
4. `docker compose ps` shows `bulletin-internal` as healthy once `/health` answers.

To update, pull and run `docker compose up -d --build` again. `docker compose down` stops the
stack; the `pgdata` and `files` volumes keep the archive and the stored attachments.

### Settings

| Variable | Default | Meaning |
| --- | --- | --- |
| `POSTGRES_PASSWORD` | (required) | The database password, in hex, since it goes into a URL. |
| `BULLETIN_ADMIN_TOKENS` | none | Admin API tokens, comma-separated `name:token` pairs; tokens have 32 or more characters. |
| `BULLETIN_DATABASE_URL` | set by `compose.yaml` | The PostgreSQL URL. |
| `BULLETIN_ADMIN_HOST` | set by `compose.yaml` | The address the admin listener binds to. |
| `BULLETIN_FILES` | `/data/files` | Where stored attachment files go. |
| `BULLETIN_SEED` | `/app/seeds/boards.json` | The boards added on start. |

### Operator commands

The CLI works on the database directly. Boards are named `<site>-<board>`, such as `1053-1435`.

```sh
docker compose exec app bulletin boards                    # every board: key, tier, category, name
docker compose exec app bulletin boards --tier P1
docker compose exec app bulletin boards --pending          # discovered boards awaiting review
docker compose exec app bulletin tier set 1053-1435 P2 --by owner
docker compose exec app bulletin tier history 1053-1435
docker compose exec app bulletin review accept 1053-2000 --tier P4 --category announcement
docker compose exec app bulletin discover                  # queue a re-discovery of every site
```

A tier change takes effect at the next scheduling pass. A board turned on from `off` is queued
for backfill.

### Admin API

The admin listener answers only on the internal network `bulletin_bulletin-admin`, and every
request needs one of the bearer tokens; changes are recorded under the token's name.

| Request | Body | Answer |
| --- | --- | --- |
| `GET /admin/boards?tier=P1&pending=true` | | the boards, filters optional |
| `GET /admin/boards/pending` | | discovered boards awaiting review |
| `PUT /admin/boards/{site}-{board}/tier` | `{"tier": "P2"}` | 204 |
| `GET /admin/boards/{site}-{board}/tier-changes` | | the board's tier changes |
| `POST /admin/boards/{site}-{board}/review` | `{"tier": "P4", "category": "announcement"}`, both optional | 204 |

```sh
docker run --rm --network bulletin_bulletin-admin curlimages/curl -s \
  -H "Authorization: Bearer ${TOKEN}" "http://bulletin-internal-admin:8001/admin/boards?tier=P1"
```
