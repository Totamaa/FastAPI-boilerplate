# FastAPI Boilerplate - Idées d'évolution

## Protocoles & transport

- **WebSocket** - notifications temps réel (ex : nouvelle review sur un film suivi, stats live)
- **GraphQL** (Strawberry) - endpoint alternatif au REST, utile pour des clients qui veulent fetch exactement les champs dont ils ont besoin
- **Server-Sent Events** - alternative légère aux WebSockets pour les flux unidirectionnels (flux d'activité, mise à jour des stats)
- **gRPC** - si un service interne consomme l'API, plus efficace que REST pour les appels service-to-service

---

## Recherche

- **Full-text search** (PostgreSQL `tsvector` / `pg_trgm`) - recherche sur titre, synopsis, nom d'acteur/réalisateur avec ranking de pertinence
- **Filtres avancés** - recherche combinée (genre + année + note min + durée max) avec tri dynamique
- **Autocomplétion** - endpoint `/search/suggest?q=` pour la saisie progressive côté front
- **Elasticsearch / Typesense** - si la recherche devient un cas d'usage central, moteur dédié à la place de PostgreSQL

---

## Cache

- **Redis cache** - mettre en cache les réponses coûteuses (liste des films populaires, top reviews) avec TTL
- **Cache HTTP** - headers `ETag` / `Cache-Control` / `Last-Modified` sur les endpoints de lecture pour réduire la bande passante
- **Cache invalidation** - stratégie explicite pour invalider le cache quand un film ou une review est modifié

---

## Intégrations externes

- **Email** (Resend / SendGrid / SES) - confirmation d'inscription, reset de mot de passe, notification de review, digest hebdo
- **Paiement** (Stripe) - abonnement premium pour accéder à des fonctionnalités avancées (watchlist étendue, export, clé API personnelle)
- **Stockage fichiers** (S3 / Cloudflare R2) - upload de posters de films, photos de profil, photos d'acteurs
- **TMDB / OMDb API** - enrichissement automatique des fiches films (synopsis, poster, box-office) depuis une source externe
- **Webhooks sortants** - notifier un système tiers à chaque événement (nouvelle review, film ajouté)

---

## Sécurité

- **MFA** (TOTP - Google Authenticator / Authy) - deuxième facteur au login via code 6 chiffres
- **SSO** (OAuth2 / OIDC) - login avec Google, GitHub, etc. via un provider externe (Auth0, Keycloak, ou implémentation maison)
- **Refresh token rotation** - invalider l'ancien refresh token à chaque renouvellement pour limiter la fenêtre d'exposition
- **Device/session management** - liste des sessions actives + révocation individuelle depuis un endpoint `/auth/sessions`
- **IP allowlist / blocklist** - restriction d'accès par IP pour les endpoints admin
- **Audit log** - traçabilité de toutes les actions sensibles (création/suppression de comptes, changements de rôle) dans une table dédiée

---

## Fonctionnalités métier

- **Watchlist** - chaque utilisateur peut ajouter des films à regarder / déjà vus
- **Likes / réactions** sur les reviews
- **Recommandations** - "si tu as aimé X, tu pourrais aimer Y" basé sur les genres et les notes des autres utilisateurs
- **Collections** - groupes de films thématiques créés par les utilisateurs ou les admins (ex : "Meilleurs films des années 90")
- **Pagination cursor-based** - remplacer `limit/offset` par un cursor opaque pour des listes stables sur de gros volumes
- **Soft delete** - `deleted_at` au lieu de vraie suppression, avec endpoints de restauration et purge planifiée

---

## Architecture

- **Multi-tenant** - isoler les données par organisation (schéma PostgreSQL séparé ou colonne `tenant_id` avec Row-Level Security)
- **Event-driven** (Kafka / RabbitMQ) - découpler les modules via des événements asynchrones plutôt que des appels directs
- **CQRS** - séparer explicitement les modèles de lecture (projections dénormalisées) et d'écriture (agrégats)
- **Feature flags** - activer/désactiver des fonctionnalités sans redéploiement (LaunchDarkly, Unleash, ou table DB simple)
- **API versioning** - préfixe `/api/v2/` avec politique de dépréciation et sunset headers pour ne pas casser les clients existants

---

## Observabilité

- **Métriques** (Prometheus + Grafana) - latence p95/p99, taux d'erreur, queue depth Taskiq, stats pool DB
- **Tracing distribué** (OpenTelemetry) - tracer une requête de bout en bout à travers les services
- **Sentry** - capture d'erreurs en production avec grouping, alertes et contexte utilisateur
- **Health checks enrichis** - endpoint `/health` avec état détaillé (DB, Redis, broker) pour les load balancers

---

## Developer experience

- **SDK client généré** - générer un client Python/TypeScript depuis le schéma OpenAPI (openapi-generator)
- **Collection Postman / Bruno** - collection versionnée dans le repo pour tester l'API manuellement
- **Seed enrichi** - compléter `scripts/seed.py` avec des données cohérentes et volumineuses pour tester les perfs et la pagination
