# Estado del dashboard — Unidad V

**Estado al 17/11/2026: 0/5 componentes funcionales verificados (0%).** Power BI Desktop aparece registrado como aplicación y se inició; la ventana se tituló “Sin título - Power BI Desktop”. La automatización disponible no pudo leer ni controlar su interfaz (`Accessibility state unavailable`), por lo que no se creó PBIX, páginas o capturas. Los archivos de `dashboard/powerbi/` son preparación y documentación, no componentes funcionales.

## Disponibilidad de datos (no equivale a avance funcional)

Los datos y salidas para conectar/consultar sí están disponibles: Data Mart SQL Server con 2,111 hechos y siete niveles; métricas supervisadas U3; asignaciones/tabla de perfiles U4 y resultados PCA. `dashboard/powerbi/queries/` contiene consultas M para leer estas fuentes, `model_relationships.md` define relaciones y `measures.dax` propone medidas. `guia_montaje.md` documenta páginas y verificaciones manuales. Esto es preparación de fuentes y no se contabiliza como visualizaciones del dashboard. El helper `src/powerbi_sources.py` y `tests/dashboard/` validan por código las tablas locales y su cruce 1:1 por índice de fila.

## Herramienta requerida y bloqueo

Las guías del proyecto requieren Power BI para el dashboard final. No se sustituye por Streamlit, notebook u otra herramienta sin autorización docente expresa. Se requiere instalar/usar Power BI Desktop en el equipo autorizado o conseguir autorización docente escrita para alternativa compatible.

## Backlog para llegar a revisión

1. Abrir Power BI Desktop, importar las consultas M desde `dashboard/powerbi/queries/` y actualizar la ruta de proyecto si es necesario.
2. Configurar relaciones y medidas según `model_relationships.md` y `measures.dax`; comprobar 2,111 observaciones, siete categorías y los conteos de U4.
3. Montar las cuatro páginas usando `guia_montaje.md` y aplicar `tema_ecbd.json`.
4. Validar comparaciones U3 A/B, advertencia de circularidad, matriz base correctamente rotulada, PCA y límites del clustering.
5. Guardar el PBIX en `dashboard/`, revisar visualmente filtros e interacciones y guardar capturas/exportación verificables en `dashboard/evidencias/`.

La sensibilidad adicional in-memory documentada en `dashboard/evidencias/sensibilidad_kmeans.json` encontró Silhouette más alta para k=10 y k=11 que para k=9 en el rango ampliado 2–12; k=9 permanece elección exploratoria del rango original, no óptimo global demostrado. La variación por semillas también aconseja cautela.

El objetivo conservador para la revisión integradora del 17/11 es al menos 70% funcional; con el estado actual ese criterio **no está cumplido**. Entrega/aceptación docente y Classroom permanecen no verificadas. Véase `dashboard/powerbi/guia_montaje.md` para el montaje manual; hace falta interacción directa en Power BI Desktop para importar las consultas, crear las relaciones/medidas, construir las páginas, refrescar, revisar y guardar `dashboard/ECBD_Integrador_2026.pbix` y capturas reales.
