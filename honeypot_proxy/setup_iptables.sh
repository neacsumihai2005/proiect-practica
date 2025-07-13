#!/bin/sh
# honeypot_proxy/setup_iptables.sh

# Activare IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Redirecționare trafic HTTP (port 80) către mitmproxy (8080)
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

