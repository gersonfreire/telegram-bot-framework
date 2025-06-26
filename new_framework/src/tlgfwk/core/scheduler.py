"""
Job Scheduling System

This module provides advanced job scheduling functionality for the Telegram Bot Framework.
Built on APScheduler with persistence, monitoring, and Telegram integration.
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
import logging
import traceback
import pickle
import base64
from functools import wraps

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.job import Job
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_REMOVED
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor
    HAS_APSCHEDULER = True
except ImportError:
    HAS_APSCHEDULER = False

from ..utils.logger import get_logger


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    SCHEDULED = "scheduled"


class TriggerType(Enum):
    """Job trigger type enumeration."""
    DATE = "date"
    INTERVAL = "interval"
    CRON = "cron"


@dataclass
class JobInfo:
    """Job information container."""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    status: JobStatus
    created_at: datetime
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class JobResult:
    """Job execution result."""
    
    def __init__(self, success: bool, job_info: JobInfo, result: Any = None, error: str = None):
        self.success = success
        self.job_info = job_info
        self.result = result
        self.error = error
        self.timestamp = datetime.now()


def scheduled_job(
    trigger: Union[str, TriggerType],
    name: str = None,
    description: str = "",
    user_id: int = None,
    chat_id: int = None,
    **trigger_kwargs
):
    """
    Decorator for registering scheduled jobs.
    
    Args:
        trigger: Trigger type (date, interval, cron)
        name: Job name (defaults to function name)
        description: Job description
        user_id: Associated user ID
        chat_id: Associated chat ID
        **trigger_kwargs: Trigger-specific parameters
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Store job metadata on function
        wrapper._job_config = {
            'trigger': trigger,
            'name': name or func.__name__,
            'description': description,
            'user_id': user_id,
            'chat_id': chat_id,
            'trigger_kwargs': trigger_kwargs
        }
        
        return wrapper
    return decorator





class JobScheduler:
    """
    Advanced Job Scheduler for the Telegram Bot Framework.
    
    Provides scheduling, monitoring, and management of background jobs.
    """
    
    def __init__(self, bot_instance, config: Dict[str, Any] = None):
        """
        Initialize the job scheduler.
        
        Args:
            bot_instance: The main bot framework instance
            config: Scheduler configuration
        """
        if not HAS_APSCHEDULER:
            raise ImportError("APScheduler is required for job scheduling. Install with: pip install apscheduler")
        
        self.bot = bot_instance
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        # Job storage
        self.jobs: Dict[str, JobInfo] = {}
        self.job_functions: Dict[str, Callable] = {}
        
        # Event callbacks
        self.job_callbacks: Dict[str, List[Callable]] = {
            'job_added': [],
            'job_executed': [],
            'job_error': [],
            'job_removed': []
        }
        
        # Initialize scheduler
        self._initialize_scheduler()
        
        self.logger.info("Job scheduler initialized")
    
    def _initialize_scheduler(self):
        """Initialize the APScheduler instance."""
        # Configure job stores
        jobstores = {
            'default': MemoryJobStore()
        }
        
        # Add persistent job store if configured
        if self.config.get('use_persistent_store'):
            db_url = self.config.get('database_url', 'sqlite:///jobs.db')
            try:
                jobstores['persistent'] = SQLAlchemyJobStore(url=db_url)
                self.logger.info(f"Persistent job store configured: {db_url}")
            except Exception as e:
                self.logger.warning(f"Failed to configure persistent job store: {e}")
        
        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(max_workers=self.config.get('max_workers', 20)),
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 30
        }
        
        # Choose scheduler type based on bot's async mode
        if self.config.get('async_mode', True):
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
        else:
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
        
        # Add event listeners
        self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._on_job_added, EVENT_JOB_ADDED)
        self.scheduler.add_listener(self._on_job_removed, EVENT_JOB_REMOVED)
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Job scheduler started")
            
            # Load jobs from persistent storage
            self._load_jobs_from_storage()
            
            # Register built-in maintenance jobs
            self._register_maintenance_jobs()
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            # Save jobs to persistent storage
            self._save_jobs_to_storage()
            
            self.scheduler.shutdown(wait=True)
            self.logger.info("Job scheduler stopped")
    
    def add_job(
        self,
        func: Callable,
        trigger: Union[str, TriggerType],
        name: str = None,
        description: str = "",
        user_id: int = None,
        chat_id: int = None,
        job_id: str = None,
        replace_existing: bool = False,
        **trigger_kwargs
    ) -> str:
        """
        Add a new scheduled job.
        
        Args:
            func: Function to execute
            trigger: Trigger type
            name: Job name
            description: Job description
            user_id: Associated user ID
            chat_id: Associated chat ID
            job_id: Custom job ID
            replace_existing: Replace existing job with same ID
            **trigger_kwargs: Trigger-specific parameters
            
        Returns:
            Job ID
        """
        try:
            # Generate job ID if not provided
            if not job_id:
                job_id = f"job_{uuid.uuid4().hex[:16]}"
            
            # Check if job already exists
            if job_id in self.jobs and not replace_existing:
                raise ValueError(f"Job {job_id} already exists")
            
            # Normalize trigger type
            if isinstance(trigger, str):
                trigger = TriggerType(trigger.lower())
            
            # Create trigger
            trigger_obj = self._create_trigger(trigger, trigger_kwargs)
            
            # Register function
            func_name = f"job_func_{job_id}"
            self.job_functions[func_name] = func
            
            # Add job to scheduler
            apscheduler_job = self.scheduler.add_job(
                func=self._execute_job_wrapper,
                trigger=trigger_obj,
                id=job_id,
                name=name or func.__name__,
                args=[job_id],
                replace_existing=replace_existing
            )
            
            # Create job info
            job_info = JobInfo(
                id=job_id,
                name=name or func.__name__,
                description=description,
                trigger_type=trigger,
                trigger_config=trigger_kwargs,
                function_name=func_name,
                args=[],
                kwargs={},
                status=JobStatus.SCHEDULED,
                created_at=datetime.now(),
                next_run_time=apscheduler_job.next_run_time,
                user_id=user_id,
                chat_id=chat_id
            )
            
            # Store job info
            self.jobs[job_id] = job_info
            
            self.logger.info(f"Job added: {job_id} ({name})")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to add job: {e}")
            raise
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job ID to remove
            
        Returns:
            True if successful
        """
        try:
            # Remove from scheduler
            self.scheduler.remove_job(job_id)
            
            # Remove from storage
            if job_id in self.jobs:
                job_info = self.jobs[job_id]
                job_info.status = JobStatus.CANCELLED
                del self.jobs[job_id]
                
                # Clean up function reference
                if job_info.function_name in self.job_functions:
                    del self.job_functions[job_info.function_name]
            
            self.logger.info(f"Job removed: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """
        Pause a scheduled job.
        
        Args:
            job_id: Job ID to pause
            
        Returns:
            True if successful
        """
        try:
            self.scheduler.pause_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.PAUSED
            
            self.logger.info(f"Job paused: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        Resume a paused job.
        
        Args:
            job_id: Job ID to resume
            
        Returns:
            True if successful
        """
        try:
            self.scheduler.resume_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.SCHEDULED
                
                # Update next run time
                apscheduler_job = self.scheduler.get_job(job_id)
                if apscheduler_job:
                    self.jobs[job_id].next_run_time = apscheduler_job.next_run_time
            
            self.logger.info(f"Job resumed: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    def modify_job(self, job_id: str, **changes) -> bool:
        """
        Modify an existing job.
        
        Args:
            job_id: Job ID to modify
            **changes: Changes to apply
            
        Returns:
            True if successful
        """
        try:
            # Modify in scheduler
            self.scheduler.modify_job(job_id, **changes)
            
            # Update job info
            if job_id in self.jobs:
                job_info = self.jobs[job_id]
                
                # Update next run time
                apscheduler_job = self.scheduler.get_job(job_id)
                if apscheduler_job:
                    job_info.next_run_time = apscheduler_job.next_run_time
            
            self.logger.info(f"Job modified: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to modify job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """
        Get job information.
        
        Args:
            job_id: Job ID
            
        Returns:
            JobInfo or None if not found
        """
        job_info = self.jobs.get(job_id)
        
        if job_info:
            # Update next run time from scheduler
            apscheduler_job = self.scheduler.get_job(job_id)
            if apscheduler_job:
                job_info.next_run_time = apscheduler_job.next_run_time
        
        return job_info
    
    def list_jobs(
        self,
        user_id: int = None,
        status_filter: JobStatus = None
    ) -> List[JobInfo]:
        """
        List jobs with optional filters.
        
        Args:
            user_id: Filter by user ID
            status_filter: Filter by status
            
        Returns:
            List of JobInfo objects
        """
        jobs = list(self.jobs.values())
        
        if user_id is not None:
            jobs = [job for job in jobs if job.user_id == user_id]
        
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]
        
        # Update next run times
        for job in jobs:
            apscheduler_job = self.scheduler.get_job(job.id)
            if apscheduler_job:
                job.next_run_time = apscheduler_job.next_run_time
        
        return jobs
    
    def run_job_now(self, job_id: str) -> bool:
        """
        Execute a job immediately.
        
        Args:
            job_id: Job ID to execute
            
        Returns:
            True if successful
        """
        try:
            apscheduler_job = self.scheduler.get_job(job_id)
            if not apscheduler_job:
                raise ValueError(f"Job {job_id} not found")
            
            # Execute job
            apscheduler_job.modify(next_run_time=datetime.now())
            
            self.logger.info(f"Job scheduled for immediate execution: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run job {job_id}: {e}")
            return False
    
    def add_job_callback(self, event: str, callback: Callable):
        """
        Add a job event callback.
        
        Args:
            event: Event name (job_added, job_executed, etc.)
            callback: Callback function
        """
        if event in self.job_callbacks:
            self.job_callbacks[event].append(callback)
        else:
            self.logger.warning(f"Unknown job event: {event}")
    
    def register_job_functions(self, module_or_dict):
        """
        Register job functions from a module or dictionary.
        
        Args:
            module_or_dict: Module or dictionary containing functions
        """
        if hasattr(module_or_dict, '__dict__'):
            # Module
            for name, obj in module_or_dict.__dict__.items():
                if callable(obj) and hasattr(obj, '_job_config'):
                    self._register_decorated_job(obj)
        else:
            # Dictionary
            for name, func in module_or_dict.items():
                if callable(func) and hasattr(func, '_job_config'):
                    self._register_decorated_job(func)
    
    def _register_decorated_job(self, func: Callable):
        """Register a job function decorated with @scheduled_job."""
        config = func._job_config
        
        job_id = self.add_job(
            func=func,
            trigger=config['trigger'],
            name=config['name'],
            description=config['description'],
            user_id=config['user_id'],
            chat_id=config['chat_id'],
            **config['trigger_kwargs']
        )
        
        self.logger.info(f"Registered decorated job: {job_id} ({config['name']})")
    
    def _create_trigger(self, trigger_type: TriggerType, config: Dict[str, Any]):
        """Create APScheduler trigger from configuration."""
        if trigger_type == TriggerType.DATE:
            run_date = config.get('run_date', datetime.now())
            return DateTrigger(run_date=run_date)
        
        elif trigger_type == TriggerType.INTERVAL:
            return IntervalTrigger(**config)
        
        elif trigger_type == TriggerType.CRON:
            return CronTrigger(**config)
        
        else:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")
    
    def _execute_job_wrapper(self, job_id: str):
        """Wrapper for job execution with error handling and logging."""
        job_info = self.jobs.get(job_id)
        if not job_info:
            self.logger.error(f"Job info not found for job: {job_id}")
            return
        
        start_time = datetime.now()
        job_info.status = JobStatus.RUNNING
        job_info.last_run_time = start_time
        job_info.run_count += 1
        
        try:
            # Get job function
            func = self.job_functions.get(job_info.function_name)
            if not func:
                raise ValueError(f"Job function not found: {job_info.function_name}")
            
            # Execute function
            result = func(*job_info.args, **job_info.kwargs)
            
            # Update status
            job_info.status = JobStatus.COMPLETED
            job_info.last_error = None
            
            # Create result
            job_result = JobResult(True, job_info, result)
            
            # Trigger callbacks
            self._trigger_callbacks('job_executed', job_result)
            
            # Notify user if configured
            if job_info.chat_id and hasattr(self.bot, 'send_message'):
                self.bot.send_message(
                    job_info.chat_id,
                    f"✅ Job '{job_info.name}' completed successfully"
                )
            
            self.logger.info(f"Job executed successfully: {job_id}")
            return result
            
        except Exception as e:
            # Update error status
            job_info.status = JobStatus.FAILED
            job_info.error_count += 1
            job_info.last_error = str(e)
            
            # Create error result
            job_result = JobResult(False, job_info, error=str(e))
            
            # Trigger callbacks
            self._trigger_callbacks('job_error', job_result)
            
            # Notify user if configured
            if job_info.chat_id and hasattr(self.bot, 'send_message'):
                self.bot.send_message(
                    job_info.chat_id,
                    f"❌ Job '{job_info.name}' failed: {str(e)}"
                )
            
            self.logger.error(f"Job execution failed: {job_id} - {e}")
            self.logger.debug(traceback.format_exc())
            
            raise
        
        finally:
            # Update next run time
            apscheduler_job = self.scheduler.get_job(job_id)
            if apscheduler_job:
                job_info.next_run_time = apscheduler_job.next_run_time
            else:
                # Job was removed or completed
                job_info.next_run_time = None
                if job_info.status not in [JobStatus.FAILED, JobStatus.COMPLETED]:
                    job_info.status = JobStatus.COMPLETED
    
    def _on_job_executed(self, event):
        """Handle job executed event."""
        job_id = event.job_id
        self.logger.debug(f"Job executed event: {job_id}")
    
    def _on_job_error(self, event):
        """Handle job error event."""
        job_id = event.job_id
        self.logger.error(f"Job error event: {job_id} - {event.exception}")
    
    def _on_job_added(self, event):
        """Handle job added event."""
        job_id = event.job_id
        self.logger.debug(f"Job added event: {job_id}")
        
        # Trigger callbacks
        if job_id in self.jobs:
            self._trigger_callbacks('job_added', self.jobs[job_id])
    
    def _on_job_removed(self, event):
        """Handle job removed event."""
        job_id = event.job_id
        self.logger.debug(f"Job removed event: {job_id}")
        
        # Trigger callbacks
        if job_id in self.jobs:
            self._trigger_callbacks('job_removed', self.jobs[job_id])
    
    def _trigger_callbacks(self, event: str, data: Any):
        """Trigger callbacks for a job event."""
        for callback in self.job_callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in job callback for {event}: {e}")
    
    def _register_maintenance_jobs(self):
        """Register built-in maintenance jobs."""
        # Job cleanup (remove old completed jobs)
        self.add_job(
            func=self._cleanup_old_jobs,
            trigger=TriggerType.INTERVAL,
            name="job_cleanup",
            description="Clean up old completed jobs",
            hours=6
        )
        
        # Statistics update
        self.add_job(
            func=self._update_job_statistics,
            trigger=TriggerType.INTERVAL,
            name="job_stats",
            description="Update job statistics",
            minutes=30
        )
    
    def _cleanup_old_jobs(self):
        """Clean up old completed jobs."""
        cutoff_time = datetime.now() - timedelta(days=7)
        removed_count = 0
        
        jobs_to_remove = []
        for job_id, job_info in self.jobs.items():
            if (job_info.status in [JobStatus.COMPLETED, JobStatus.FAILED] and
                job_info.last_run_time and
                job_info.last_run_time < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old jobs")
    
    def _update_job_statistics(self):
        """Update job statistics."""
        total_jobs = len(self.jobs)
        scheduled_jobs = len([j for j in self.jobs.values() if j.status == JobStatus.SCHEDULED])
        completed_jobs = len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED])
        failed_jobs = len([j for j in self.jobs.values() if j.status == JobStatus.FAILED])
        
        stats = {
            'total': total_jobs,
            'scheduled': scheduled_jobs,
            'completed': completed_jobs,
            'failed': failed_jobs,
            'updated_at': datetime.now().isoformat()
        }
        
        # Store statistics if persistence is available
        if hasattr(self.bot, 'persistence'):
            self.bot.persistence.save_bot_data('job_statistics', stats)
        
        self.logger.debug(f"Job statistics updated: {stats}")
    
    def _save_jobs_to_storage(self):
        """Save jobs to persistent storage."""
        if hasattr(self.bot, 'persistence'):
            try:
                jobs_data = {}
                for job_id, job_info in self.jobs.items():
                    # Serialize job info
                    job_data = asdict(job_info)
                    
                    # Serialize function if possible
                    func = self.job_functions.get(job_info.function_name)
                    if func and hasattr(func, '__name__'):
                        job_data['function_module'] = getattr(func, '__module__', None)
                        job_data['function_name_original'] = func.__name__
                    
                    jobs_data[job_id] = job_data
                
                self.bot.persistence.save_bot_data('scheduled_jobs', jobs_data)
                self.logger.info(f"Saved {len(jobs_data)} jobs to persistent storage")
                
            except Exception as e:
                self.logger.error(f"Failed to save jobs to storage: {e}")
    
    def _load_jobs_from_storage(self):
        """Load jobs from persistent storage."""
        if hasattr(self.bot, 'persistence'):
            try:
                jobs_data = self.bot.persistence.load_bot_data('scheduled_jobs')
                if not jobs_data:
                    return
                
                loaded_count = 0
                for job_id, job_data in jobs_data.items():
                    try:
                        # Recreate job info
                        job_info = JobInfo(**job_data)
                        
                        # Skip completed or failed jobs
                        if job_info.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                            continue
                        
                        # Try to restore function (simplified - would need more complex logic)
                        # For now, we'll mark jobs as needing manual restoration
                        job_info.status = JobStatus.PAUSED
                        
                        self.jobs[job_id] = job_info
                        loaded_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to restore job {job_id}: {e}")
                
                self.logger.info(f"Loaded {loaded_count} jobs from persistent storage")
                
            except Exception as e:
                self.logger.error(f"Failed to load jobs from storage: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get job statistics."""
        stats = {
            'total_jobs': len(self.jobs),
            'scheduled': len([j for j in self.jobs.values() if j.status == JobStatus.SCHEDULED]),
            'running': len([j for j in self.jobs.values() if j.status == JobStatus.RUNNING]),
            'completed': len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED]),
            'failed': len([j for j in self.jobs.values() if j.status == JobStatus.FAILED]),
            'paused': len([j for j in self.jobs.values() if j.status == JobStatus.PAUSED]),
            'cancelled': len([j for j in self.jobs.values() if j.status == JobStatus.CANCELLED]),
            'scheduler_running': self.scheduler.running,
        }
        
        # Calculate total runs and errors
        total_runs = sum(job.run_count for job in self.jobs.values())
        total_errors = sum(job.error_count for job in self.jobs.values())
        
        stats['total_runs'] = total_runs
        stats['total_errors'] = total_errors
        stats['success_rate'] = (total_runs - total_errors) / total_runs if total_runs > 0 else 0
        
        return stats


@dataclass
class Job:
    """Job configuration class."""
    id: str
    func: Callable
    trigger: str
    kwargs: Dict[str, Any]
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    status: JobStatus = JobStatus.PENDING
    
    def __post_init__(self):
        if not self.name:
            self.name = self.func.__name__ if hasattr(self.func, "__name__") else "unnamed_job"
    
    def __eq__(self, other):
        """Compare jobs by ID only for equality testing."""
        if not isinstance(other, Job):
            return False
        return self.id == other.id


# Define Scheduler as an alias for JobScheduler for backward compatibility
Scheduler = JobScheduler
