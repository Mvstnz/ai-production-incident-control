FROM python:3.12.10-slim
WORKDIR /app
COPY backend/requirements.lock.txt backend/requirements.lock.txt
RUN pip install --no-cache-dir -r backend/requirements.lock.txt
COPY backend backend
COPY database database
COPY fixtures fixtures
COPY config config
COPY prompts prompts
COPY sops sops
RUN mkdir -p .local
USER 10001:10001
