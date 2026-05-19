"""Run standalone scraping scripts as subprocesses (Railway/local)."""
import asyncio
import logging
import os
import sys
from typing import Optional
from uuid import UUID

from app.database.models import ScrapingLogCreate
from app.database.supabase_client import db

logger = logging.getLogger(__name__)


def resolve_script_paths(script_name: str) -> tuple[str, str]:
    """
    Resolve project root and script path for local dev and Railway (/app).

    Returns:
        (project_root, script_path)
    """
    if os.path.exists(f"/app/{script_name}"):
        return "/app", f"/app/{script_name}"

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script_path = os.path.join(project_root, script_name)
    if os.path.exists(script_path):
        return project_root, script_path

    raise FileNotFoundError(
        f"Script not found: {script_name}. Tried /app/{script_name} and {script_path}"
    )


def resolve_python_executable(project_root: str) -> str:
    """Pick Python interpreter for subprocess."""
    venv_python = os.path.join(project_root, "venv", "bin", "python3")
    if os.path.exists(venv_python):
        return venv_python
    if os.path.exists("/opt/venv/bin/python"):
        return "/opt/venv/bin/python"
    return sys.executable


async def run_standalone_scraper(
    source_id: UUID,
    script_name: str,
    max_pages: int = 3,
    timeout_seconds: int = 3600,
) -> Optional[asyncio.subprocess.Process]:
    """
    Run a standalone scraper script (e.g. scrape_aircargonews.py) in a subprocess.

    Args:
        source_id: Source UUID (for logging on failure)
        script_name: Script filename in project root
        max_pages: Passed to script as --max-pages
        timeout_seconds: Max wait time before killing subprocess

    Returns:
        Completed process, or None if startup failed
    """
    source_id_str = str(source_id)
    try:
        project_root, script_path = resolve_script_paths(script_name)
        python_cmd = resolve_python_executable(project_root)
        subprocess_env = os.environ.copy()

        logger.info(
            "Starting standalone scraper: script=%s python=%s cwd=%s max_pages=%s",
            script_path,
            python_cmd,
            project_root,
            max_pages,
        )

        process = await asyncio.create_subprocess_exec(
            python_cmd,
            script_path,
            "--max-pages",
            str(max_pages),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_root,
            env=subprocess_env,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.error(
                "Standalone scraper timed out after %ss: %s (source %s)",
                timeout_seconds,
                script_name,
                source_id_str,
            )
            process.kill()
            await process.wait()
            _log_subprocess_failure(
                source_id,
                f"{script_name} timed out after {timeout_seconds} seconds",
            )
            return None

        stdout_text = stdout.decode("utf-8", errors="ignore") if stdout else ""
        stderr_text = stderr.decode("utf-8", errors="ignore") if stderr else ""

        if process.returncode == 0:
            logger.info("Standalone scraper completed: %s", script_name)
            if stdout_text:
                logger.info("stdout (last 800 chars): %s", stdout_text[-800:])
            return process

        logger.error(
            "Standalone scraper failed: %s exit=%s",
            script_name,
            process.returncode,
        )
        if stderr_text:
            logger.error("stderr: %s", stderr_text[-1500:])
        if stdout_text:
            logger.error("stdout: %s", stdout_text[-1500:])
        _log_subprocess_failure(
            source_id,
            f"{script_name} failed (exit {process.returncode}): {stderr_text[:300]}",
        )
        return process

    except Exception as e:
        logger.error("Error running %s for source %s: %s", script_name, source_id_str, e)
        _log_subprocess_failure(source_id, f"Subprocess error: {str(e)[:500]}")
        return None


def _log_subprocess_failure(source_id: UUID, error_message: str) -> None:
    try:
        log = ScrapingLogCreate(
            source_id=source_id,
            status="failed",
            error_message=error_message,
            articles_found=0,
        )
        db.create_scraping_log(log)
    except Exception as log_error:
        logger.error("Failed to write scraping log: %s", log_error)
