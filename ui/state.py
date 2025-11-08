import streamlit as st
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from ui.api_client import run_backtest


class BackgroundJobManager:
    """Manages background jobs with persistent state across page navigation."""

    def __init__(self):
        # Initialize session state if it doesn't exist
        if not hasattr(st, 'session_state'):
            return

        if "job_manager" not in st.session_state:
            st.session_state["job_manager"] = {
                "jobs": {},  # job_id -> job_data
                "active_jobs": set(),  # currently running job IDs
            }

    def get_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all jobs (completed and active)."""
        self._ensure_initialized()
        return st.session_state["job_manager"]["jobs"]

    def get_active_jobs(self) -> set:
        """Get currently running job IDs."""
        self._ensure_initialized()
        return st.session_state["job_manager"]["active_jobs"]

    def _ensure_initialized(self):
        """Ensure session state is initialized."""
        if "job_manager" not in st.session_state:
            st.session_state["job_manager"] = {
                "jobs": {},  # job_id -> job_data
                "active_jobs": set(),  # currently running job IDs
            }

    def start_backtest_job(self, symbol: str, start_date: str, end_date: str, initial_cash: float) -> str:
        """Start a background backtest job."""
        self._ensure_initialized()
        job_id = str(uuid.uuid4())

        # Create job entry
        job_data = {
            "id": job_id,
            "type": "backtest",
            "status": "running",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_cash": initial_cash,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "result": None,
            "error": None,
            "thread": None
        }

        # Add to jobs
        st.session_state["job_manager"]["jobs"][job_id] = job_data
        st.session_state["job_manager"]["active_jobs"].add(job_id)

        # Start background thread
        thread = threading.Thread(target=self._run_backtest_job, args=(job_id,))
        thread.daemon = True
        job_data["thread"] = thread
        thread.start()

        return job_id

    def _run_backtest_job(self, job_id: str):
        """Run the backtest job in background thread."""
        try:
            job = st.session_state["job_manager"]["jobs"][job_id]

            # Update progress
            job["progress"] = 5
            job["status"] = "running"

            # Create progress callback
            def progress_callback(progress: float, message: str = ""):
                job["progress"] = progress
                if message:
                    job["progress_message"] = message

            # Import and setup backtest service with progress callback
            from app.services.backtest_service import BacktestService
            backtest_svc = BacktestService()
            backtest_svc.set_progress_callback(progress_callback)

            # Run the backtest with progress tracking
            result = backtest_svc.run(
                job["symbol"],
                job["start_date"],
                job["end_date"],
                job["initial_cash"]
            )

            # Mark as completed
            job["status"] = "completed"
            job["result"] = result
            job["progress"] = 100
            job["completed_at"] = datetime.now().isoformat()

        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            job["progress"] = 100
        finally:
            # Remove from active jobs
            self._ensure_initialized()
            if job_id in st.session_state["job_manager"]["active_jobs"]:
                st.session_state["job_manager"]["active_jobs"].remove(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and data."""
        self._ensure_initialized()
        jobs = st.session_state["job_manager"]["jobs"]
        return jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up completed jobs older than max_age_hours."""
        self._ensure_initialized()
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        jobs = st.session_state["job_manager"]["jobs"]

        to_remove = []
        for job_id, job in jobs.items():
            if job["status"] in ["completed", "failed"]:
                created_at = datetime.fromisoformat(job["created_at"]).timestamp()
                if created_at < cutoff_time:
                    to_remove.append(job_id)

        for job_id in to_remove:
            del jobs[job_id]


# Global job manager instance
job_manager = BackgroundJobManager()


def get_state() -> dict:
    if "app_state" not in st.session_state:
        st.session_state["app_state"] = {}
    return st.session_state["app_state"]


