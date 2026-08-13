import importlib
import os
import time
import platform
import psutil
from sqlalchemy import text as sql_text

from extensions import db
from utils.logger import get_recent_logs, logger


def _check_database():
    """Can we actually round-trip a query against the configured DB?"""
    try:
        db.session.execute(sql_text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Health check: database unreachable: {e}")
        return False


def _check_lexicon():
    """Is the Setswana lexicon table populated (not just present but empty)?"""
    try:
        from models import LexiconEntry
        return LexiconEntry.query.count() > 0
    except Exception as e:
        logger.error(f"Health check: lexicon unreadable: {e}")
        return False


def _check_sentiment_engine():
    """Is the transformers package available for the sentiment pipeline to load?

    Deliberately doesn't load an actual model here — that's a multi-second,
    memory-heavy operation and a health check should stay cheap. Confirming
    the package itself imports is a real, honest signal of whether sentiment
    analysis can work at all, short of that cost.
    """
    try:
        importlib.import_module('transformers')
        return True
    except Exception as e:
        logger.error(f"Health check: sentiment engine unavailable: {e}")
        return False


def _check_storage():
    """Is the data directory actually writable?"""
    try:
        return os.access('data', os.W_OK)
    except Exception as e:
        logger.error(f"Health check: storage unwritable: {e}")
        return False


class SystemService:
    @staticmethod
    def get_system_health():
        """
        Collects real system health metrics, including live checks against
        the database, lexicon, sentiment engine, and storage — replacing
        what used to be four hardcoded "PASS" entries.
        """
        checks = [
            ('API_GATEWAY', lambda: True),  # tautological: if this handler ran, the gateway is up
            ('DATABASE', _check_database),
            ('LEXICON', _check_lexicon),
            ('SENTIMENT_ENGINE', _check_sentiment_engine),
            ('STORAGE', _check_storage),
        ]

        services = []
        for name, check_fn in checks:
            start = time.time()
            ok = check_fn()
            latency_ms = round((time.time() - start) * 1000)
            services.append({
                'name': name,
                'status': 'PASS' if ok else 'FAIL',
                'latency': f'{latency_ms}ms',
            })

        overall_status = 'healthy' if all(s['status'] == 'PASS' for s in services) else 'degraded'

        health = {
            "status": overall_status,
            "timestamp": time.time(),
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine()
            },
            "resources": {
                "cpu_usage": "0%",
                "memory_usage": "0%",
                "disk_usage": "0%"
            },
            "services": services,
        }

        # Real resource usage via psutil (cross-platform, no shell execution)
        try:
            health["resources"]["cpu_usage"] = f"{psutil.cpu_percent(interval=0.1)}%"
            health["resources"]["memory_usage"] = f"{psutil.virtual_memory().percent}%"
            health["resources"]["disk_usage"] = f"{psutil.disk_usage('/').percent}%"
        except Exception as e:
            logger.error(f"Failed to fetch real system metrics: {str(e)}")
            # Fallback values stay as 0%

        return health

    @staticmethod
    def get_logs(limit=100):
        """Retrieves recent logs from the system."""
        return get_recent_logs(limit)

    @staticmethod
    def log_event(level, message):
        """Utility to log an event from a service or route."""
        if level.upper() == "INFO":
            logger.info(message)
        elif level.upper() == "WARN" or level.upper() == "WARNING":
            logger.warning(message)
        elif level.upper() == "ERROR":
            logger.error(message)
        else:
            logger.info(f"[{level}] {message}")
