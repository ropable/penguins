# penguins — agent instructions

## Quick start

```bash
source .venv/bin/activate       # Activate local virtualenv before Python commands
uv sync                         # install all deps (prod + dev)
cp .env.example .env            # if missing; edit DATABASE_URL etc.
python manage.py migrate
python manage.py runserver
```

## Commands

| Action          | Command                                                                               |
| --------------- | ------------------------------------------------------------------------------------- |
| Run all tests   | `python manage.py test`                                                               |
| Run single test | `python manage.py test observations.tests.test_views.PenguinsViewsTest.test_homepage` |
| Lint Python     | `ruff check .`                                                                        |
| Lint templates  | `djlint penguins/templates observations/templates --lint`                             |
| Format          | `ruff format .`                                                                       |
| Import videos   | `python manage.py video_import [--year YYYY]`                                         |
| Collect static  | `python manage.py collectstatic --noinput`                                            |
| Docker build    | `docker build -t penguins .`                                                          |

**Order for verification:** `ruff check . && python manage.py test` (no typecheck step — none configured).

## Architecture

- **Django 5.2** project with one app: `observations/`
- Package manager: **uv** only (no pip, no pip-compile, no Poetry)
- **PostGIS** database with `django.contrib.gis`
- **Azure blob storage** (`django-storages[azure]`) for video files — `AZURE_*` env vars required
- **SSO** via `dbca_utils.middleware.SSOLoginMiddleware`
- App URLs mounted at `/` (not `/observations/`)
- WSGI entrypoint loads `.env` via `python-dotenv` before Django boot
- Static files served by **WhiteNoise** (Brotli-compressed)
- Only dev dependency groups exist (no `test`, `lint`, `typecheck` groups)

## Ruff quirks

- Line length: **140** (not 88 or 120)
- **E501** (line too long) and **E722** (bare except) are **ignored** project-wide

## Kustomize / deploy

- Kustomize in `kustomize/` — base + overlays for prod (hourly video import) and uat (daily import)
- Runner affinity: **ARM64 only** (CI builds `linux/arm64`; deployment `nodeSelector`)
- Image: `ghcr.io/dbca-wa/penguins`

## Important gotchas

- `.env` files with secrets **committed to the repo** (dev, prod, uat) — do not commit additional secrets
- No CI test or lint job — Docker build + Trivy scan + TruffleHog only
- Pre-commit hook runs TruffleHog (`trufflehog git file://. --since-commit HEAD --only-verified --fail`)
- Python base image in Dockerfile comes from the Docker Hub hardened images registry (`dhi.io/python:3.13-debian13-dev`)
- No `make`, no `package.json`, no Node tooling — all JS from CDNs
- `test_video.mp4` is a real binary fixture checked into git (~400 KB)
