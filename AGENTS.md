# Reglas operativas del proyecto

- Antes de trabajar, lee `docs/sdd/00_reglas_globales.md` y sólo la especificación activa indicada por el usuario.
- Implementa una unidad a la vez. No inicies una unidad posterior sin instrucción expresa.
- Trata la especificación activa como fuente de verdad. Divide el trabajo en tareas pequeñas y verifica cada criterio de aceptación con evidencia.
- Conserva el dataset original en `data/raw`; nunca lo edites, reemplaces ni sobrescribas. Todo derivado va exclusivamente en `data/processed`.
- No inventes resultados, métricas, fuentes, fechas ni datos académicos. Registra bloqueos y discrepancias.
- No sobrescribas ni elimines trabajo existente. Revisa `git status` y diffs antes de editar.
- No instales dependencias innecesarias. Prioriza las herramientas aprobadas en las reglas globales; solicita autorización antes de sustituir una herramienta requerida por la guía.
- Ejecuta pruebas reales y registra comandos, entorno, resultados y rutas de evidencia. No declares un criterio cumplido sólo porque esté planeado.
- No hagas commits, push, pull, merge ni cambies historial sin autorización explícita.
- Separa planeación, implementación, pruebas y evidencias. Mantén los cambios acotados a la tarea actual.
