# SDD — Unidad V: Dashboard e integración final

**Alcance:** construir y validar el proyecto requerido en Power BI Desktop, integrar resultados verificados de U2–U4 y cerrar el informe/storytelling. Esta especificación no autoriza cambiar datos, modelos ni resultados anteriores.

## Restricciones

- Usar Power BI Desktop; no sustituir la herramienta requerida sin autorización docente.
- Mantener intactos `data/raw`, el notebook inicial con cambio local, SQL, modelos y evidencias U2–U4.
- Fuentes previstas: CSV procesado U2, dimensión SQL de sólo lectura, métricas U3, asignaciones/perfiles U4 y varianza PCA.
- No declarar PBIX/PBIP funcional por su mera existencia. No publicar valores hasta refrescar y contrastar fuentes.
- En conexión local, limitar la confianza de certificado al servidor de desarrollo y conservar cifrado; no guardar credenciales.
- Registrar entregas y aprobación académica sólo con evidencia independiente.

## Criterios de aceptación

| Criterio | Evidencia requerida | Estado al 17/11/2026 |
|---|---|---|
| AC-V01 Proyecto Power BI válido y abierto en Desktop | PBIP abre y validación PBIR/TMDL documentada | PASS con límite: 0 errores; 1 aviso de esquema visual 2.14 no descargable por el validador. Desktop guardó PBIP y se restauraron los campos `$schema` que eliminó. |
| AC-V02 Cinco consultas actualizan sin error | Refresh real en Desktop, sin credenciales persistidas | PASS: se cargaron FactDashboard (2,111), DimObesityLevel (7), ModelMetrics (5), ClusterProfile (9) y PcaVariance (2). Autenticación Windows. Confianza SSL limitada al proceso `localhost\SQLEXPRESS`; ámbito User vacío. |
| AC-V03 Integridad de datos integrada | 2,111 observaciones, 7 clases, 2,111 índices/asignaciones 1:1, duplicados preservados | PASS en fuentes y contrato M: 2,111 filas, 2,111 índices U4 únicos, asignaciones completas; 24 duplicados preservados. No se cambió el CSV raw. |
| AC-V04 Modelo semántico | Relaciones activas y correctas, tipos y medidas probadas en Desktop | Parcial: la relación DimObesityLevel→FactDashboard filtró `Normal_Weight` a 287 observaciones y se restauró 2,111; la relación ClusterProfile→FactDashboard no se comprobó por interacción. |
| AC-V05 Cuatro páginas funcionales | Datos reales visibles, títulos, visuales, filtros e interacciones probados | Parcial: las cuatro páginas tienen datos y capturas; se probó el filtro de categoría. Falta integrar en página 2 la imagen de matrices base y revisar interacción de relación de clusters. |
| AC-V06 Integración fiel de U3/U4 | Métricas, perfiles, PCA y advertencias coinciden con fuentes | PASS para valores mostrados: regresión RF y filas por escenario/modelo coinciden con CSV U3; 9 perfiles, 9 clusters y PC1/PC2 coinciden con U4. Se ajustó el gráfico para no promediar modelos distintos. |
| AC-V07 Calidad y evidencia | Tests, integridad raw, capturas finales, proyecto reabierto y documentación coherente | PASS técnico: PBIP reabierto y refrescado; cuatro capturas revisadas; suites 3/12/8/2 PASS; SHA raw antes/después coincide; `git diff --check` revisado. La aprobación académica queda aparte. |
| AC-V08 Informe final y defensa | Informe exportado y revisado con resultados del dashboard efectivamente verificados | Parcial: PDF generado y seis páginas revisadas visualmente. Classroom, defensa y aceptación docente no verificadas. |

## Arquitectura y páginas

`FactDashboard` usa el CSV U2 enriquecido por unión 1:1 con asignaciones U4 mediante `row_index`; las filas idénticas se conservan. `DimObesityLevel` es la dimensión de SQL. `ModelMetrics`, `ClusterProfile` y `PcaVariance` son tablas independientes salvo relación de perfil-cluster a hechos. Página 1: panorama; página 2: modelos A/B y regresión, con circularidad A; página 3: clusters/PCA, con k=9 exploratorio y sensibilidad; página 4: hallazgos, recomendaciones y limitaciones. No relacionar métricas ni PCA artificialmente.

## Verificación y evidencias

Contrastar fuentes/filas, categorías, unicidad de `row_index`, relaciones, DAX y métricas; refrescar, probar segmentadores, navegar todas las páginas, revisar visualmente, guardar y reabrir el proyecto. Guardar evidencia bajo `dashboard/evidencias/` y actualizar sólo estados observados. Hash raw de referencia: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`.

## Estado inicial registrado

`dashboard/ECBD_Integrador_2026/` es el PBIP original actualizado y reabierto en Desktop. Se verificaron cinco componentes de alto nivel (refresco de fuentes, página 1, página 2, página 3 y página 4), cuatro páginas con datos y filtro de obesidad; queda pendiente incrustar la matriz de confusión base en la página 2 y probar la relación de perfiles. La interfaz sólo ofreció guardar PBIP y exportar plantilla/PDF, por lo que no se afirma que exista PBIX. El hash raw antes/después fue idéntico. Evidencia: `dashboard/evidencias/verificacion_powerbi_2026-11-16.json` y capturas finales en `dashboard/evidencias/final_powerbi_2026-11-16_validado/`. Classroom y aceptación docente no se infieren.
