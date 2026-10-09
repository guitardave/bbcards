# BB Cards

BB Cards is a Django-based web application for cataloging and managing a personal sports-card collection. It helps collectors keep card sets, players, card details, images, and exportable collection lists organized in one searchable application.

Although the project is named for baseball cards, the data model supports baseball, football, and basketball sets.

## Features

- **Card-set management**
  - Create, edit, list, and remove card sets.
  - Track the set year, name, and sport.
  - Browse sets in year/name order.

- **Card cataloging**
  - Associate cards with a player and card set.
  - Record card numbers, subsets, condition, graded status, and images.
  - Automatically generate slugs for players, sets, and cards.
  - View recently added cards and browse the complete collection.

- **Player management**
  - Maintain a searchable, reusable player list.
  - Filter players included in or excluded from normal collection views.
  - Use player pages to browse cards associated with an individual player.

- **Search**
  - Search across card metadata, including year, set name, sport, subset, card number, and player name.
  - Uses PostgreSQL full-text search capabilities through Django's `SearchVector` and `SearchQuery` APIs.

- **AI card image finder**
  - An LLM agent (DigitalOcean Serverless Inference) searches the web for a photo of each card using Brave Image Search, then downloads, validates, and attaches the best match.
  - Use the **Image Manager** page (nav bar) to list cards with or without images and run the agent on a single card from its row; results update in place without a page reload.
  - Or use the **Find image** button on a card's image page, or fill in many cards at once with the `fetch_card_images` management command (see [AI image agent](#ai-image-agent)).

- **Images and exports**
  - Upload card images through Django's file-storage abstraction.
  - Card images are stored in AWS S3 (via `boto3` and `django-storages`) when AWS settings are present, and on local disk otherwise.
  - Export collection lists to Excel with `openpyxl`.
  - Export collection lists to PDF with `xhtml2pdf`.

- **Authentication and profiles**
  - Django authentication with login and logout support.
  - User profiles can store a favorite player.
  - User management and password-update views are included.
  - Authenticated API access supports session, basic, and token authentication.

- **Responsive interface**
  - Bootstrap-based templates styled with `django-bootstrap5` and crispy forms.
  - HTMX-powered asynchronous form and list interactions reduce full-page reloads.
  - Optional view-mode toggling is available for users.

- **REST API**
  - Authenticated endpoints are available under `/api/` for cards, sets, players, and search.
  - API responses are serialized with Django REST Framework.

## Technology stack

- Python
- Django 4.2
- PostgreSQL
- Django REST Framework
- Redis-backed caching
- Bootstrap 5 and crispy forms
- HTMX
- AWS S3 object storage for uploaded card images
- DigitalOcean Serverless Inference (LLM) and Brave Search API for the image agent
- uv for dependency management
- Gunicorn for deployment
- Docker Compose for local PostgreSQL and Adminer services

## Project structure

```text
bbcards/
├── api/          REST API endpoints and serializers
├── bbcards/      Django project configuration and URL routing
├── cards/        Card and card-set models, views, exports, templates, and the AI image agent
├── players/      Player models, views, and templates
├── users/        Authentication, profiles, and user management
├── static/       CSS, JavaScript, and other static assets
├── templates/    Shared Django templates
├── manage.py     Django administration command-line utility
├── pyproject.toml  Project metadata and dependencies
└── uv.lock       Locked dependency versions
```

## Requirements

- Python 3.14 (see `.python-version`) and [uv](https://docs.astral.sh/uv/).
- PostgreSQL is required for normal development and production use because the application uses PostgreSQL full-text search features.
- Redis is required by the configured cache backend.
- Docker and Docker Compose are optional but provide a convenient local PostgreSQL and Adminer setup.

## Local development setup

### 1. Clone the repository

```bash
git clone https://github.com/guitardave/bbcards.git
cd bbcards
```

### 2. Install dependencies

```bash
uv sync
```

This creates `.venv` and installs the locked dependencies from `uv.lock`. Run commands with `uv run` (for example `uv run python manage.py runserver`) or activate the environment with `source .venv/bin/activate`.

### 3. Start PostgreSQL locally

The repository includes a Docker Compose configuration for PostgreSQL and Adminer:

```bash
docker compose up -d postgres adminer
```

The included Compose file exposes an Adminer database browser at `http://localhost:8881`. Confirm the PostgreSQL connection details in your local environment before starting Django; the application's `DATABASE_URL` must point to a reachable PostgreSQL database.

### 4. Configure environment variables

Create a `.env` file in the project root or export the variables in your shell. At minimum, configure a Django secret key and database URL:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-development-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=true   # local development only; defaults to false
DATABASE_URL=postgres://testuser:testpass@localhost:5432/testdb
```

The application also reads the following optional settings when the related features are enabled:

```dotenv
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USER=
REDIS_PW=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=          # optional
AWS_S3_ENDPOINT_URL=         # optional, for S3-compatible hosts such as DO Spaces

# AI image agent
MODEL_ACCESS_KEY=            # DigitalOcean Serverless Inference model access key
BRAVE_API_KEY=               # Brave Search API key
DO_INFERENCE_MODEL=          # optional, default: deepseek-v4.1-flash
DO_INFERENCE_URL=            # optional, default: https://inference.do-ai.run/v1
```

> **Note:** The exact PostgreSQL host, port, username, password, and database name must match the database service you use. Update `DATABASE_URL` if your local PostgreSQL installation uses different values.

### 5. Apply migrations and create an administrator

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser and sign in with a user account.

## AI image agent

The agent in `cards/image_agent.py` finds a photo for a card. It builds a description from the card's year, set, sport, subset, number, and player, then lets the model call two tools in a loop:

- `search_images` queries Brave Image Search.
- `choose_image` picks one of the returned URLs. The image is downloaded, verified as a real JPEG/PNG/WebP/GIF (max 8 MB), and saved to `Card.card_image`.

Safeguards: the model can only choose URLs that appeared in search results, and downloads are restricted to public `http(s)` hosts (no private or loopback addresses, no redirects).

**From the Image Manager:** choose **Image Manager** in the nav bar. It lists cards missing images (or all cards) with a **Find image** / **Re-search** button on each row. The search runs for that card only, shows a spinner, and swaps in the result.

**From a card's image page:** open a card's image page and click **Find image** (or **Find a different image**, which replaces the existing image). This blocks the request for roughly 10-30 seconds.

**In bulk:**

```bash
uv run python manage.py fetch_card_images [--limit 25] [--overwrite]
```

By default only cards without an image are processed; `--overwrite` also replaces existing images. Errors on individual cards are reported and skipped.

Requires `MODEL_ACCESS_KEY` and `BRAVE_API_KEY`. Not every model on a DigitalOcean account is authorized for inference; if requests return `403 Forbidden`, list available models with `GET {DO_INFERENCE_URL}/models` and set `DO_INFERENCE_MODEL` to one that works. Images come from the open web, so review them before relying on them.

## API overview

All API routes are rooted at `/api/` and require authentication. The available resources include:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/` | Return the most recent cards exposed by the API |
| `GET` | `/api/search/?q=<term>` | Search cards |
| `GET` | `/api/<card_id>/` | Retrieve a card |
| `GET` | `/api/set/<set_id>/` | List cards in a set |
| `GET` | `/api/sets/` | List card sets |
| `POST` | `/api/sets/new/` | Create a card set |
| `POST` | `/api/sets/<set_id>/` | Update a card set |
| `GET` | `/api/player/<player_id>/` | List cards for a player |
| `GET` | `/api/players/` | List players |
| `POST` | `/api/players/new/` | Create a player |
| `POST` | `/api/players/<player_id>/` | Update a player |

Card creation is also available through the API. Refer to `api/serializers.py` and `api/views.py` for the accepted request fields and response shapes.

## Deployment

Dependencies are managed with uv; install them in the build step with `uv sync --frozen`. Also run `uv run python manage.py collectstatic --noinput` in the build step; WhiteNoise serves the collected files from `staticfiles/`. Run the app with Gunicorn:

```bash
uv run gunicorn bbcards.wsgi --timeout 120
```

The longer timeout matters: an image search can take 10-30 seconds or more, and Gunicorn's 30-second default would kill the worker mid-request.

There is no `Procfile`, so configure this as the run command on your hosting platform.

Before deploying, configure production values for at least:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS` (comma-separated; defaults to `.jojodave.com`, which matches the apex domain and all subdomains)
- `DJANGO_CSRF_TRUSTED_ORIGINS` (defaults to `https://jojodave.com,https://*.jojodave.com`)
- Optional: `DJANGO_SSL_REDIRECT` (default `True`) and `DJANGO_HSTS_SECONDS` (default `0`; raise it once HTTPS is confirmed)
- `DATABASE_URL`
- Redis connection variables
- AWS credentials and bucket name. These are required in production: without them uploads fall back to local disk, which is ephemeral on most platforms and is wiped on each deploy
- `MODEL_ACCESS_KEY` and `BRAVE_API_KEY` if the image agent is used

Review Django's deployment checklist before running the application in production. In particular, do not use development `DEBUG` settings or permissive CORS configuration for a public production deployment without reviewing the security implications.

## Data model

The primary collection relationships are:

```text
Player ────────┐
               ├── Card
CardSet ───────┘

CardUser ── favorite_player ── Player
```

A `Card` belongs to one `Player` and one `CardSet`. A `CardSet` records the year, set name, and sport. Card records can additionally include an image, subset, condition, card number, and grading flag.

## Development notes

- Database-backed full-text search relies on PostgreSQL features and should be tested against PostgreSQL rather than SQLite.
- HTMX endpoints are used for asynchronous create, update, delete, and form-refresh interactions.
- Uploaded files use Django's `STORAGES` setting. When `AWS_STORAGE_BUCKET_NAME` and AWS credentials are set, media is stored in S3 under the `media/` prefix and served from the bucket's URL (the prefix must be publicly readable). Otherwise, media is stored in the local `media/` directory.
- Keep credentials, secret keys, and production connection strings out of source control.

## License

No license file is currently included in the repository. Add a license before redistributing the project or accepting external contributions under defined terms.
