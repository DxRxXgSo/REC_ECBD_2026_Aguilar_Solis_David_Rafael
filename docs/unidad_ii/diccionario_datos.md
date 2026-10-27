# Diccionario de datos

**Fuente:** UCI Machine Learning Repository, dataset 544, DOI [10.24432/C5H31Z](https://doi.org/10.24432/C5H31Z). El CSV local contiene 2,111 registros y 17 columnas. La documentación de UCI informa que 23% se recopiló mediante una plataforma web y 77% se generó sintéticamente con Weka/SMOTE. Las distribuciones locales que siguen fueron calculadas desde el archivo fuente; rangos numéricos son mínimos y máximos observados, no límites clínicos.

| Variable | Tipo inferido del CSV | Significado según UCI/paper | Dominio observado / resumen |
|---|---|---|---|
| `Gender` | Categórica nominal | Género reportado por la persona | Female, Male |
| `Age` | Numérica continua | Edad | 14–61 años; media 24.31 |
| `Height` | Numérica continua | Estatura | 1.45–1.98 m; media 1.70 |
| `Weight` | Numérica continua | Peso | 39–173 kg; media 86.59 |
| `family_history_with_overweight` | Binaria | Antecedente familiar de sobrepeso | yes, no |
| `FAVC` | Binaria | Consumo frecuente de alimentos hipercalóricos | yes, no |
| `FCVC` | Numérica ordinal codificada | Frecuencia habitual de consumo de verduras en comidas | 1–3; media 2.42. La UCI lo describe como entero; este archivo contiene decimales por valores sintéticos/interpolados. |
| `NCP` | Numérica ordinal/cuenta aproximada | Número de comidas principales al día | 1–4; media 2.69. Hay valores fraccionarios en registros sintéticos. |
| `CAEC` | Categórica ordinal | Consumo de alimentos entre comidas | no, Sometimes, Frequently, Always |
| `SMOKE` | Binaria | Hábito de fumar | yes, no |
| `CH2O` | Numérica ordinal codificada | Consumo diario de agua | 1–3; media 2.01. La escala de frecuencia se describe en el artículo. |
| `SCC` | Binaria | Monitoreo de calorías consumidas | yes, no |
| `FAF` | Numérica ordinal codificada | Frecuencia de actividad física | 0–3; media 1.01. Hay decimales por registros sintéticos. |
| `TUE` | Numérica ordinal codificada | Tiempo de uso de dispositivos tecnológicos | 0–2; media 0.66. Hay decimales por registros sintéticos. |
| `CALC` | Categórica ordinal | Frecuencia de consumo de alcohol | no, Sometimes, Frequently, Always |
| `MTRANS` | Categórica nominal | Medio de transporte habitual | Automobile, Motorbike, Bike, Public_Transportation, Walking |
| `NObeyesdad` | Categórica ordinal objetivo | Categoría de nivel de obesidad | Insufficient_Weight, Normal_Weight, Overweight_Level_I, Overweight_Level_II, Obesity_Type_I, Obesity_Type_II, Obesity_Type_III |

## Calidad y límites

La lectura local no detectó valores faltantes y contó 24 filas exactamente duplicadas; el ETL las conserva. Los rangos observados describen esta muestra, no reglas de validación clínica. Las variables tipo escala tienen valores fraccionarios compatibles con la generación sintética y no se redondean. Las categorías de `NObeyesdad` son la etiqueta publicada; su relación con `Weight` y `Height` limita interpretaciones predictivas independientes. No se dispone de identificador que permita separar registros sintéticos individuales. La mezcla de respuestas recolectadas y registros sintéticos limita inferencias sobre población, causalidad y generalización.

## Referencias

- UCI Machine Learning Repository. (2019). *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. Dataset 544. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. *Data in Brief, 25*, 104344. https://doi.org/10.1016/j.dib.2019.104344
