#!/usr/bin/env python3
import threading
import time
import re
import logging
import os
from scapy.all import sniff, TCP, IP

LOG_FILE = "/var/log/auth.log"   # Adaptează dacă folosești alt fișier (ex: /var/log/secure)
OUTPUT_LOG = "/var/log/ssh_monitor.log"

# Configurare logging
logging.basicConfig(filename=OUTPUT_LOG, level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Regex-uri pentru failed / successful login
RE_FAILED = re.compile(r'Failed password.* from (?P<ip>\d+\.\d+\.\d+\.\d+)')
RE_SUCCESS = re.compile(r'Accepted password.* from (?P<ip>\d+\.\d+\.\d+\.\d+)')

def detect_ssh_syn(pkt):
    """Loghează când vine un SYN către portul 22."""
    if pkt.haslayer(TCP) and pkt.haslayer(IP):
        tcp = pkt[TCP]
        ip = pkt[IP]
        if tcp.dport == 22 and tcp.flags == 'S':
            logging.info(f"SSH SYN attempt from {ip.src}")

def tail_logs():
    f = None
    last_inode = None
    position = 0
    while True:
        try:
            if f is None:
                f = open(LOG_FILE, "r")
                last_inode = os.fstat(f.fileno()).st_ino
                f.seek(0, 2)  # merge la sfârșitul fișierului
                position = f.tell()

            stat = os.stat(LOG_FILE)
            current_inode = stat.st_ino
            file_size = stat.st_size

            # Dacă inode-ul s-a schimbat (rotire fișier) sau fișierul e mai mic decât poziția curentă
            if current_inode != last_inode or file_size < position:
                f.close()
                f = open(LOG_FILE, "r")
                last_inode = current_inode
                position = 0
                logging.info("[*] Log file rotated or truncated, reopened and reset position")

            f.seek(position)
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue

            position = f.tell()

            m = RE_FAILED.search(line)
            if m:
                logging.warning(f"SSH login FAILED from {m.group('ip')}")
                continue

            m = RE_SUCCESS.search(line)
            if m:
                logging.info(f"SSH login SUCCESS from {m.group('ip')}")

        except FileNotFoundError:
            logging.error(f"Log file {LOG_FILE} not found, waiting...")
            if f:
                f.close()
                f = None
            time.sleep(1)
        except Exception as e:
            logging.error(f"Unexpected error in tail_logs: {e}")
            time.sleep(1)

def main():
    t = threading.Thread(target=tail_logs, daemon=True)
    t.start()
    sniff(filter="tcp port 22", prn=detect_ssh_syn, store=0)

if __name__ == "__main__":
    main()

