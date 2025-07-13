FROM mitmproxy/mitmproxy:latest

USER root

RUN apt-get update && apt-get install -y iptables iproute2 procps


COPY setup_iptables.sh /setup_iptables.sh
RUN chmod +x /setup_iptables.sh

COPY mitmproxy_config.py /app/mitmproxy_config.py

RUN mkdir -p /logs && chown mitmproxy:mitmproxy /logs

USER mitmproxy

EXPOSE 8080

CMD /bin/sh -c "/setup_iptables.sh && mitmdump --mode transparent -s /app/mitmproxy_config.py --set stream_websocket=True"

