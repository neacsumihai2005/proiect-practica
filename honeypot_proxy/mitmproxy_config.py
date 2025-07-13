# honeypot_proxy/mitmproxy_config.py

import json
from mitmproxy import ctx

# Fișierul în care salvăm logurile JSON (în volum montat)
LOG_FILE = "/logs/proxy_logs.json"

def request(flow):
    data = {
        "type": "request",
        "client_ip": flow.client_conn.address[0],
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "headers": dict(flow.request.headers),
        "timestamp": flow.request.timestamp_start,
        "content": flow.request.get_text(strict=False)
    }
    append_log(data)

def response(flow):
    data = {
        "type": "response",
        "status_code": flow.response.status_code,
        "headers": dict(flow.response.headers),
        "timestamp": flow.response.timestamp_end,
        "content": flow.response.get_text(strict=False)
    }
    append_log(data)

def append_log(data):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def start():
    ctx.log.info("Proxy logging started, logs will be saved in " + LOG_FILE)

