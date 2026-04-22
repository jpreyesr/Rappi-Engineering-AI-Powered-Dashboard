FROM node:20-bookworm-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
RUN npm install --no-save @rollup/rollup-linux-arm64-gnu @rollup/rollup-linux-x64-gnu
COPY frontend ./
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=demo
ENV DUCKDB_PATH=data/processed/dashboard.duckdb
ENV MODEL_NAME=gemini-2.5-flash

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY data ./data
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY docker/start.sh ./docker/start.sh

RUN chmod +x ./docker/start.sh

EXPOSE 8000

CMD ["./docker/start.sh"]
