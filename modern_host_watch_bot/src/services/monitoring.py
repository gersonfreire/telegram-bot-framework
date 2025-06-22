"""
Host monitoring service.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Bot
from telegram.ext import JobQueue

from ..models.host import HostJob, HostStatus
from ..utils.network import network_checker
from ..services.persistence import db_manager
from ..config.settings import settings

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for managing host monitoring jobs."""
    
    def __init__(self, bot: Bot, job_queue: JobQueue):
        self.bot = bot
        self.job_queue = job_queue
        self.active_jobs: Dict[str, HostJob] = {}
    
    async def add_host_job(self, job: HostJob) -> bool:
        """Add a new host monitoring job."""
        try:
            # Check if job already exists
            if job.job_id in self.active_jobs:
                logger.warning(f"Job {job.job_id} already exists")
                return False
            
            # Save to database
            if not await db_manager.save_host_job(job):
                logger.error(f"Failed to save job {job.job_id} to database")
                return False
            
            # Add to job queue
            self.job_queue.run_repeating(
                self._monitor_host_job,
                interval=job.host_config.interval_seconds,
                first=job.host_config.interval_seconds,
                name=job.job_name,
                data=job.job_id
            )
            
            # Add to active jobs
            self.active_jobs[job.job_id] = job
            
            logger.info(f"Added monitoring job for {job.host_config.host_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding host job {job.job_id}: {e}")
            return False
    
    async def remove_host_job(self, job_id: str) -> bool:
        """Remove a host monitoring job."""
        try:
            if job_id not in self.active_jobs:
                logger.warning(f"Job {job_id} not found in active jobs")
                return False
            
            job = self.active_jobs[job_id]
            
            # Remove from job queue
            try:
                self.job_queue.get_jobs_by_name(job.job_name)[0].schedule_removal()
            except (IndexError, KeyError):
                logger.warning(f"Job {job_id} not found in job queue")
            
            # Mark as inactive in database
            if not await db_manager.delete_host_job(job_id):
                logger.error(f"Failed to delete job {job_id} from database")
                return False
            
            # Remove from active jobs
            del self.active_jobs[job_id]
            
            logger.info(f"Removed monitoring job for {job.host_config.host_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing host job {job_id}: {e}")
            return False
    
    async def update_job_interval(self, job_id: str, new_interval: int) -> bool:
        """Update the interval of a monitoring job."""
        try:
            if job_id not in self.active_jobs:
                logger.warning(f"Job {job_id} not found in active jobs")
                return False
            
            job = self.active_jobs[job_id]
            
            # Remove old job
            await self.remove_host_job(job_id)
            
            # Update interval
            job.host_config.interval_seconds = new_interval
            job.updated_at = datetime.utcnow()
            
            # Add new job with updated interval
            return await self.add_host_job(job)
            
        except Exception as e:
            logger.error(f"Error updating job interval for {job_id}: {e}")
            return False
    
    async def _monitor_host_job(self, context) -> None:
        """Monitor a single host job."""
        job_id = context.job.data
        
        try:
            if job_id not in self.active_jobs:
                logger.warning(f"Job {job_id} not found in active jobs")
                return
            
            job = self.active_jobs[job_id]
            host_address = job.host_config.host_address
            port = job.host_config.port
            
            logger.debug(f"Monitoring host {host_address}:{port}")
            
            # Perform comprehensive check
            ping_success, port_open, response_time = await network_checker.check_host_comprehensive(
                host_address, port
            )
            
            # Update status
            new_status = HostStatus(
                host_address=host_address,
                is_online=ping_success,
                port_open=port_open,
                last_check=datetime.utcnow(),
                response_time_ms=response_time
            )
            
            # Update consecutive failures
            if ping_success and port_open:
                new_status.consecutive_failures = 0
            else:
                new_status.consecutive_failures = job.host_status.consecutive_failures + 1
                new_status.last_failure = datetime.utcnow()
            
            # Update job status
            job.update_status(new_status)
            
            # Save to database
            await db_manager.update_host_status(job_id, new_status)
            
            # Send notifications if needed
            await self._handle_notifications(job, new_status)
            
            logger.debug(f"Host {host_address} check completed: ping={ping_success}, port={port_open}")
            
        except Exception as e:
            logger.error(f"Error monitoring host job {job_id}: {e}")
    
    async def _handle_notifications(self, job: HostJob, status: HostStatus) -> None:
        """Handle notifications for host status changes."""
        try:
            # Get user preferences
            user = await db_manager.get_user(job.user_id)
            if not user or not user.preferences.enable_notifications:
                return
            
            # Check if we should send notification
            should_notify = False
            
            if not status.is_online or not status.port_open:
                # Send notification on failure
                should_notify = True
            elif user.preferences.show_success_logs and (status.is_online and status.port_open):
                # Send success notification if enabled
                should_notify = True
            
            if should_notify:
                message = self._format_status_message(job, status)
                await self.bot.send_message(
                    chat_id=job.user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error handling notifications for job {job.job_id}: {e}")
    
    def _format_status_message(self, job: HostJob, status: HostStatus) -> str:
        """Format status message for notification."""
        host_address = job.host_config.host_address
        port = job.host_config.port
        
        if status.is_online and status.port_open:
            status_icon = "🟢"
            status_text = "Online"
            response_time = f" ({status.response_time_ms}ms)" if status.response_time_ms else ""
        else:
            status_icon = "🔴"
            if not status.is_online:
                status_text = "Offline"
            else:
                status_text = f"Port {port} Closed"
            response_time = ""
        
        message = f"{status_icon} *Host Status Update*\n\n"
        message += f"*Host:* `{host_address}`\n"
        message += f"*Status:* {status_text}{response_time}\n"
        message += f"*Port:* {port}\n"
        message += f"*Time:* {status.last_check.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    async def load_all_jobs(self) -> None:
        """Load all active jobs from database."""
        try:
            jobs = await db_manager.get_host_jobs()
            
            for job in jobs:
                if job.is_active:
                    # Add to job queue
                    self.job_queue.run_repeating(
                        self._monitor_host_job,
                        interval=job.host_config.interval_seconds,
                        first=job.host_config.interval_seconds,
                        name=job.job_name,
                        data=job.job_id
                    )
                    
                    # Add to active jobs
                    self.active_jobs[job.job_id] = job
            
            logger.info(f"Loaded {len(jobs)} monitoring jobs from database")
            
        except Exception as e:
            logger.error(f"Error loading jobs from database: {e}")
    
    async def get_user_jobs(self, user_id: int) -> List[HostJob]:
        """Get all jobs for a specific user."""
        return [job for job in self.active_jobs.values() if job.user_id == user_id]
    
    async def get_job_by_host(self, user_id: int, host_address: str) -> Optional[HostJob]:
        """Get job by host address for a specific user."""
        for job in self.active_jobs.values():
            if job.user_id == user_id and job.host_config.host_address == host_address:
                return job
        return None 