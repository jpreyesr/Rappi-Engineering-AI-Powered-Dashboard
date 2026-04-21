# Arquitectura

## Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts
- Backend: FastAPI, Pydantic, OpenAI Python SDK
- Datos: DuckDB
- AI: OpenAI con tool calling
- Forma de ejecución: monolito modular local

## Monolito Modular

El proyecto se mantiene intencionalmente como una sola aplicación local en vez de microservicios. Esto facilita correr la demo, evita complejidad de despliegue y aun así conserva límites claros mediante módulos.

Módulos del backend:

- `api/routes`: endpoints HTTP solamente
- `schemas`: contratos Pydantic de request/response
- `services`: orquestación de casos de uso y lógica de aplicación
- `repositories`: consultas a DuckDB
- `db`: helpers de conexión a base de datos
- `core`: configuración y constantes

Módulos del frontend:

- `pages`: composición de páginas
- `features/dashboard`: hooks y componentes del dashboard
- `features/chat`: hook y componente del chat
- `services`: clientes HTTP
- `types`: contratos de API
- `lib`: formateo visual y helpers de gráficos

## Flujo De Datos

1. Los CSVs se ubican en `data/extracted/`.
2. `POST /api/data/load` ejecuta la ingesta en backend.
3. La ingesta lee múltiples CSVs, ignora archivos inválidos, normaliza el formato wide de serie temporal y escribe tablas en DuckDB.
4. Los endpoints analíticos consultan DuckDB mediante `AnalyticsRepository`.
5. `AnalyticsService` transforma filas del repositorio en schemas reutilizables.
6. Los componentes del dashboard llaman endpoints analíticos mediante servicios del frontend.
7. El chat envía mensaje, filtros e historial corto al backend.
8. `ChatService` usa tool calling de OpenAI y cada tool llama el mismo `AnalyticsService` usado por el dashboard.

## Fuente De Verdad

El backend es dueño de:

- descubrimiento de archivos
- ingesta CSV
- persistencia DuckDB
- cálculos analíticos oficiales
- ejecución de tools del chatbot

El frontend es dueño de:

- layout
- interacción de filtros
- estados de carga, vacío y error
- renderizado de gráficos
- visualización de la conversación

El frontend no calcula KPIs oficiales, rankings, distribuciones ni agregados de tabla.

## Tablas En DuckDB

Tablas analíticas principales:

- `availability_points`: una fila por timestamp, métrica y ventana fuente
- `availability_enriched`: deltas, etiquetas, hora y día de semana derivados
- `load_metadata`: resumen de la última ingesta
- `ingestion_file_reports`: estado de ingesta por archivo

El dataset actual no incluye filas a nivel de tienda individual. Por eso los archivos fuente se tratan como ventanas fuente para rankings y tablas.

## Capas De API

Ingesta:

- `POST /api/data/load`
- `GET /api/data/status`

Analítica:

- `GET /api/filters`
- `POST /api/analytics/kpis`
- `POST /api/analytics/availability-trend`
- `POST /api/analytics/top-unstable-stores`
- `POST /api/analytics/distribution`
- `POST /api/analytics/stores-table`

Chat:

- `POST /api/chat`
- `GET /api/chat/suggestions`

Compatibilidad legacy:

- `GET /analytics/summary`
- `GET /analytics/timeseries`
- `POST /chat`

## Por Qué Dashboard Y Chat Comparten Analítica

El dashboard y el chatbot responden preguntas sobre el mismo dataset. Si cada uno implementara métricas por separado, podrían contradecirse.

Compartir `AnalyticsService` evita duplicación y mantiene todos los cálculos oficiales en una sola capa del backend.

El chat no es un generador libre de SQL. Llama tools restringidas como `get_kpis`, `get_availability_trend` y `get_distribution`. Esto hace que las respuestas estén más ancladas a datos reales y mantiene la API key y el acceso a datos dentro del backend.

## Configuración

Variables de entorno:

- `DUCKDB_PATH`: ruta del archivo DuckDB local
- `OPENAI_API_KEY`: API key de OpenAI, solo backend
- `MODEL_NAME`: nombre configurable del modelo preferido
- `OPENAI_MODEL`: alias de compatibilidad
- `VITE_API_BASE_URL`: URL base del backend para el frontend

La API key de OpenAI nunca se expone al navegador.
