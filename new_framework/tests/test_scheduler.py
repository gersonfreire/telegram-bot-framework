"""
Tests for the Scheduler class.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from tlgfwk.core.scheduler import JobScheduler, Job, JobStatus, TriggerType


class TestJob:
    """Test cases for Job class."""
    
    def test_job_creation(self):
        """Test creating a job."""
        async def test_func():
            return "test"
        
        job = Job(
            id="test_job",
            func=test_func,
            trigger="interval",
            kwargs={"seconds": 30},
            name="Test Job",
            description="A test job"
        )
        
        assert job.id == "test_job"
        assert job.func == test_func
        assert job.trigger == "interval"
        assert job.kwargs == {"seconds": 30}
        assert job.name == "Test Job"
        assert job.description == "A test job"
        assert job.status == JobStatus.PENDING
        assert job.next_run is None
        assert job.last_run is None
        assert job.run_count == 0
    
    def test_job_equality(self):
        """Test job equality comparison."""
        async def func1():
            pass
        
        async def func2():
            pass
        
        job1 = Job("job1", func1, "interval", {"seconds": 30})
        job2 = Job("job1", func2, "cron", {"hour": 12})  # Same ID, different details
        job3 = Job("job2", func1, "interval", {"seconds": 30})
        
        assert job1 == job2  # Same ID
        assert job1 != job3  # Different ID


class TestScheduler:
    """Test cases for JobScheduler class."""
    
    @pytest.fixture
    def scheduler(self):
        """Create a JobScheduler instance."""
        mock_bot = Mock()
        return JobScheduler(mock_bot)
    
    @pytest.fixture
    def mock_job_func(self):
        """Create a mock job function."""
        func = AsyncMock()
        func.__name__ = "mock_job"
        return func
    
    def test_initialization(self, scheduler):
        """Test Scheduler initialization."""
        assert scheduler.jobs == {}
        assert scheduler.running is False
        assert scheduler.scheduler is not None
    
    def test_add_job_interval(self, scheduler, mock_job_func):
        """Test adding an interval job."""
        job_id = scheduler.add_job(
            job_id="test_interval",
            func=mock_job_func,
            trigger="interval",
            seconds=30,
            name="Test Interval Job"
        )
        
        assert job_id == "test_interval"
        assert "test_interval" in scheduler.jobs
        job_info = scheduler.jobs["test_interval"]
        assert job_info.name == "Test Interval Job"
        assert job_info.trigger_type == TriggerType.INTERVAL
    
    def test_add_job_cron(self, scheduler, mock_job_func):
        """Test adding a cron job."""
        job = scheduler.add_job(
            job_id="test_cron",
            func=mock_job_func,
            trigger="cron",
            hour=12,
            minute=0,
            name="Test Cron Job"
        )
        
        assert job.id == "test_cron"
        assert job.trigger == "cron"
        assert job.kwargs["hour"] == 12
        assert job.kwargs["minute"] == 0
    
    def test_add_job_date(self, scheduler, mock_job_func):
        """Test adding a one-time date job."""
        run_date = datetime.now() + timedelta(minutes=1)
        
        job = scheduler.add_job(
            job_id="test_date",
            func=mock_job_func,
            trigger="date",
            run_date=run_date,
            name="Test Date Job"
        )
        
        assert job.id == "test_date"
        assert job.trigger == "date"
        assert job.kwargs["run_date"] == run_date
    
    def test_add_job_duplicate_id(self, scheduler, mock_job_func):
        """Test adding job with duplicate ID."""
        scheduler.add_job("duplicate", mock_job_func, "interval", seconds=30)
        
        with pytest.raises(ValueError, match="Job with ID 'duplicate' already exists"):
            scheduler.add_job("duplicate", mock_job_func, "interval", seconds=60)
    
    def test_remove_job_success(self, scheduler, mock_job_func):
        """Test successful job removal."""
        scheduler.add_job("removable", mock_job_func, "interval", seconds=30)
        
        result = scheduler.remove_job("removable")
        
        assert result is True
        assert "removable" not in scheduler.jobs
    
    def test_remove_job_not_found(self, scheduler):
        """Test removing non-existent job."""
        result = scheduler.remove_job("nonexistent")
        
        assert result is False
    
    def test_pause_job_success(self, scheduler, mock_job_func):
        """Test successful job pausing."""
        job = scheduler.add_job("pausable", mock_job_func, "interval", seconds=30)
        
        result = scheduler.pause_job("pausable")
        
        assert result is True
        assert job.status == JobStatus.PAUSED
    
    def test_pause_job_not_found(self, scheduler):
        """Test pausing non-existent job."""
        result = scheduler.pause_job("nonexistent")
        
        assert result is False
    
    def test_resume_job_success(self, scheduler, mock_job_func):
        """Test successful job resuming."""
        job = scheduler.add_job("resumable", mock_job_func, "interval", seconds=30)
        scheduler.pause_job("resumable")
        
        result = scheduler.resume_job("resumable")
        
        assert result is True
        assert job.status == JobStatus.RUNNING
    
    def test_resume_job_not_found(self, scheduler):
        """Test resuming non-existent job."""
        result = scheduler.resume_job("nonexistent")
        
        assert result is False
    
    def test_get_job_info_existing(self, scheduler, mock_job_func):
        """Test getting info for existing job."""
        job = scheduler.add_job(
            "info_test",
            mock_job_func,
            "interval",
            seconds=30,
            name="Info Test Job"
        )
        
        info = scheduler.get_job_info("info_test")
        
        assert info is not None
        assert info["id"] == "info_test"
        assert info["name"] == "Info Test Job"
        assert info["trigger"] == "interval"
        assert info["status"] == JobStatus.PENDING.value
        assert info["run_count"] == 0
    
    def test_get_job_info_not_found(self, scheduler):
        """Test getting info for non-existent job."""
        info = scheduler.get_job_info("nonexistent")
        
        assert info is None
    
    def test_get_all_jobs_empty(self, scheduler):
        """Test getting all jobs when empty."""
        jobs = scheduler.get_all_jobs()
        
        assert jobs == []
    
    def test_get_all_jobs_with_jobs(self, scheduler, mock_job_func):
        """Test getting all jobs."""
        scheduler.add_job("job1", mock_job_func, "interval", seconds=30)
        scheduler.add_job("job2", mock_job_func, "cron", hour=12)
        
        jobs = scheduler.get_all_jobs()
        
        assert len(jobs) == 2
        job_ids = [job["id"] for job in jobs]
        assert "job1" in job_ids
        assert "job2" in job_ids
    
    def test_start_scheduler(self, scheduler):
        """Test starting the scheduler."""
        scheduler.start()
        
        assert scheduler.running is True
    
    def test_shutdown_scheduler(self, scheduler):
        """Test shutting down the scheduler."""
        scheduler.start()
        await scheduler.shutdown()
        
        assert scheduler.running is False
    
    def test_job_execution(self, scheduler):
        """Test job execution."""
        executed = asyncio.Event()
        
        async def test_job():
            executed.set()
            return "success"
        
        scheduler.add_job("exec_test", test_job, "date", 
                               run_date=datetime.now() + timedelta(seconds=1))
        scheduler.start()
        
        # Wait for job to execute
        try:
            await asyncio.wait_for(executed.wait(), timeout=3.0)
            job = scheduler.jobs["exec_test"]
            assert job.run_count == 1
            assert job.last_run is not None
        finally:
            await scheduler.shutdown()
    
    def test_job_execution_with_args(self, scheduler):
        """Test job execution with arguments."""
        result_container = {"value": None}
        
        async def test_job(arg1, arg2, kwarg1=None):
            result_container["value"] = f"{arg1}-{arg2}-{kwarg1}"
        
        # Note: This test assumes the scheduler supports job arguments
        # The actual implementation might need to be extended
        job = scheduler.add_job(
            "args_test",
            test_job,
            "date",
            run_date=datetime.now() + timedelta(seconds=1)
        )
        
        # If the scheduler supports it, we could set job arguments
        # job.args = ["test1", "test2"]
        # job.kwargs = {"kwarg1": "test3"}
        
        scheduler.start()
        
        try:
            await asyncio.sleep(2)  # Wait for execution
            # Test would verify the result if arguments are supported
        finally:
            await scheduler.shutdown()
    
    def test_job_error_handling(self, scheduler):
        """Test job error handling."""
        error_occurred = asyncio.Event()
        
        async def failing_job():
            error_occurred.set()
            raise Exception("Job failed")
        
        job = scheduler.add_job("error_test", failing_job, "date",
                                     run_date=datetime.now() + timedelta(seconds=1))
        scheduler.start()
        
        try:
            await asyncio.wait_for(error_occurred.wait(), timeout=3.0)
            # Job should still be marked as attempted
            assert job.run_count >= 1
            # Status might be set to FAILED if the scheduler supports it
        finally:
            await scheduler.shutdown()
    
    def test_recurring_job(self, scheduler):
        """Test recurring job execution."""
        execution_count = {"count": 0}
        
        async def recurring_job():
            execution_count["count"] += 1
        
        scheduler.add_job("recurring_test", recurring_job, "interval", seconds=0.5)
        scheduler.start()
        
        try:
            # Wait for multiple executions
            await asyncio.sleep(2)
            assert execution_count["count"] >= 2
        finally:
            await scheduler.shutdown()
    
    def test_job_status_transitions(self, scheduler, mock_job_func):
        """Test job status transitions."""
        job = scheduler.add_job("status_test", mock_job_func, "interval", seconds=30)
        
        # Initial status
        assert job.status == JobStatus.PENDING
        
        # Start scheduler
        scheduler.start()
        assert job.status == JobStatus.RUNNING
        
        # Pause job
        scheduler.pause_job("status_test")
        assert job.status == JobStatus.PAUSED
        
        # Resume job
        scheduler.resume_job("status_test")
        assert job.status == JobStatus.RUNNING
        
        await scheduler.shutdown()
    
    def test_multiple_schedulers(self):
        """Test multiple scheduler instances."""
        mock_bot1 = Mock()
        mock_bot2 = Mock()
        scheduler1 = Scheduler(mock_bot1)
        scheduler2 = Scheduler(mock_bot2)
        
        async def job1():
            pass
        
        async def job2():
            pass
        
        await scheduler1.add_job("job1", job1, "interval", seconds=30)
        await scheduler2.add_job("job2", job2, "interval", seconds=30)
        
        assert len(scheduler1.jobs) == 1
        assert len(scheduler2.jobs) == 1
        assert "job1" in scheduler1.jobs
        assert "job2" in scheduler2.jobs
        assert "job1" not in scheduler2.jobs
        assert "job2" not in scheduler1.jobs
    
    def test_scheduler_persistence_hooks(self, scheduler):
        """Test scheduler persistence hooks (if implemented)."""
        # This would test saving/loading job state
        # Currently a placeholder for future persistence features
        
        async def persistent_job():
            pass
        
        job = scheduler.add_job("persistent", persistent_job, "interval", seconds=30)
        
        # If persistence is implemented, test:
        # - Job state is saved
        # - Job state can be restored
        # - Jobs survive scheduler restart
        
        assert job.id == "persistent"
    
    def test_job_metadata(self, scheduler, mock_job_func):
        """Test job metadata handling."""
        metadata = {
            "created_by": "test_user",
            "priority": "high",
            "tags": ["important", "daily"]
        }
        
        job = scheduler.add_job(
            "metadata_test",
            mock_job_func,
            "interval",
            seconds=30,
            name="Metadata Test",
            description="Testing metadata",
            # metadata=metadata  # If supported
        )
        
        assert job.name == "Metadata Test"
        assert job.description == "Testing metadata"
        # If metadata is supported:
        # assert job.metadata == metadata
