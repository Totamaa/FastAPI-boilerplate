# API Boilerplate — Détail & Priorisation

> Difficulté : 🟢 Facile (1-2j) · 🟡 Moyen (3-5j) · 🔴 Complexe (1 semaine+)

---

## 1. Protocoles & Transport

### WebSocket 🟡
Un canal bidirectionnel persistant entre client et serveur. Le client se connecte une fois, les deux parties peuvent envoyer des messages à tout moment sans rouvrir de connexion. Utile pour tout ce qui est temps réel : notifications push, présence en ligne, live updates. En FastAPI, `websockets` est intégré nativement. La difficulté principale n'est pas l'implémentation basique mais la gestion à l'échelle : si tu as plusieurs workers/instances, il faut un broker centralisé (Redis Pub/Sub ou similaire) pour que les messages arrivent au bon worker. Il faut aussi gérer les reconnexions côté client.

### Server-Sent Events (SSE) 🟢
Alternative plus simple aux WebSockets pour les flux **unidirectionnels** (serveur → client uniquement). La connexion HTTP reste ouverte, le serveur streame des events au format `text/event-stream`. Nativement supporté par les navigateurs, pas besoin de bibliothèque côté front. Plus facile à passer derrière un reverse proxy (Nginx, Cloudflare) que les WebSockets. À préférer quand le client n'a pas besoin d'envoyer des messages continus (flux d'activité, notifications, updates de progression de tâche).

### GraphQL (Strawberry) 🟡
Endpoint unique où le client décrit exactement les données qu'il veut dans sa requête. Élimine l'over-fetching et l'under-fetching. Strawberry génère le schéma depuis des dataclasses Python avec des types annotés. Le vrai challenge est le **problème N+1** : sans précaution, une query qui liste 100 items avec leurs relations génère 100 requêtes SQL. La solution est DataLoader (batching de requêtes). Ajoute aussi une couche de complexité pour les permissions (field-level vs type-level) et rend le cache HTTP plus difficile (tout passe en POST).

### gRPC 🔴
Protocole RPC binaire basé sur Protobuf. Tu définis tes services et messages dans des fichiers `.proto`, tu génères les stubs client/serveur, et les appels se font comme des fonctions locales. Beaucoup plus rapide et plus compact que REST pour les communications internes (service-to-service). Supporte le streaming bidirectionnel. La complexité vient du tooling (génération de code, versioning des `.proto`), de la courbe d'apprentissage, et du fait que c'est peu adapté aux clients front-end (nécessite grpc-web + proxy). Pertinent uniquement si tu as une architecture microservices.

---

## 2. Recherche

### Full-text search PostgreSQL 🟡
PostgreSQL embarque un moteur de recherche plein texte via les types `tsvector` (document indexé) et `tsquery` (requête). Tu crées une colonne `search_vector` de type `tsvector`, tu l'alimentes via un trigger ou à l'écriture, tu crées un index GIN dessus, et tes queries utilisent l'opérateur `@@`. `pg_trgm` est une extension complémentaire qui permet la recherche par similarité et les recherches partielles (utile pour l'autocomplétion). Le ranking de pertinence se gère avec `ts_rank`. Couvre bien 80% des besoins sans infrastructure supplémentaire.

### Filtres avancés 🟢
Un query builder dynamique qui accepte des paramètres optionnels et les combine. Le pattern est simple : tu commences avec une query de base, et tu appliques conditionnellement chaque filtre si le paramètre est présent. En SQLAlchemy, ça se traduit par une liste de clauses `where()` que tu appliques dynamiquement. La complexité monte avec la validation des paramètres, les opérateurs (`gte`, `lte`, `in`, `contains`) et le tri multi-colonnes. Pydantic rend la validation des paramètres de query assez propre.

### Autocomplétion 🟢
Endpoint `/suggest?q=` qui renvoie rapidement des suggestions pendant la frappe. Côté DB, `pg_trgm` avec un index GIN sur les colonnes pertinentes donne de bons résultats. Tu peux aussi simplement faire un `ILIKE '%query%'` si le volume est faible. La vraie réflexion est sur la latence (l'endpoint doit répondre en <100ms), le debounce côté front (ne pas fire à chaque keystroke), et le format de réponse (label + id + metadata pour afficher un dropdown riche).

### Elasticsearch / Typesense 🔴
Moteurs de recherche dédiés, externes à ta base de données. Elasticsearch est mature et très puissant (fuzzy search, facettes, aggregations, relevance tuning) mais lourd à opérer. Typesense est une alternative plus légère et plus simple à self-host. Le travail principal est la **synchronisation** : quand un record est créé/modifié/supprimé en DB, il faut propager le changement vers le moteur de recherche (sync synchrone, queue asynchrone, ou CDC). Pertinent uniquement quand PostgreSQL FTS ne suffit plus (gros volume, fuzzy search avancé, facettes complexes).

---

## 3. Cache

### Redis cache 🟡
Cache in-memory key-value ultra-rapide. Le pattern classique est cache-aside : avant de faire une requête DB coûteuse, on vérifie si la réponse est déjà dans Redis ; si oui on la retourne directement, sinon on fait la requête, on met en cache avec un TTL, on retourne. En Python, `redis-py` ou `aioredis` pour le client async. La difficulté n'est pas l'implémentation de base mais le **choix des TTL** (trop court = pas d'effet, trop long = données périmées) et la stratégie d'invalidation (voir ci-dessous).

### Cache HTTP (ETag / Cache-Control) 🟡
Mécanisme natif du protocole HTTP pour éviter de retransmettre des données qui n'ont pas changé. `Cache-Control` dit au client combien de temps garder la réponse en cache local. `ETag` est un hash de la réponse : le client le renvoie dans `If-None-Match`, et si la ressource n'a pas changé le serveur répond `304 Not Modified` sans body. `Last-Modified` / `If-Modified-Since` fonctionne sur le même principe avec des timestamps. Réduit la bande passante et la charge serveur sans infrastructure supplémentaire. FastAPI ne le gère pas automatiquement, il faut instrumenter les endpoints.

### Cache invalidation 🟡
Le problème classique : comment s'assurer que le cache ne renvoie pas des données obsolètes après une écriture ? Les stratégies principales sont : **write-through** (on écrit en DB et en cache en même temps), **write-behind** (on écrit en cache d'abord, la DB est mise à jour en arrière-plan), **TTL pur** (on accepte une fenêtre de stale data), et **invalidation explicite** (on supprime la clé de cache à chaque mutation). Le tagging de cache (regrouper plusieurs clés sous un tag pour les invalider ensemble) simplifie la gestion. La complexité vient des cas limites et des conditions de course (race conditions) entre lectures et écritures.

---

## 4. Intégrations externes

### Email (Resend / SendGrid / SES) 🟢
Intégration d'un provider d'envoi d'email transactionnel. Le SDK du provider est généralement simple (un appel de fonction avec `to`, `subject`, `html`). La vraie complexité est autour du **templating** (Jinja2, MJML pour le responsive email), de la **délivrabilité** (SPF, DKIM, DMARC sur ton domaine), et de la **fiabilité** (ne jamais envoyer directement dans le handler HTTP mais via une queue, pour gérer les retries en cas d'échec). Resend est actuellement le choix le plus propre pour les APIs modernes (DX excellente, webhooks natifs pour les bounces).

### Paiement Stripe 🔴
L'intégration Stripe va bien au-delà d'un simple appel API. Il faut gérer : la création de clients et produits, les Checkout Sessions ou Payment Intents, les **webhooks** (Stripe notifie ton serveur des événements de paiement de manière asynchrone — c'est là que tu actives les features), la vérification de signature de webhook, les abonnements récurrents et leur lifecycle (trial, upgrade, downgrade, annulation, dunning), le portail client pour la gestion des cartes. L'idempotence est critique (ne jamais activer deux fois). Plan : 2-3 semaines pour une intégration robuste.

### Stockage fichiers (S3 / Cloudflare R2) 🟡
Le pattern standard est le **presigned URL** : le client demande à ton API une URL temporaire signée, puis upload directement vers S3 sans passer par ton serveur. Ça évite de saturer ta bande passante. Côté API, tu gères uniquement la génération d'URLs (presigned PUT pour l'upload, presigned GET pour le download si privé) et la persistence des métadonnées en DB. Les points d'attention sont : la validation du type MIME côté serveur avant de générer l'URL, le redimensionnement d'images (Lambda@Edge ou un service dédié), et les politiques de bucket (CORS, accès public/privé).

### Webhooks sortants 🟡
Notifier des systèmes tiers quand un événement se produit dans ton API. Les challenges : **fiabilité** (le système tiers peut être down, donc il faut des retries avec backoff exponentiel), **sécurité** (signer le payload avec HMAC-SHA256 pour que le receveur puisse vérifier l'authenticité), **visibilité** (logger chaque tentative de livraison), **gestion des endpoints** (CRUD pour les URLs de webhook, activation/désactivation). À implémenter avec une queue de tâches (Celery, Taskiq, ARQ) pour ne pas bloquer le handler.

### TMDB / OMDb API 🟡
Enrichissement de données depuis une API externe. La logique principale : à la création d'une entité, déclencher un job asynchrone qui fetch les données depuis l'API externe et les merge dans la DB locale. Il faut gérer le **rate limiting** de l'API externe (backoff, quota), la **gestion des conflits** (si l'utilisateur a modifié un champ, doit-on l'écraser ?), et éventuellement un mécanisme de sync périodique pour maintenir les données à jour. Utile comme pattern générique pour tout enrichissement depuis une source externe.

---

## 5. Sécurité

### MFA / TOTP 🟡
Deuxième facteur d'authentification via une app (Google Authenticator, Authy, 1Password). Le standard TOTP (RFC 6238) génère un code à 6 chiffres qui change toutes les 30s basé sur un secret partagé et le timestamp. Côté implémentation : `pyotp` génère le secret et valide les codes, tu stockes le secret chiffré en DB, tu génères un QR code (uri `otpauth://`) pour l'enrollment. Il faut aussi prévoir les **backup codes** (10 codes usage unique pour récupérer l'accès si l'app est perdue) et le flow de désactivation. Le bon moment pour l'ajouter : après avoir un système d'auth solide.

### SSO / OAuth2 / OIDC 🟡
Permettre aux utilisateurs de se connecter avec un compte existant (Google, GitHub, Microsoft). OAuth2 gère l'autorisation (l'utilisateur accorde des permissions), OIDC est la couche d'identité au-dessus. Le flow Authorization Code : redirect vers le provider, callback avec un code, échange du code contre des tokens, fetch du profil utilisateur. `authlib` est la bibliothèque de référence en Python. Les complexités : lier un compte OAuth à un compte local existant, gérer plusieurs providers pour un même utilisateur, la révocation de tokens.

### Refresh token rotation 🟡
Stratégie de sécurité sur les refresh tokens : à chaque renouvellement d'access token, on invalide l'ancien refresh token et on émet un nouveau. Si un attaquant vole un refresh token et l'utilise, l'utilisateur légitime (qui utilisait l'ancien) déclenchera une anomalie détectable. La variante avancée est la **rotation family** : on groupe tous les tokens d'une session, et si un token de la famille déjà utilisé est rejoué, on révoque toute la famille (détection de token theft). Nécessite de stocker les tokens en DB (ou Redis) plutôt que de tout mettre dans le JWT.

### Device / Session management 🟡
Table `sessions` qui stocke les métadonnées de chaque session active : user agent parsé (browser, OS), IP de création, dernière activité, géolocalisation approximative. Endpoint `/auth/sessions` qui liste les sessions actives et permet la révocation individuelle ("déconnecter cet appareil") ou globale ("déconnecter partout sauf ici"). Feature visible par l'utilisateur final (comme sur Google ou GitHub). Côté implémentation, ça se couple naturellement avec la refresh token rotation puisque chaque session a un refresh token associé.

### IP allowlist / blocklist 🟢
Middleware qui, avant chaque requête, vérifie l'IP source contre une liste. Allowlist : seules les IPs listées ont accès (utile pour les endpoints admin). Blocklist : les IPs listées sont rejetées avec 403. La liste peut être statique (config) ou dynamique (table DB ou Redis pour les bans automatiques). Les points d'attention : la détection de la vraie IP derrière un reverse proxy (`X-Forwarded-For`, `X-Real-IP` — à valider selon ta config pour éviter le spoofing), et le support CIDR pour les plages d'IPs.

### Audit log 🟡
Table `audit_logs` immuable qui enregistre les actions sensibles : qui a fait quoi, quand, depuis quelle IP, avec quel résultat. Les champs typiques : `user_id`, `action` (enum : `user.created`, `role.changed`...), `target_type`, `target_id`, `diff` (JSON des changements avant/après), `ip`, `timestamp`. L'implementation peut se faire via un middleware, des hooks SQLAlchemy (event listeners sur `after_insert`, `after_update`), ou de manière explicite dans le code métier. L'immutabilité est importante : pas d'UPDATE ni de DELETE sur cette table, éventuellement un rôle DB en lecture seule.

---

## 6. Fonctionnalités métier

### Soft delete 🟢
Au lieu de supprimer physiquement un row, on met à jour un champ `deleted_at` (nullable timestamp). Les requêtes normales filtrent automatiquement `WHERE deleted_at IS NULL`. Avantages : restauration facile, audit trail, intégrité référentielle préservée. En SQLAlchemy, un `FilteredQuery` ou un mixin avec un event listener `before_query` peut automatiser le filtre. Il faut prévoir : un endpoint de restauration pour les admins, une tâche de purge planifiée pour les records anciens (RGPD), et gérer les contraintes d'unicité (un email "supprimé" doit pouvoir être réutilisé).

### Pagination cursor-based 🟡
Alternative au `LIMIT/OFFSET` classique. Avec l'offset, si des rows sont insérées/supprimées entre deux pages, les résultats sont incohérents (doublons ou sauts). Avec le cursor, on encode la position comme un identifiant opaque (base64 d'un `id` ou `(created_at, id)`). La requête est `WHERE id > cursor LIMIT n`. La réponse inclut un `next_cursor` que le client renvoie pour la page suivante. Implémentation plus propre avec des curseurs basés sur des colonnes indexées. Le tri doit être stable (ordre deterministe). Plus complexe à implémenter qu'offset mais indispensable pour les listes volumineuses ou les feeds temps réel.

### Likes / Réactions 🟢
Table `reactions` polymorphique : `user_id`, `target_type` (enum ou string), `target_id`, `reaction_type` (like, love, etc.), `created_at`. Contrainte unique sur `(user_id, target_type, target_id, reaction_type)` pour éviter les doublons. Le compteur peut être stocké dénormalisé dans l'entité cible (colonne `likes_count` mise à jour via trigger ou dans le service) pour éviter un `COUNT(*)` à chaque lecture. Le toggle (like → unlike) se fait avec un upsert ou un delete conditionnel.

### Collections / Watchlist 🟢
Table de jonction `user_collection_items` : `collection_id`, `item_type`, `item_id`, `position` (pour l'ordre), `added_at`. Les collections peuvent être possédées par un user ou par le système. La watchlist est une collection système auto-créée par user (avec un statut : `to_watch`, `watching`, `watched`). Les fonctionnalités avancées sont le tri drag-and-drop (mise à jour des `position`), la pagination de la collection, et le partage public (slug unique, visibilité publique/privée).

### Recommandations 🔴
Deux familles d'approches. Le **content-based filtering** : trouver des items similaires à ceux qu'un user a aimé, basé sur leurs attributs (genres, tags, etc.) — plus simple à implémenter mais moins personnalisé. Le **collaborative filtering** : trouver des users similaires à l'user cible et recommander ce qu'ils ont aimé — plus puissant mais nécessite beaucoup de données et des algorithmes comme SVD, ALS, ou des modèles de deep learning. En pratique pour un boilerplate : implémenter d'abord une heuristique simple (top items du même genre que tes favoris) et prévoir les hooks pour plugger un vrai moteur de recommandation plus tard.

---

## 7. Architecture

### API versioning 🟡
Stratégie pour faire évoluer l'API sans casser les clients existants. Les approches principales : prefix d'URL (`/api/v1/`, `/api/v2/`), header `Accept-Version`, content negotiation. Le prefix URL est le plus simple et le plus transparent. Il faut aussi une politique de **dépréciation** : header `Sunset` pour indiquer la date de fin de vie, header `Deprecation` pour alerter les clients. Côté code, les versions partagent généralement les models et services, mais ont des routers et schémas Pydantic séparés. La question du code sharing entre versions (héritage, composition) est le vrai enjeu de maintenabilité.

### Feature flags 🟢
Activer/désactiver des fonctionnalités sans déploiement, et potentiellement par utilisateur/segment (A/B testing, beta rollout). La version minimaliste : une table `feature_flags` (`key`, `enabled`, `rollout_percentage`, `allowed_user_ids`) et un service `is_feature_enabled(key, user_id)`. La version managée : LaunchDarkly ou Unleash (plus de features mais dépendance externe). Un flag sur un simple champ DB est souvent suffisant et très rapide à implémenter. C'est un outil de déploiement mais aussi de kill switch en production.

### Multi-tenant 🔴
Isoler les données de plusieurs organisations (tenants) dans la même instance. Deux approches principales : **schema-per-tenant** (PostgreSQL schema séparé par tenant — isolation forte mais complexe à gérer) et **row-level** avec `tenant_id` partout + Row-Level Security PostgreSQL (plus simple, l'isolation est garantie par la DB). Le tenant est résolu depuis le domaine, un header, ou le JWT au début de chaque requête. Tous les queries doivent filtrer par tenant — les oublis créent des fuites de données critiques. C'est une décision structurante : difficile à ajouter après coup, doit être pensée dès le départ si nécessaire.

### Event-driven (Kafka / RabbitMQ) 🔴
Découpler les modules via des messages asynchrones. Au lieu de `service_A.appelle_directement(service_B)`, A publie un event sur un bus, B écoute ce bus et réagit. Avantages : couplage faible, résilience (B peut être down sans bloquer A), scalabilité des consommateurs. RabbitMQ est plus simple à opérer pour des cas classiques (message queues). Kafka est adapté aux gros volumes et à l'event sourcing (log immuable rejouable). La complexité est dans la garantie de livraison (at-least-once vs exactly-once), l'idempotence des handlers, et l'ordre des messages.

### CQRS 🔴
Command Query Responsibility Segregation : séparer explicitement les opérations d'écriture (Commands) des opérations de lecture (Queries). Les writes passent par des agrégats qui appliquent la logique métier et émettent des events ; les reads utilisent des projections dénormalisées optimisées pour l'affichage. Permet d'optimiser séparément les deux chemins (index différents, éventuellement des stores différents pour la lecture). La complexité est réelle : cohérence éventuelle entre le write model et les projections, debuggabilité plus difficile. À réserver aux domaines où la complexité métier le justifie.

---

## 8. Observabilité

### Health checks enrichis 🟢
Endpoint `/health` qui retourne l'état détaillé de toutes les dépendances : DB (temps de réponse d'un ping), Redis (ping), broker de messages, services tiers critiques. Format standard : `{ "status": "ok|degraded|down", "checks": { "db": {"status": "ok", "latency_ms": 3}, ... } }`. Les load balancers et orchestrateurs (k8s) utilisent cet endpoint pour le routing. Distinguer `/health/live` (le process est vivant) de `/health/ready` (il peut recevoir du trafic) est une bonne pratique pour Kubernetes.

### Sentry 🟢
SDK de capture d'erreurs en production. Une ligne d'initialisation, et toutes les exceptions non gérées sont automatiquement capturées avec leur stack trace, les variables locales, et le contexte de la requête. La valeur ajoutée est dans la configuration : enrichir chaque event avec `user_id`, `tenant_id`, `environment` ; ignorer les erreurs attendues (404, 401) ; configurer les alertes ; et utiliser le **performance monitoring** pour tracer les transactions lentes. Sentry a aussi un SDK pour le front-end, ce qui permet de corréler les erreurs client et serveur.

### Métriques Prometheus 🟡
Exposition de métriques au format Prometheus sur `/metrics`. Les métriques typiques pour une API : latence des requêtes par endpoint et status code (histogram), taux de requêtes (counter), erreurs (counter), connexions DB actives (gauge), taille des queues, cache hit rate. `prometheus-fastapi-instrumentator` auto-instrumente FastAPI. Tu ajoutes des métriques custom avec `Counter`, `Histogram`, `Gauge` de `prometheus_client`. Grafana consomme Prometheus pour les dashboards. La difficulté est dans le choix des métriques pertinentes et la construction des dashboards.

### Tracing distribué (OpenTelemetry) 🔴
Tracer une requête de bout en bout à travers tous les services. Chaque opération (requête HTTP entrante, appel DB, appel externe, job async) crée un **span** avec un ID, une durée, des attributs. Les spans s'organisent en **trace** via un `trace_id` propagé dans les headers. OpenTelemetry est le standard vendor-neutral : tu instrumente avec le SDK OTel, et tu envoies vers Jaeger, Tempo, Honeycomb, ou Datadog selon ta préférence. `opentelemetry-instrument` peut auto-instrumenter SQLAlchemy, httpx, Redis. La complexité est dans le setup initial et le sampling (ne pas tracer 100% des requêtes en prod).

---

## 9. Developer Experience

### Collection Postman / Bruno 🟢
Fichier de collection versionné dans le repo qui documente et permet de tester tous les endpoints manuellement. Bruno est à préférer car sa collection est un fichier texte (YAML/JSON human-readable) qui se commit proprement dans Git, contrairement aux exports Postman. Inclure des variables d'environnement (`base_url`, `auth_token`), des scripts de pré-requête pour s'authentifier automatiquement, et des exemples de body pour chaque endpoint. C'est de la documentation exécutable.

### Seed enrichi 🟢
Script `seed.py` qui peuple la DB avec des données volumineuses et cohérentes pour tester les perfs, la pagination, et le comportement aux limites. `Faker` génère des données réalistes. La clé est la **cohérence des relations** (les reviews pointent vers des films qui existent, les films ont des genres valides). Prévoir différents profils : `seed --size small/medium/large` pour adapter au contexte (dev local vs test de charge). Un bon seed fait gagner énormément de temps pour détecter les bugs de pagination et les problèmes de perfs.

### SDK client généré 🟡
Génération automatique d'un client Python ou TypeScript depuis le schéma OpenAPI de l'API. `openapi-generator` ou `fern` prennent le `/openapi.json` et génèrent un client typé avec des méthodes pour chaque endpoint. À intégrer dans la CI : à chaque changement de l'API, le client est régénéré et publié (PyPI, npm). La difficulté est dans la qualité du schéma OpenAPI en input (les descriptions, les exemples, les noms d'opération) — garbage in, garbage out. Très utile si tu as des clients multiples ou si tu distribues l'API publiquement.

---
---

# Priorisation recommandée

> Critère : utilité générale pour n'importe quel backend API, pas spécifique au domaine métier.

---

## Tier 1 — Fondations non négociables

Ces points devraient être dans tout boilerplate dès le départ. Le coût d'ajout plus tard est élevé ou c'est de la dette technique évidente.

| Priorité | Feature | Raison |
|---|---|---|
| ★★★ | **Soft delete** | Pattern structurant, difficile à ajouter rétrospectivement sur une DB existante |
| ★★★ | **Refresh token rotation** | Sécurité basique de l'auth, ne coûte presque rien à implémenter |
| ★★★ | **Audit log** | Requis dans presque tous les contextes professionnels (compliance, debug prod) |
| ★★★ | **Health checks enrichis** | Indispensable dès qu'il y a un déploiement réel |
| ★★★ | **Sentry** | Visibilité sur la prod, setup en 10 minutes, ROI immédiat |
| ★★★ | **Pagination cursor-based** | Offset est bancal sur les gros volumes, et refactorer après coup est pénible |
| ★★★ | **Cache HTTP (ETag / Cache-Control)** | Gratuit en termes d'infrastructure, réduit la charge immédiatement |

---

## Tier 2 — Rapidement dans le boilerplate

Fonctionnalités à haute valeur ajoutée, implémentation raisonnable, applicables à quasi tous les projets.

| Priorité | Feature | Raison |
|---|---|---|
| ★★☆ | **API versioning** | Décision à prendre tôt — le préfixe `/v1/` dès le début coûte rien et évite un breaking change futur |
| ★★☆ | **Feature flags (version simple)** | Outil de déploiement fondamental, la version DB-only est triviale |
| ★★☆ | **Email transactionnel** | Quasi systématique (confirmation, reset password) |
| ★★☆ | **Filtres avancés** | Utile dans tout CRUD non trivial |
| ★★☆ | **Redis cache** | Dès qu'il y a des endpoints lourds ou du trafic |
| ★★☆ | **Full-text search PostgreSQL** | Couvre 80% des besoins sans infrastructure, PostgreSQL est déjà là |
| ★★☆ | **Session management** | Complément naturel du refresh token, visible par l'utilisateur |
| ★★☆ | **Seed enrichi** | Productivité dev quotidienne |

---

## Tier 3 — Selon le contexte, mais souvent utile

Valeur ajoutée réelle, mais le besoin dépend du type de projet.

| Priorité | Feature | Raison |
|---|---|---|
| ★☆☆ | **SSE ou WebSocket** | Dès que du temps réel est nécessaire — SSE en premier, WebSocket si bidirectionnel |
| ★☆☆ | **Stockage fichiers S3** | Dès qu'il y a un upload utilisateur |
| ★☆☆ | **MFA / TOTP** | Si le produit a des données sensibles |
| ★☆☆ | **Autocomplétion** | UX importante si la recherche est centrale |
| ★☆☆ | **Métriques Prometheus** | Quand on passe en production réelle avec du trafic |
| ★☆☆ | **Webhooks sortants** | Si l'API a vocation à être intégrée par des tiers |
| ★☆☆ | **Collection Bruno/Postman** | Bonne pratique, effort minimal |
| ★☆☆ | **IP allowlist/blocklist** | Si les endpoints admin sont exposés publiquement |

---

## Tier 4 — Valeur réelle mais complexité significative

À planifier consciemment, pas à faire à la va-vite.

| Feature | Condition d'ajout |
|---|---|
| **Stripe** | Seulement si modèle monétaire établi |
| **SSO OAuth2** | Si UX de signup est un enjeu (consumer app) |
| **Tracing OpenTelemetry** | Quand les métriques ne suffisent plus pour diagnostiquer |
| **SDK client généré** | Si API publique ou plusieurs clients |
| **Elasticsearch / Typesense** | Quand PostgreSQL FTS montre ses limites |
| **GraphQL** | Si clients front-end multiples avec des besoins très différents |

---

## Tier 5 — Complexité architecturale, besoin spécifique

Ne pas ajouter par défaut dans un boilerplate. À introduire quand la complexité du domaine ou le scale le justifient explicitement.

| Feature | Quand vraiment |
|---|---|
| **Multi-tenant** | Si le produit est un SaaS B2B multi-org dès le départ |
| **Event-driven (Kafka/RabbitMQ)** | Microservices ou volume qui justifie le découplage |
| **CQRS** | Domaine métier complexe avec lecture/écriture très asymétriques |
| **gRPC** | Architecture microservices avec appels service-to-service fréquents |
| **Recommandations** | Après avoir des données et un modèle métier établi |

---

## Synthèse en une phrase

> Commence par : soft delete + cursor pagination + refresh token rotation + audit log + health checks + Sentry. Ce sont les 6 choses que tu regretteras de ne pas avoir mises dès le début.
