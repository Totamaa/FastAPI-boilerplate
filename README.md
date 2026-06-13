# FastAPI Boilerplate

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen?style=flat-square)](tests/)
[![CI](https://img.shields.io/github/actions/workflow/status/Totamaa/FastAPI-boilerplate/test.yml?style=flat-square&label=CI)](https://github.com/Totamaa/FastAPI-boilerplate/actions)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

A production-ready FastAPI boilerplate built around a movie database domain.
Async SQLAlchemy, JWT + API key auth, background tasks, scheduled jobs, soft delete — all wired up and tested.

---

## Overview

FastAPI Boilerplate is a **boilerplate** for building production-grade REST APIs with FastAPI. It uses a movie catalogue as its domain (movies, actors, directors, genres, reviews) so every pattern is grounded in realistic data relationships rather than abstract CRUD.

Fork it, strip what you don't need, and build on top of a solid foundation.

## Stack

| Layer | Technology |
| --- | --- |
| Framework | FastAPI 0.115 + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Migrations | Alembic |
| Auth | JWT (access + refresh) + API key |
| Scheduler | APScheduler (cron jobs) |
| Testing | pytest-asyncio, httpx, coverage ≥ 90 % |
| Packaging | uv + pip-tools |

## Prerequisites

- **Python 3.12+**
- **Docker Desktop** (PostgreSQL + Redis via Docker Compose)
- **Make** — on Windows use Git Bash, WSL, or [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm)

## Quick start

```bash
# 1. Clone
git clone https://github.com/Totamaa/FastAPI-boilerplate
cd FastAPI-boilerplate

# 2. Copy environment config and fill in values
cp .env.example .env

# 3. First-time setup: creates venv, installs deps, starts Docker services, runs migrations
make setup

# 4. Start the dev server (hot-reload)
make dev
```

The API is available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/api/docs`.

## Common commands

```bash
make dev          # Start API dev server + worker
make test         # Run tests with coverage report
make migrate      # Apply pending Alembic migrations
make sync         # Recompile deps + sync venv + migrate (after a pull)
make fix          # Auto-format and fix lint issues (ruff)
make check        # Lint check without modifying files (CI)
make down         # Stop Docker services
make help         # List all available commands
```

## Documentation

All technical documentation lives in [`docs/`](docs/):

| File | Contents |
| --- | --- |
| [`docs/info.md`](docs/info.md) | Architecture, auth, env vars, migrations, CI |
| [`docs/api-boilerplate-roadmap.md`](docs/api-boilerplate-roadmap.md) | Roadmap and feature backlog |

## Project structure

```text
src/app/
├── core/           # Config, auth, dependencies, middleware
├── modules/        # Domain modules: movies, actors, directors, genres, reviews, users
├── background/     # Async background tasks (post-request)
├── scheduler/      # Scheduled jobs (APScheduler cron)
└── main.py

migrations/         # Alembic migration versions
tests/
├── unit/           # Unit tests
└── integration/    # Integration tests (real Postgres, per-test rollback)
```

Each domain module follows the same layered structure: `model → repository → service → schemas → router → dependencies`.

## License

MIT
