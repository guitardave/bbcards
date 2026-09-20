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

- **Images and exports**
  - Upload card images through Django's file-storage abstraction.
  - Support AWS S3 configuration through `boto3` and `django-storages`.
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
- AWS S3-compatible object storage support
- Gunicorn for deployment
- Docker Compose for local PostgreSQL and Adminer services

## Project structure

```text
bbcards/
├── api/          REST API endpoints and serializers
├── bbcards/      Django project configuration and URL routing
├── cards/        Card and card-set models, views, exports, and templates
├── players/      Player models, views, and templates
├── users/        Authentication, profiles, and user management
├── static/       CSS, JavaScript, and other static assets
├── templates/    Shared Django templates
├── cards/        Collection data and uploaded card-related assets
├── manage.py     Django administration command-line utility
├── Procfile      Gunicorn process definition
└── requirements.txt
```

## Requirements

- Python 3.10 or later is recommended.
- PostgreSQL is required for normal development and production use because the application uses PostgreSQL full-text search features.
- Redis is required by the configured cache backend.
- Docker and Docker Compose are optional but provide a convenient local PostgreSQL and Adminer setup.

## Local development setup

### 1. Clone the repository

```bash
git clone https://github.com/guitardave/bbcards.git
cd bbcards
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start PostgreSQL locally

The repository includes a Docker Compose configuration for PostgreSQL and Adminer:

```bash
docker compose up -d postgres adminer
```

The included Compose file exposes an Adminer database browser at `http://localhost:8881`. Confirm the PostgreSQL connection details in your local environment before starting Django; the application's `DATABASE_URL` must point to a reachable PostgreSQL database.

### 5. Configure environment variables

Create a `.env` file in the project root or export the variables in your shell. At minimum, configure a Django secret key and database URL:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-development-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
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
```

> **Note:** The exact PostgreSQL host, port, username, password, and database name must match the database service you use. Update `DATABASE_URL` if your local PostgreSQL installation uses different values.

### 6. Apply migrations and create an administrator

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser and sign in with a user account.

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

The project includes a `Procfile` for Gunicorn-based hosting:

```text
web: gunicorn bbcards.wsgi
```

Before deploying, configure production values for at least:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- Redis connection variables
- AWS credentials and bucket name if S3 storage is used

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
- Uploaded files are configured through Django's storage settings; local development uses filesystem storage by default, while AWS S3 settings are available for deployments that need object storage.
- Keep credentials, secret keys, and production connection strings out of source control.

## License

No license file is currently included in the repository. Add a license before redistributing the project or accepting external contributions under defined terms.
