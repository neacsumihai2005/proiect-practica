# c2_server/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY c2_server.py .

RUN pip install flask

EXPOSE 5000

CMD ["python", "c2_server.py"]

