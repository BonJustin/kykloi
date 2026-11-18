"""
system/logger.py - Centralized Telemetry and Logging Engine for Project Kykloi.
Provides ANSI colorized terminal streams, persistent file sinks, routine tracing,
and threshold-triggered FIFO log truncation (in-place halving).
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
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MiB threshold
DEFAULT_PRUNE_RATIO = 0.5  # Retain newest 50% when threshold is breached


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


class HalfPruningFileHandler(logging.FileHandler):
    """
    Append-only file handler that monitors file size and atomically purges the oldest
    records when a defined capacity threshold is reached, retaining approximately half
    of the newest log output aligned to line boundaries.
    """

    def __init__(
        self,
        filename: Path | str,
        mode: str = "a",
        encoding: str = "utf-8",
        delay: bool = False,
        max_bytes: int = DEFAULT_MAX_BYTES,
        prune_ratio: float = DEFAULT_PRUNE_RATIO,
    ):
        super().__init__(filename, mode=mode, encoding=encoding, delay=delay)
        self.max_bytes = max_bytes
        self.prune_ratio = min(max(prune_ratio, 0.1), 0.9)

    def should_prune(self) -> bool:
        """Determines whether the physical log file size exceeds the threshold."""
        if self.max_bytes <= 0:
            return False
        try:
            return os.path.getsize(self.baseFilename) >= self.max_bytes
        except OSError:
            return False

    def do_prune(self) -> None:
        """
        Closes current stream, seeks past the oldest entries to the next clean newline,
        writes the preserved segment to a temporary file, and performs an atomic replace.
        """
        if self.stream is not None:
            self.stream.flush()
            self.stream.close()
            self.stream = None

        try:
            current_size = os.path.getsize(self.baseFilename)
            if current_size < self.max_bytes:
                return

            cutoff = int(current_size * (1.0 - self.prune_ratio))
            with open(self.baseFilename, "rb") as src:
                src.seek(cutoff)
                # Discard the partial line fragment at the cut boundary
                src.readline()
                retained_bytes = src.read()

            tmp_target = Path(self.baseFilename).with_suffix(".prune.tmp")
            with open(tmp_target, "wb") as dst:
                prune_notice = (
                    f"--- [KYKLOI LOG PRUNED: {current_size} bytes -> {len(retained_bytes)} bytes] ---\n"
                ).encode(self.encoding or "utf-8")
                dst.write(prune_notice)
                dst.write(retained_bytes)

            tmp_target.replace(self.baseFilename)
        except OSError:
            pass
        finally:
            self.stream = self._open()

    def emit(self, record: logging.LogRecord) -> None:
        """Emits a record, executing size verification and conditional truncation first."""
        try:
            if self.should_prune():
                self.do_prune()
            super().emit(record)
        except Exception:
            self.handleError(record)


def setup_logging(
    subsystem: str = "core",
    verbose: bool = False,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    max_bytes: Optional[int] = None,
    prune_ratio: float = DEFAULT_PRUNE_RATIO,
) -> logging.Logger:
    """Configures the root Kykloi logger with console and pruning file handlers."""
    root_logger = logging.getLogger("kykloi")
    root_logger.setLevel(logging.DEBUG)

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

        # Allow environment configuration override if parameter not explicitly set
        effective_max_bytes = max_bytes
        if effective_max_bytes is None:
            env_val = os.environ.get("KYKLOI_LOG_MAX_BYTES")
            effective_max_bytes = (
                int(env_val) if env_val and env_val.isdigit() else DEFAULT_MAX_BYTES
            )

        file_handler = HalfPruningFileHandler(
            target_log_file,
            mode="a",
            encoding="utf-8",
            max_bytes=effective_max_bytes,
            prune_ratio=prune_ratio,
        )
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
