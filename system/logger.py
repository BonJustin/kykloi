"""
system/logger.py - Centralized Telemetry and Logging Engine for Project Kykloi.
Provides ANSI colorized terminal streams, persistent file sinks, and routine tracing.
"""

import contextlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Enable Virtual Terminal Processing on Windows 10+ for ANSI escape codes
if sys.platform == "win32":
    os.system("")

DEFAULT_LOG_FILE = Path(__file__).resolve().parent / "kykloi.log"


class AnsiColorFormatter(logging.Formatter):
    """Formats log records with ANSI colors for interactive terminal displays."""

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[1;31m",  # Bold Red
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        time_str = self.formatTime(record, "%H:%M:%S")
        name = record.name
        if name.startswith("kykloi."):
            name = name[7:]

        lvl_name = f"{record.levelname:<5}"
        prefix = f"{self.DIM}[{time_str}]{self.RESET} {color}{lvl_name}{self.RESET} {self.DIM}[{name}]{self.RESET}"
        message = record.getMessage()

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message = f"{message}\n{record.exc_text}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        return f"{prefix} {message}"


class PlainFileFormatter(logging.Formatter):
    """Deterministic plain-text formatter for file logging with ISO-8601 timestamps."""

    def format(self, record: logging.LogRecord) -> str:
        time_str = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        lvl_name = f"{record.levelname:<8}"
        name = record.name
        message = record.getMessage()

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message = f"{message}\n{record.exc_text}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"

        return f"{time_str} | {lvl_name} | {name:<24} | {message}"


def setup_logging(
    subsystem: str = "core",
    verbose: bool = False,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
) -> logging.Logger:
    """Configures the root Kykloi logger with console and optional file handlers."""
    root_logger = logging.getLogger("kykloi")
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers to prevent duplicate lines on re-initialization
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(AnsiColorFormatter())
        root_logger.addHandler(console_handler)

    target_log_file = log_file if log_file is not None else DEFAULT_LOG_FILE
    if target_log_file:
        target_log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(target_log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(PlainFileFormatter())
        root_logger.addHandler(file_handler)

    return logging.getLogger(f"kykloi.{subsystem}")


def get_logger(subsystem: str) -> logging.Logger:
    """Retrieves a scoped child logger."""
    return logging.getLogger(f"kykloi.{subsystem}")


@contextlib.contextmanager
def timed_step(logger: logging.Logger, operation_name: str, level: int = logging.INFO):
    """Context manager for tracing operational subroutines with duration telemetry."""
    start_time = time.perf_counter()
    logger.log(level, "STARTED: %s", operation_name)
    try:
        yield
        elapsed = (time.perf_counter() - start_time) * 1000.0
        logger.log(level, "FINISHED: %s (%.2f ms)", operation_name, elapsed)
    except Exception as err:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        logger.error("FAILED: %s after %.2f ms: %s", operation_name, elapsed, err)
        raise
