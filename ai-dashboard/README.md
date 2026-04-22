# AI-Powered Dashboard

Aplicación web local para analizar datos históricos de disponibilidad de tiendas y hacer preguntas en lenguaje natural sobre la misma capa analítica que usa el dashboard.

El dataset principal corresponde a exportaciones wide de monitoreo sintético: cada CSV trae una fila con la métrica
`synthetic_monitoring_visible_stores` y muchas columnas de timestamps con granularidad nativa cercana a 10 segundos. El backend
transpone esas columnas a una serie temporal normalizada antes de calcular KPIs, tendencias, distribución, anomalías y ventanas de monitoreo.

## Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts
- Backend: Python, FastAPI
- Datos: DuckDB
- AI: Gemini API con function calling ejecutado en backend
- Arquitectura: monolito modular

## Estructura Del Proyecto

```text
ai-dashboard/
  backend/app/              App FastAPI, ingesta, analítica y tools del chat
  frontend/src/             Dashboard React y UI del chat
  data/extracted/           Carpeta principal de CSVs
  data/raw/                 Fallback opcional con zip si extracted está vacío
  data/processed/           DuckDB local generado
  docs/                     Arquitectura y notas de presentación
```

## Ubicación De Los Datos

Ubica los CSVs en:

```text
data/extracted/
```

Esta es la fuente principal. El backend lee automáticamente todos los CSVs válidos desde esa carpeta.

`data/raw/` es solo un fallback. Si `data/extracted/` está vacío, el backend busca un zip en `data/raw/`, lo extrae en `data/extracted/` y carga los CSVs extraídos.

El frontend nunca lee archivos locales.

## Configuración Del Backend

Desde `ai-dashboard/backend`:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Crea un archivo de entorno local si lo necesitas:

```bash
cp ../.env.example .env
```

Para habilitar el chat con AI, configura una API key de Gemini:

```bash
GEMINI_API_KEY=tu_api_key
MODEL_NAME=gemini-2.5-flash
```

`GOOGLE_API_KEY` también funciona como alias de compatibilidad, pero `GEMINI_API_KEY` es el nombre preferido.

Ejecuta el backend:

```bash
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Endpoints principales:

- `GET /health`
- `POST /api/data/load`
- `GET /api/data/status`
- `GET /api/data/sources`
- `GET /api/filters`
- `POST /api/analytics/kpis`
- `POST /api/analytics/availability-trend`
- `POST /api/analytics/delta-trend`
- `POST /api/analytics/top-unstable-stores`
- `POST /api/analytics/distribution`
- `POST /api/analytics/stores-table`
- `POST /api/analytics/hourly-heatmap`
- `POST /api/analytics/period-comparison`
- `POST /api/analytics/monitoring-windows`
- `POST /api/chat`
- `GET /api/chat/suggestions`

## Cargar Datos

Después de ubicar los CSVs en `data/extracted/`, ejecuta:

```bash
curl -X POST http://127.0.0.1:8000/api/data/load
```

Consulta el estado de la carga:

```bash
curl http://127.0.0.1:8000/api/data/status
```

La ingesta crea o reemplaza estas tablas en DuckDB:

- `availability_points`
- `availability_enriched`
- `load_metadata`
- `ingestion_file_reports`
- `monitoring_windows`

## Configuración Del Frontend

Desde `ai-dashboard/frontend`:

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Abre:

```text
http://127.0.0.1:5173/
```

El frontend espera esta variable:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Cómo Usar La App

1. Inicia el backend.
2. Carga los datos con `POST /api/data/load`.
3. Inicia el frontend.
4. Usa los filtros para elegir rango de fechas, métrica, ventanas fuente, granularidad, rango horario, umbral y escala Y.
5. Revisa KPIs, tendencia de línea/área, delta, distribución, heatmap, comparación de períodos y tabla de ventanas.
6. Haz preguntas en el chat. El chat llama tools del backend y usa el mismo servicio analítico que el dashboard.

## Nota Sobre El Dataset

Los CSVs actuales contienen series agregadas de disponibilidad, no registros individuales por tienda. Por eso la UI muestra las entidades de ranking y tabla como ventanas de monitoreo.

Algunos archivos pueden tener valores en órdenes de magnitud muy distintos. El dashboard permite escala lineal, automática o logarítmica para que sea posible comparar ramp-ups pequeños con ventanas en millones sin que la línea quede aplastada.

Los endpoints del backend todavía incluyen `stores` en algunos nombres porque son contratos estables para soportar datos futuros con granularidad real por tienda.

## Verificación

Chequeo rápido del backend:

```bash
./.venv/bin/python -m compileall app tests
```

Chequeo rápido del frontend:

```bash
npm run build
```

Si `pytest` está instalado en el entorno del backend:

```bash
./.venv/bin/python -m pytest tests
```
