# CinemaDB — Documentation technique

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Démarrage](#2-démarrage)
3. [Gestion des dépendances](#3-gestion-des-dépendances)
4. [Base de données](#4-base-de-données)
5. [Architecture](#5-architecture)
6. [Core](#6-core)
7. [Variables d'environnement](#7-variables-denvironnement)
8. [Linting — Ruff](#8-linting--ruff)
9. [Tests](#9-tests)
10. [CI](#10-ci)

---

## 1. Prérequis

- **Python 3.12+**
- **Make** — Windows : [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm) ou via Git Bash / WSL
- **Docker Desktop**

---

## 2. Démarrage

### 2.1. Premier lancement

```bash
# 1. Copier le fichier d'environnement et renseigner les valeurs
cp .env.example .env

# 2. Setup complet (venv, docker, dépendances, migrations)
make setup
```

`make setup` crée le virtualenv, installe les dépendances, démarre les services Docker et applique les migrations.

### 2.2. Lancement quotidien

```bash
make dev
```

Démarre le serveur FastAPI en mode dev (hot-reload).

### 2.3. Après un pull

```bash
make sync
```

Recompile les dépendances si les `.in` ont changé, met à jour le venv, et applique les nouvelles migrations.

---

## 3. Gestion des dépendances

On utilise **pip-tools** avec **uv** pour séparer et verrouiller les dépendances.

### 3.1. Fichiers source

| Fichier | Rôle |
| --- | --- |
| `requirements.in` | Dépendances de production |
| `requirements-dev.in` | Dépendances de dev (inclut prod via `-r requirements.in`) |
| `requirements.txt` | Lockfile prod (généré, ne pas éditer) |
| `requirements-dev.txt` | Lockfile dev (généré, ne pas éditer) |

Le `-r requirements.in` dans le fichier dev garantit que les versions sont résolues ensemble — pas de conflit possible entre prod et dev.

### 3.2. Ajouter un package

1. Ajouter la dépendance dans le bon fichier `.in` :
   - prod → `requirements.in`
   - dev uniquement → `requirements-dev.in`
2. Spécifier une contrainte de version si nécessaire : `fastapi>=0.115,<0.116`
3. Appliquer :

```bash
make sync
```

---

## 4. Base de données

### 4.1. Modèles

Approche **code-first**. Les modèles SQLAlchemy sont dans `src/app/modules/{module}/model.py`. Modifier la table = modifier le modèle, puis générer une migration.

Toutes les relations sont en `lazy="raise"` par défaut (configuré globalement dans `modules/base/model.py` via un event listener SQLAlchemy). Accéder à une relation sans l'avoir explicitement chargée (`selectinload`, `joinedload`) lève une erreur immédiatement.

### 4.2. Migrations

```bash
# Générer une migration après avoir modifié un modèle
make revision msg="description_courte"

# Appliquer les migrations en attente
make migrate

# Annuler la dernière migration
make migrate-down

# Reset complet de la DB (DEV uniquement — irréversible)
make db-reset
```

---

## 5. Architecture

### 5.1. Arborescence

```txt
cinemadb/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.in
├── requirements-dev.in
├── requirements.txt              (généré)
├── requirements-dev.txt          (généré)
│
├── docs/
│   └── info.md
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── scripts/
│   └── seed.py
│
├── tests/
│   ├── conftest.py
│   └── unit/
│
└── src/app/
    ├── main.py                   # Factory FastAPI, lifespan, middlewares, handlers
    │
    ├── background/               # Tâches asynchrones ponctuelles (Taskiq)
    │   └── tasks/
    │       └── movie_stats.py    # recalcul stats après création d'une review
    │
    ├── scheduler/                # Tâches planifiées (APScheduler)
    │   └── jobs/
    │       ├── movie_stats.py    # batch quotidien 02:00 UTC — avg_rating / review_count
    │       └── trending.py       # top-10 hebdo lundi 08:00 UTC
    │
    ├── core/                     # Infrastructure transverse (voir §6)
    │   ├── api/
    │   │   ├── router.py
    │   │   ├── dependencies/
    │   │   │   ├── auth.py
    │   │   │   ├── db.py
    │   │   │   └── request_id.py
    │   │   └── v1/
    │   │       ├── router.py
    │   │       ├── actors.py
    │   │       ├── auth.py
    │   │       ├── directors.py
    │   │       ├── genres.py
    │   │       ├── movie_cast.py
    │   │       ├── movies.py
    │   │       ├── reviews.py
    │   │       └── users.py
    │   ├── config/
    │   │   ├── settings.py
    │   │   ├── database.py
    │   │   ├── redis.py
    │   │   ├── broker.py
    │   │   └── logs.py
    │   ├── errors/
    │   │   ├── exceptions/
    │   │   └── handlers/
    │   ├── middleware/
    │   ├── security/
    │   └── utils/
    │
    └── modules/                  # Domaines métier
        ├── base/                 # Modèle et schémas de base partagés
        ├── associations/
        │   └── movie_genres.py   # table de liaison M-N films ↔ genres
        ├── actors/
        ├── auth/
        ├── directors/
        ├── genres/
        ├── movie_cast/           # N-N avec données : film ↔ acteur (rôle, ordre, lead)
        ├── movie_details/        # 1-1 avec movies (synopsis, budget, box-office…)
        ├── movies/
        ├── reviews/
        └── users/
```

### 5.2. Anatomie d'un module — de la route à la DB

Chaque module suit la même structure en 5 fichiers :

```txt
modules/{module}/
├── model.py          # Entité SQLAlchemy
├── schemas.py        # Schémas Pydantic (requête / réponse)
├── exceptions.py     # Exceptions métier du module
├── repository.py     # Accès base de données
├── service.py        # Logique métier
└── dependencies.py   # Injection de dépendances (factories)
```

**Le flux d'une requête :**

```txt
Router (core/api/v1/) → Dependencies → Service → Repository → Model
```

---

**`model.py`** — l'entité SQLAlchemy, définit la table et les relations :

```python
class MovieModel(BaseModel):
    __tablename__ = "movies"
    title = Column(String(500), nullable=False)
    director = relationship("DirectorModel", back_populates="movies")
```

---

**`schemas.py`** — les schémas Pydantic, un par usage :

- **Request** : validation des entrées + `to_model()` pour convertir vers le modèle SQLAlchemy
- **Response** : `from_model()` (classmethod) pour sérialiser + `ConfigDict(from_attributes=True)`
- **Update** : tous les champs optionnels, utilise `model_dump(exclude_unset=True)` pour ne toucher que ce qui est fourni

---

**`exceptions.py`** — les erreurs métier du module :

```python
class MovieNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=404, message="Movie not found", tag="MOVIE")
```

Héritent de `AppException` (définie dans `core/errors/exceptions/base.py`). Un handler centralisé les transforme automatiquement en réponse HTTP cohérente.

---

**`repository.py`** — les requêtes SQL, rien d'autre :

```python
class MovieRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, movie_id: UUID) -> MovieModel | None:
        result = await self.db.execute(select(MovieModel).where(MovieModel.id == movie_id))
        return result.scalar_one_or_none()
```

---

**`service.py`** — la logique métier, orchestre le repo via l'UoW :

```python
class MovieService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get(self, movie_id: UUID) -> MovieResponse:
        async with self.uow:
            movie = await self.uow.movies.get_by_id(movie_id)
            if not movie:
                raise MovieNotFoundException()
            return MovieResponse.from_model(movie)
```

L'UoW (`core/config/database.py`) centralise la session DB. Il commite ou rollback automatiquement à la sortie du `async with`.

---

**`dependencies.py`** — câble le service et cache la complexité :

```python
def get_movie_service(
    db: AsyncSession = Depends(get_db),
) -> MovieService:
    return MovieService(UnitOfWork(db))
```

---

**`core/api/v1/{module}.py`** — le router, aussi simple que possible :

```python
@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: UUID,
    service: MovieService = Depends(get_movie_service),
):
    return await service.get(movie_id)
```

Aucune logique dans le router. Toute la complexité (DB, auth, logging) est dans les dependencies.

---

## 6. Core

Infrastructure transverse, partagée par tous les modules.

**`core/config/`** — configuration centralisée via Pydantic Settings. Les variables d'environnement sont lues depuis `.env` et validées au démarrage. `database.py` configure l'engine SQLAlchemy async et l'`UnitOfWork`, `redis.py` la connexion Redis, `broker.py` le broker Taskiq.

**`core/errors/`** — gestion centralisée des erreurs :

- `exceptions/base.py` — `AppException` (base de toutes les erreurs métier)
- `handlers/` — intercepte les `AppException`, les erreurs SQLAlchemy (violation de contrainte unique, etc.) et transforme toute exception imprévue en 500

**`core/middleware/`** :

- `headers.py` — injecte les headers de sécurité et le `X-Request-ID` sur chaque réponse
- `rate_limit.py` — limitation de débit par IP via Redis

**`core/api/dependencies/`** :

- `auth.py` — validation du JWT, récupère l'utilisateur courant
- `db.py` — fournit la session SQLAlchemy async par requête
- `request_id.py` — génère un UUID unique par requête pour la traçabilité

**`core/security/`** :

- `hash_lib.py` — hachage et vérification des mots de passe
- `jwt_lib.py` — génération et validation des tokens JWT
- `anonymize_lib.py` — anonymisation des données sensibles pour les logs

---

## 7. Variables d'environnement

Toutes les variables sont lues depuis `.env` (copié depuis `.env.example`) et validées au démarrage par Pydantic Settings. Un démarrage échoue immédiatement si une variable obligatoire est absente ou invalide.

### Application

| Variable | Exemple | Rôle |
| --- | --- | --- |
| `ENVIRONMENT` | `dev` | Contexte d'exécution : `test` \| `dev` \| `ppr` \| `prod` |
| `APP_NAME` | `CinemaDB` | Nom de l'application (3–20 caractères) |
| `APP_VERSION` | `0.1.0` | Version semver |
| `APP_DESCRIPTION` | `Movie database backend API` | Description courte (3–200 caractères) |
| `APP_PORT` | `8000` | Port interne uvicorn |
| `APP_WORKERS` | `1` | Workers uvicorn — mettre le nombre de vCPUs en prod |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Liste JSON des origines CORS autorisées |

### Logging

| Variable | Exemple | Rôle |
| --- | --- | --- |
| `LOG_LEVEL` | `DEBUG` | Niveau de log : `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` |
| `LOG_MAX_BYTES` | `10485760` | Taille max d'un fichier de log avant rotation (10 MB) |
| `LOG_BACKUP_COUNT` | `5` | Nombre de fichiers de log archivés conservés |

### Base de données (PostgreSQL)

| Variable | Exemple | Rôle |
| --- | --- | --- |
| `DB_HOST` | `localhost` | Adresse du serveur PostgreSQL |
| `DB_PORT` | `5432` | Port TCP |
| `DB_NAME` | `cinemadb` | Nom de la base |
| `DB_USER` | `cinemadb_user` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | *(secret)* | Mot de passe — générer avec `openssl rand -hex 64` |

En dev, PostgreSQL tourne via Docker Compose.

### Redis

| Variable | Exemple | Rôle |
| --- | --- | --- |
| `REDIS_HOST` | `localhost` | Adresse du serveur Redis |
| `REDIS_PORT` | `6379` | Port TCP |
| `REDIS_PASSWORD` | *(secret)* | Mot de passe — générer avec `openssl rand -hex 64` |

Redis sert à deux choses : la **limitation de débit** par IP (middleware) et le **broker Taskiq** pour les tâches asynchrones de recalcul de stats.

### Sécurité

| Variable | Exemple | Rôle |
| --- | --- | --- |
| `API_KEY` | *(secret)* | Clé partagée envoyée via le header `X-API-Key` — `openssl rand -hex 64` |
| `JWT_SECRET_KEY` | *(secret)* | Clé de signature des tokens JWT — `openssl rand -hex 64` |
| `JWT_ALGORITHM` | `HS256` | Algorithme JWT : `HS256` \| `RS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Durée de vie du token d'accès (max 60 min) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Durée de vie du refresh token (max 45 jours) |
| `JWT_SESSION_MAX_LIFETIME_DAYS` | `30` | Durée de vie maximale d'une session (max 100 jours) |
| `JWT_SESSION_MAX_COUNT` | `5` | Nombre maximum de sessions actives par utilisateur (max 10) |

---

## 8. Linting — Ruff

Le projet utilise **Ruff** pour le linting et le formatage. La configuration est dans `pyproject.toml`.

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
extend-exclude = ["migrations/"]   # les migrations sont générées, ne pas linter

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = [
    "E501",   # longueur de ligne — géré par le formateur
    "B008",   # Depends() en argument par défaut — pattern FastAPI intentionnel
]

[tool.ruff.lint.isort]
known-first-party = ["app"]
```

**Règles activées :**

| Code | Catégorie | Description |
| --- | --- | --- |
| `E` | pycodestyle | Erreurs de style PEP 8 |
| `F` | pyflakes | Imports inutilisés, variables indéfinies |
| `I` | isort | Ordre des imports |
| `UP` | pyupgrade | Modernisation automatique de la syntaxe Python |
| `B` | flake8-bugbear | Patterns susceptibles de causer des bugs |
| `SIM` | flake8-simplify | Simplifications de code |

### Commandes

```bash
# Vérifier le style (sans modifier)
ruff check .

# Corriger automatiquement ce qui peut l'être
ruff check --fix .

# Vérifier le formatage
ruff format --check .

# Formater les fichiers
ruff format .
```

---

## 9. Tests

Les tests sont dans `tests/` et organisés par type avec des `pytest.mark`.

### 9.1. Tests unitaires (`@pytest.mark.unit`)

Dossier : `tests/unit/`

Testent la logique pure sans I/O. Tournent sans Docker, sans base de données, sans réseau.

### 9.2. Tests d'intégration (`@pytest.mark.integration`)

Dossier : `tests/integration/`

Testent le stack complet : requête HTTP → service → repository → base de données réelle. Requièrent PostgreSQL et Redis (via Docker Compose).

**Infrastructure de test (conftest.py) :**

- Un fixture `_bootstrap_test_db` crée la base `{DB_NAME}_test`, applique toutes les migrations Alembic, et la détruit en fin de session.
- Chaque test reçoit une `db_session` qui fait un `ROLLBACK` à la fin — isolation garantie sans recréer la base entre chaque test.

### 9.3. Coverage

Le seuil minimum est **85 %**, configuré dans `pyproject.toml` :

```toml
[tool.coverage.run]
source = ["src"]
omit = ["src/app/main.py"]

[tool.coverage.report]
fail_under = 85
show_missing = true
```

`main.py` est exclu — c'est la factory d'application, elle n'est pas testable unitairement.

### 9.4. Commandes

```bash
# Lancer tous les tests avec rapport de couverture
make test

# Uniquement les tests unitaires (rapide, sans Docker)
pytest -m unit

# Tests d'intégration uniquement
pytest -m integration
```

`make test` affiche les lignes non couvertes et échoue si la couverture descend sous 85 % (via `fail_under` dans `pyproject.toml`).

---

## 10. CI

Deux workflows GitHub Actions, déclenchés sur `push` et `pull_request` vers `main`.

### 10.1. Lint (`.github/workflows/lint.yml`)

Vérifie le style et le formatage via Ruff.

```txt
push / pull_request → main
  │
  ├── ruff check .          (linting — erreurs, imports, bugbear…)
  └── ruff format --check . (formatage — diffs sans modifier les fichiers)
```

Échoue si le code n'est pas formaté ou contient des violations de linting. Corriger localement avec `ruff check --fix .` et `ruff format .` avant de pusher.

### 10.2. Test (`.github/workflows/test.yml`)

Lance **tous** les tests (unit + intégration) avec PostgreSQL et Redis en service containers, et vérifie que la couverture atteint 85 %.

```txt
push / pull_request → main
  │
  ├── Services : postgres:16-alpine + redis:7-alpine
  ├── pip install -r requirements-dev.txt
  └── pytest --cov --cov-report=term-missing --tb=short -q
        └── échoue si coverage < 85 % (fail_under dans pyproject.toml)
```

**Variables d'environnement injectées en CI :**

| Variable | Valeur CI |
| --- | --- |
| `ENVIRONMENT` | `test` |
| `APP_NAME` | `CinemaDB` |
| `APP_PORT` | `8000` |
| `DB_HOST` | `localhost` |
| `DB_NAME` | `cinemadb` |
| `DB_USER` | `cinemadb_user` |
| `REDIS_HOST` | `localhost` |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `JWT_SESSION_MAX_LIFETIME_DAYS` | `30` |
| `JWT_SESSION_MAX_COUNT` | `5` |

Les secrets (`DB_PASSWORD`, `REDIS_PASSWORD`, `API_KEY`, `JWT_SECRET_KEY`) sont des valeurs fixes CI sans valeur réelle — ils respectent les contraintes de validation (longueur minimale) mais ne protègent rien.
