# Informe final integrador — borrador (Unidades I–IV)

**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad
**Estudiante:** David Rafael Aguilar Solis · 22300607 · 10IDGS-G1
**Institución:** Universidad Tecnológica de Tula-Tepeji · Tecnologías de la Información
**Asignatura:** Extracción de Conocimiento en Bases de Datos · **Docente:** pendiente de confirmación
**Estado:** borrador técnico; Unidad V/dashboard, entrega y aprobación académica pendientes.

## Resumen

El proyecto emplea el dataset UCI de obesidad para documentar preparación y Data Mart, comparar modelos supervisados para Weight y NObeyesdad y explorar agrupamiento/PCA. El archivo tiene 2,111 observaciones y 17 variables; se preservaron sus valores y 24 duplicados exactos. Las cifras incluidas proceden de artefactos existentes ejecutados; no representan relaciones causales ni generalización externa.

## Problema, objetivos y método

La pregunta es qué patrones descriptivos aparecen entre hábitos, condición física y niveles de obesidad, y qué límites deben considerarse al comunicarlos. La planeación aplica CRISP-DM: comprensión del problema/datos, preparación, modelado, evaluación y comunicación. Unidad II verificó equivalencia raw/procesado y montó staging/dimensión/hechos en SQL Server. Unidad III usó particiones agrupadas y pipelines con preprocesamiento dentro de validación, con test reservado. Unidad IV ajustó K-Means/PCA sin la etiqueta en el ajuste.

## Datos y preparación

Fuente UCI, 2,111 filas × 17 columnas, cero nulos y 24 duplicados exactos. Raw SHA-256 `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`; derivado SHA-256 `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`. El derivado conserva los valores; normaliza serialización UTF-8/LF. No se afirma que se hayan aplicado correcciones de calidad o filtrado.

## Unidad III — resultados supervisados

El RF optimizado para regresión tuvo test MAE 4.7501, RMSE 8.1428 y R² 0.9005; CV agrupada RMSE 8.9627. En clasificación A, la logística optimizada logró accuracy 0.9621 y F1 macro 0.9615; en B, el RF logró accuracy 0.8697 y F1 macro 0.8666. A incluye Height/Weight y por eso tiene riesgo de circularidad. Las métricas provienen de `docs/unidad_iii/resultados/optimizacion_metricas_test.csv`; selección por CV en entrenamiento, no test.

## Unidad IV — resultados exploratorios

Se estandarizaron Age, Height, Weight, FCVC, NCP, CH2O, FAF y TUE. Máximo Silhouette en k=2–9: 0.172636 con k=9, en el límite superior de búsqueda; se interpreta como señal modesta, no como segmentación definitiva. PC1 y PC2 explicaron 41.31% acumulado. Los duplicados permanecen y tienen peso repetido; la inclusión de antropometría podría dominar distancias.

## Limitaciones, entrega y trabajo pendiente

Los registros sintéticos, el origen geográfico del dataset, duplicados y decisiones de variables limitan generalización. No se infiere causalidad, diagnóstico clínico ni efectos de hábitos. El dashboard Power BI no está implementado/verificado en este entorno; las guías requieren esa herramienta y no hay autorización para sustituirla. Integrar Unidad V, revisar el dashboard, completar capturas y narrativa, confirmar identidad docente, presentar en Classroom y obtener aceptación. El calendario oficial actualizado sitúa U4 el 18/11 a las 12:00, revisión integradora 17/11 en una guía y 18/11 en otra, correcciones el 19/11 y cierre U5 el 20/11; se conserva la discrepancia.

## Fuentes

- UCI Machine Learning Repository. *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). *Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico*. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344
