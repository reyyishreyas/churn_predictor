from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path


def configure_logger(name: str, log_path: Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if log_path:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def append_jsonl(path: Path, payload: dict) -> None:
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
