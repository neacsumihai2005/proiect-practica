#!/usr/bin/env python3
import threading
import time
import re
import logging
from logging.handlers import RotatingFileHandler
from scapy.all import sniff, TCP, IP

LOG_FILE = "/var/log/auth.log"   # Adaptează dacă folosești alt fișier (ex: /var/log/secure)
OUTPUT_LOG = "/var/log/ssh_monitor.log"

# Configurare RotatingFileHandler
logger = logging.getLogger("ssh_monitor")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    OUTPUT_LOG,
    maxBytes=10_000,  # 10kB, înainte de rotire
    backupCount=3
)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Regex-uri pentru failed / successful login
RE_FAILED = re.compile(r'Failed password.* from (?P<ip>\d+\.\d+\.\d+\.\d+)')
RE_SUCCESS = re.compile(r'Accepted password.* from (?P<ip>\d+\.\d+\.\d+\.\d+)')

def detect_ssh_syn(pkt):
    """Loghează când vine un SYN către portul 22."""
    if pkt.haslayer(TCP) and pkt.haslayer(IP):
        tcp = pkt[TCP]
        ip = pkt[IP]
        if tcp.dport == 22 and tcp.flags == 'S':
            logger.info(f"SSH SYN attempt from {ip.src}")
def tail_logs():
    """Monitorizează log-ul sistemului pentru login-uri SSH."""
    try:
        with open(LOG_FILE, "r") as f:
            # mergem la finalul fișierului
            f.seek(0, 2)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue

                m = RE_FAILED.search(line)
                if m:
                    logger.warning(f"SSH login FAILED from {m.group('ip')}")
                    continue

                m = RE_SUCCESS.search(line)
                if m:
                    logger.info(f"SSH login SUCCESS from {m.group('ip')}")
    except FileNotFoundError:
        logger.error(f"Log file {LOG_FILE} not found")
    except Exception as e:
        logger.error(f"Unexpected error in tail_logs: {e}")

def main():
    t = threading.Thread(target=tail_logs, daemon=True)
    t.start()
    sniff(filter="tcp port 22", prn=detect_ssh_syn, store=0)

if __name__ == "__main__":
    main()
