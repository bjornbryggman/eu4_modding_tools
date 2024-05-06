import logging
import sys
from pathlib import Path

import structlog


def init_logger(log_level=int, log_directory=Path):
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S (UTC)"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Processors for console logging (human-friendly format)
    console_processors = shared_processors + [structlog.processors.format_exc_info, structlog.dev.ConsoleRenderer()]

    # Processors for file logging (JSON format)
    file_processors = shared_processors + [
        structlog.processors.CallsiteParameterAdder({
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
            structlog.processors.CallsiteParameter.PROCESS,
        }),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]

    if sys.stderr.isatty():
        logging.basicConfig(level=log_level, handlers=[logging.StreamHandler(sys.stdout)], format="%(message)s")

    else:
        log_directory.mkdir(parents=True, exist_ok=True)
        log_file_path = log_directory / "Log.txt"

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(), foreign_pre_chain=shared_processors
            )
        )

        logging.basicConfig(level=log_level, handlers=[file_handler], format="%(message)s")

    structlog.configure(
        processors=console_processors if sys.stderr.isatty() else file_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
