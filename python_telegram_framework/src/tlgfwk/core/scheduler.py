from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from ..utils.logger import get_logger

class JobScheduler:
    """
    Manages scheduled jobs using APScheduler.

    This class provides a wrapper around APScheduler to:
    - Persist jobs across bot restarts using a SQLAlchemy job store.
    - Provide a simple interface for adding, removing, and retrieving jobs.

    Attributes:
        persistence_manager (PersistenceManager): The persistence manager instance.
        logger (logging.Logger): The logger instance.
        scheduler (AsyncIOScheduler): The APScheduler instance.
    """
    def __init__(self, persistence_manager):
        """
        Initializes the JobScheduler.

        Args:
            persistence_manager (PersistenceManager): The persistence manager.
        """
        self.persistence_manager = persistence_manager
        self.logger = get_logger(__name__)
        
        db_path = self.persistence_manager._get_path('jobs.sqlite')
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{db_path}')
        }
        
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)

    def start(self):
        """Starts the scheduler."""
        self.scheduler.start()
        self.logger.info("Scheduler started.")

    def shutdown(self):
        """Shuts down the scheduler."""
        self.scheduler.shutdown()
        self.logger.info("Scheduler shut down.")

    def add_job(self, func, trigger, **kwargs):
        """Adds a job to the scheduler."""
        return self.scheduler.add_job(func, trigger, **kwargs)

    def remove_job(self, job_id):
        """Removes a job from the scheduler."""
        self.scheduler.remove_job(job_id)

    def get_jobs(self):
        """Returns a list of all scheduled jobs."""
        return self.scheduler.get_jobs()