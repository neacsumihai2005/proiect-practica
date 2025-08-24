#!/usr/bin/env python3
"""
mitm_daemon.py

Porneste mitmdump in transparent mode si logheaza stdout/stderr intr-un fisier cu RotatingFileHandler.
Restart automat daca mitmdump moare.
Rulat ca root (transparent mode necesita privilegii).
"""

import subprocess
import time
import shutil
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import signal

# Config
MITMDUMP_BIN = shutil.which("mitmdump") or "/usr/bin/mitmdump"
MITM_CMD = [
    MITMDUMP_BIN,
    "--mode", "transparent",
    "--listen-port", "8080",
    "--ssl-insecure",
    "--set", "console_eventlog_verbosity=info"
]
LOG_PATH = "/var/log/mitmproxy_activity.log"
MAX_BYTES = 10 * 1024 * 1024   # 10 MB
BACKUP_COUNT = 7
RESTART_DELAY = 5  # secunde

# Setup logger with rotating file handler
logger = logging.getLogger("mitm_daemon")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_PATH, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to stdout for systemd journal visibility
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

def sigterm_handler(signum, frame):
    logger.info("Received signal %s, exiting.", signum)
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

def ensure_bin():
    if not os.path.isfile(MITMDUMP_BIN) or not os.access(MITMDUMP_BIN, os.X_OK):
        logger.error("mitmdump not found at %s or not executable. Install mitmproxy.", MITMDUMP_BIN)
        raise SystemExit(1)

def run_loop():
    ensure_bin()
    logger.info("Starting mitm_daemon; command: %s", " ".join(MITM_CMD))
    while True:
        try:
            proc = subprocess.Popen(MITM_CMD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            logger.info("mitmdump started, pid=%s", proc.pid)
            # Citim linie cu linie si logam
            if proc.stdout is not None:
                for line in proc.stdout:
                    # strip newline dar pastram legibilitatea
                    logger.info(line.rstrip())
            # asteptam finalizarea
            ret = proc.wait()
            logger.warning("mitmdump exited with code %s", ret)
        except Exception as e:
            logger.exception("Error while running mitmdump: %s", e)
        logger.info("Restart mitmdump in %s seconds...", RESTART_DELAY)
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    if os.geteuid() != 0:
        logger.warning("It is recommended to run mitm_daemon as root for transparent mode.")
    try:
        run_loop()
    except KeyboardInterrupt:
        logger.info("mitm_daemon interrupted by keyboard, exiting.")

