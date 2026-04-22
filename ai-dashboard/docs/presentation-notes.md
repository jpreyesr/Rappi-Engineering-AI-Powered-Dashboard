# Notas De Presentación

## Qué AI Se Usó

La app usa Gemini API desde el backend con function calling. El modelo no consulta DuckDB directamente ni recibe archivos CSV completos; llama funciones controladas que reutilizan la misma capa analítica del dashboard.

## Por Qué Así

El objetivo no es tener un chat decorativo, sino un asistente grounded en datos reales. Tool calling permite que las cifras salgan de DuckDB y que el modelo se limite a interpretar y explicar resultados devueltos por herramientas del backend.

La API key vive solo en backend porque el navegador no debe exponer secretos ni tener acceso directo a Gemini. El frontend solo envía mensaje, filtros e historial corto a FastAPI.

## Decisiones Técnicas

- FastAPI: contratos claros, Pydantic, endpoints simples y buena ergonomía para una demo local.
- DuckDB: motor analítico local, rápido para CSVs y series temporales, sin levantar infraestructura adicional.
- React/Vite: frontend ágil para construir una UI de demo con TypeScript, Tailwind y Recharts.
- Monolito modular: suficiente para una app local; evita microservicios y mantiene límites claros por carpetas.
- Function calling: reduce alucinaciones porque el modelo debe usar funciones analíticas reales.

## Semántica Del Dataset

Los CSVs son exportaciones wide de monitoreo sintético. Cada archivo representa una ventana de observación y trae una fila con muchas columnas de timestamps. La ingesta transpone esas columnas a filas `(timestamp, metric, visible_stores, source_file)`.

La métrica `synthetic_monitoring_visible_stores` se presenta como conteo de tiendas visibles. La UI evita afirmar que siempre es instantánea o acumulada porque algunas ventanas parecen ramp-up y otras tienen valores en millones.

No existe `store_id`, por lo que rankings y tablas se defienden como análisis por ventana de monitoreo, no por tienda individual.

## Cómo Defender La Solución

- "El backend es la fuente de verdad para datos y métricas."
- "El frontend no calcula KPIs oficiales; solo filtra, formatea y renderiza."
- "Dashboard y chat comparten `AnalyticsService`, por eso no se contradicen."
- "La escala logarítmica es una decisión visual para comparar ventanas de magnitudes distintas."
- "Delta, anomalías y heatmap existen porque disponibilidad es una serie temporal operativa; no basta con KPIs agregados."
- "Gemini no tiene acceso libre a SQL ni a archivos; usa tools controladas."
