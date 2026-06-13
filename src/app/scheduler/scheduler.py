from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config.logs import get_logger
from app.scheduler.jobs.movie_stats import run as run_movie_stats
from app.scheduler.jobs.purge import run as run_purge
from app.scheduler.jobs.purge import run_tokens as run_purge_tokens
from app.scheduler.jobs.trending import run as run_trending

logger = get_logger()
scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(run_movie_stats, CronTrigger(hour=2, minute=0), id="refresh_movie_stats")
    scheduler.add_job(
        run_trending, CronTrigger(day_of_week="mon", hour=8, minute=0), id="log_trending_movies"
    )
    scheduler.add_job(run_purge, CronTrigger(hour=3, minute=0), id="purge_soft_deleted")
    scheduler.add_job(
        run_purge_tokens,
        CronTrigger(day_of_week="sun", hour=3, minute=30),
        id="purge_expired_tokens",
    )
    scheduler.start()
    logger.info("SCHEDULER:Start", "Scheduler started with tasks.")


def stop_scheduler() -> None:
    scheduler.shutdown()
    logger.info("SCHEDULER:Stop", "Scheduler stopped.")
