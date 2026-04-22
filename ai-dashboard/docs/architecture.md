# Arquitectura

## Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts
- Backend: FastAPI, Pydantic, Gemini API por HTTP
- Datos: DuckDB
- AI: Gemini con function calling
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
4. Cada archivo válido queda registrado como una ventana de monitoreo con estadísticas y comportamiento detectado.
5. Los endpoints analíticos consultan DuckDB mediante `AnalyticsRepository`.
6. `AnalyticsService` transforma filas del repositorio en schemas reutilizables.
7. Los componentes del dashboard llaman endpoints analíticos mediante servicios del frontend.
8. El chat envía mensaje, filtros e historial corto al backend.
9. `ChatService` usa function calling de Gemini y cada tool llama el mismo `AnalyticsService` usado por el dashboard.

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
- `monitoring_windows`: estadísticas por archivo fuente y clasificación simple de comportamiento

El dataset actual no incluye filas a nivel de tienda individual. Por eso los archivos fuente se tratan como ventanas de monitoreo para rankings y tablas.

La métrica `synthetic_monitoring_visible_stores` se interpreta como conteo de tiendas visibles observado por monitoreo sintético. La granularidad nativa es de aproximadamente 10 segundos; agregaciones a 1, 5, 15 minutos, 1 hora o día se calculan en backend.

## Capas De API

Ingesta:

- `POST /api/data/load`
- `GET /api/data/status`
- `GET /api/data/sources`

Analítica:

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

El chat no es un generador libre de SQL. Llama tools restringidas como `get_kpis`, `get_availability_trend`, `get_delta_trend`, `get_distribution` y `get_monitoring_windows`. Esto hace que las respuestas estén más ancladas a datos reales y mantiene la API key y el acceso a datos dentro del backend.

## Decisiones Visuales Del Dashboard

El dashboard usa escala Y automática, lineal o logarítmica porque algunas ventanas tienen valores mucho menores que otras. La escala no cambia los datos; solo evita que series de magnitudes diferentes queden visualmente aplastadas.

Los gráficos de delta y anomalías existen porque una caída rápida puede ser más importante que el valor absoluto. El heatmap por hora/día ayuda a encontrar patrones operativos cuando hay ventanas de varios días.

## Configuración

Variables de entorno:

- `DUCKDB_PATH`: ruta del archivo DuckDB local
- `GEMINI_API_KEY`: API key de Gemini, solo backend
- `MODEL_NAME`: nombre configurable del modelo preferido
- `GOOGLE_API_KEY`: alias de compatibilidad
- `VITE_API_BASE_URL`: URL base del backend para el frontend

La API key de Gemini nunca se expone al navegador.
