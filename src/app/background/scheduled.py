from app.core.config.broker import broker
from app.scheduler.jobs.movie_stats import refresh_all_movie_stats
from app.scheduler.jobs.purge import purge_expired_tokens, purge_soft_deleted
from app.scheduler.jobs.trending import log_trending_movies


@broker.task(schedule=[{"cron": "0 2 * * *"}])
async def task_refresh_movie_stats() -> None:
    await refresh_all_movie_stats()


@broker.task(schedule=[{"cron": "0 8 * * MON"}])
async def task_log_trending() -> None:
    await log_trending_movies()


@broker.task(schedule=[{"cron": "0 3 * * *"}])
async def task_purge_soft_deleted() -> None:
    await purge_soft_deleted()


@broker.task(schedule=[{"cron": "30 3 * * SUN"}])
async def task_purge_expired_tokens() -> None:
    await purge_expired_tokens()
