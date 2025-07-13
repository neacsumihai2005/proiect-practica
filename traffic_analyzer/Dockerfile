# traffic_analyzer/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y tcpdump iproute2 iputils-ping libcap2-bin

COPY analyzer.py .

RUN pip install scapy

CMD ["python", "analyzer.py"]

