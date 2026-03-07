# app/logger.py
import sys
from loguru import logger
import os
from pathlib import Path

def setup_logger():
    logger.remove()   # remove default handler

    # always relative to this file's location
    BASE_DIR = Path(__file__).resolve().parent.parent  # project root
    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)   # create if not exists


    # terminal — show everything
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True
    )

    # file — only errors and above
    logger.add(
        "logs/error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        rotation="10 MB",      # new file when size hits 10MB
        retention="30 days",   # delete logs older than 30 days
        compression="zip",     # compress old log files
        backtrace=True,        # full traceback on error
        diagnose=True          # show variable values in traceback
    )

    # file — all logs
    logger.add(
        "logs/app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return logger