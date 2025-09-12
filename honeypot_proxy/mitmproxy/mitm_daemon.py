#!/usr/bin/env python3
"""
mitm_daemon.py

Porneste mitmdump in transparent mode si logheaza stdout/stderr intr-un fisier cu RotatingFileHandler.
Restart automat daca mitmdump moare.
Rulat ca root (transparent mode necesita privilegii).
Toate path-urile si porturile sunt placeholders pentru configurare usoara.
"""

import subprocess
import time
import shutil
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import signal
from pathlib import Path

# ===================== CONFIGURARE =====================
# Path catre binar mitmdump
MITMDUMP_BIN = shutil.which("mitmdump") or "/usr/bin/mitmdump"

# Comanda de lansare mitmdump
MITM_CMD = [
    MITMDUMP_BIN,
    "--mode", "transparent",
    "--listen-port", "{MITM_PORT}",  # <-- inlocuieste cu portul dorit
    "--set", "console_eventlog_verbosity=info"
]

# Log rotating
LOG_PATH = "{LOG_FILE_PATH}"  # <-- inlocuieste cu path-ul dorit pentru log ("/var/log/mitmproxy_activity.log")
MAX_BYTES = 10 * 1024 * 1024   # 10 MB
BACKUP_COUNT = 7
RESTART_DELAY = 5  # secunde

# SSL keylog file (folosit de browsere pentru decriptarea TLS)
SSLKEYLOG_PATH = os.path.expanduser("{USER_HOME}/.mitmproxy/sslkeylogfile.txt")  # <-- placeholder user
SSLKEYLOG_MODE = 0o600
# ========================================================

# Setup logger
logger = logging.getLogger("mitm_daemon")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_PATH, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log si la stdout pentru systemd/journal
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

def ensure_sslkeylogfile():
    """
    Verifica existenta fisierului SSLKEYLOGFILE, il creeaza daca lipseste si seteaza permisiuni restrictive.
    """
    path = Path(SSLKEYLOG_PATH).expanduser()
    try:
        if not path.exists():
            logger.info("SSL keylog file nu exista; il creez la %s", str(path))
            path.write_bytes(b"")  # fisier gol
            path.chmod(SSLKEYLOG_MODE)
            logger.info("Setat chmod %o pentru %s", SSLKEYLOG_MODE, str(path))
        else:
            cur_mode = path.stat().st_mode & 0o777
            if cur_mode != SSLKEYLOG_MODE:
                logger.info("Permisiuni curente %o pentru %s; le schimb in %o", cur_mode, str(path), SSLKEYLOG_MODE)
                path.chmod(SSLKEYLOG_MODE)
    except Exception as e:
        logger.exception("Eroare la pregatirea sslkeylogfile: %s", e)
        raise

def run_loop():
    ensure_bin()
    logger.info("Starting mitm_daemon; command: %s", " ".join(MITM_CMD))
    while True:
        try:
            ensure_sslkeylogfile()
            env = os.environ.copy()
            env['SSLKEYLOGFILE'] = SSLKEYLOG_PATH
            logger.info("Exporting SSLKEYLOGFILE=%s for mitmdump process", SSLKEYLOG_PATH)
            
            proc = subprocess.Popen(
                MITM_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
            logger.info("mitmdump started, pid=%s", proc.pid)
            
            if proc.stdout is not None:
                for line in proc.stdout:
                    logger.info(line.rstrip())
            
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
