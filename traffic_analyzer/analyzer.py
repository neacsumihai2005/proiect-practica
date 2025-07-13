# traffic_analyzer/analyzer.py

from scapy.all import sniff, IP, TCP
import json
import os
import time

LOG_FILE = "/logs/traffic_logs.json"
os.makedirs("/logs", exist_ok=True)

def packet_callback(packet):
    if IP in packet and TCP in packet:
        ip_layer = packet[IP]
        tcp_layer = packet[TCP]
        
        data = {
            "timestamp": time.time(),
            "src_ip": ip_layer.src,
            "dst_ip": ip_layer.dst,
            "src_port": tcp_layer.sport,
            "dst_port": tcp_layer.dport,
            "flags": str(tcp_layer.flags),
            "payload": bytes(tcp_layer.payload).hex() if tcp_layer.payload else None,
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
        print(f"[+] Logged packet: {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}")

def main():
    print("[*] Starting packet sniffing on interface eth0...")
    sniff(filter="tcp", prn=packet_callback, store=False, iface="eth0")

if __name__ == "__main__":
    main()

