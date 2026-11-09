# Matriz bibliográfica preliminar

Fecha de corte: 9 de noviembre de 2026. Ventana reciente: 9 de noviembre de 2021 a 9 de noviembre de 2026. La selección de trabajo contiene diez artículos recientes y un clásico adicional, todos con una vía de lectura completa gratuita comprobada. La [verificación de acceso](acceso-a-fuentes.md) distingue texto editorial y copias de autor.

Los números corresponden a las referencias del [estado del arte](../docs/estado-del-arte.md); las claves identifican las entradas de `bibliografia.bib`. Comprobar disponibilidad no equivale a haber leído críticamente todas las páginas. La indexación y el cuartil de las revistas siguen pendientes de comprobación en Scopus o Web of Science.

## Comparación

| Ref. y clave | Datos y método | Relación y límites respecto del estudio | Evidencia consultada |
|---|---|---|---|
| [1] `wang2024paleosismicos` | Registros paleosísmicos de 93 segmentos; comparación de cinco procesos de renovación y promedio bayesiano | Antecedente de incertidumbre y evaluación; no es un HMM categórico. El uso de MCMC no convierte el modelo de recurrencia en HMM | HTML editorial y PDF de 12 páginas disponibles; resumen, introducción y métodos consultados |
| [2] `willis2025microseismicidad` | Microseismicidad inducida en Decatur; extracción espectral con NMF y HMM, seguida de agrupamiento y análisis focal | Antecedente de estados latentes a partir de señales; las observaciones no son categorías de magnitud de un catálogo | HTML editorial completo disponible; resumen, §4 y declaración de disponibilidad consultados |
| [3] `georgakopoulou2024phmm` | Conteos en diez zonas de Centro y Sudamérica; PHMM y selección AIC/BIC | Completitud y agregación de datos reales; las intensidades no se trasladan a nuestra B categórica | HTML editorial completo comprobado; §§2, 3.1 y 4 consultadas |
| [4] `rizal2023segmentos` | Frecuencias anuales en Sumatra; PHMM y Copula-HMM | Tres estados de tasa no equivalen a tres categorías de magnitud por evento | PDF editorial de 16 páginas disponible; primera página, formulación y conclusiones consultadas |
| [5] `rizal2024magnitud` | Máximos anuales de magnitud; GMM independiente frente a GHMM, con BIC | Comparación pertinente de dependencia secuencial; un máximo anual no equivale a un evento individual | HTML y PDF editorial de 10 páginas disponibles; resumen, formulación y conclusiones consultados |
| [6] `neely2023ltfm` | Grandes terremotos y memoria de falla; LTFM con proceso oculto | Contraste entre estados con interpretación física y etiquetas didácticas | Manuscrito de autor completo de 28 páginas disponible; planteamiento y descripción del modelo consultados. No se equipara con la versión editorial |
| [7] `kravchinsky2022cadenas` | Secuencias sintéticas de autómatas celulares y cadenas absorbentes | Simulación markoviana y comparación de estadísticas; no es un HMM de emisiones | HTML editorial completo disponible como Free Access; resumen y discusión consultados |
| [8] `barani2025memoria` | Catálogos sintéticos con restricciones energéticas | Contraste físico; no respalda las probabilidades hipotéticas del experimento | HTML y PDF editorial de 11 páginas disponibles; descripción del simulador y disponibilidad de código consultadas |
| [9] `kohler2026generalizacion` | Catálogo regional; modelos neuronales, Markov e híbridos con separación temporal | Generalización si se incorpora entrenamiento en una extensión; no es evidencia de nuestro desempeño | HTML y PDF editorial de 22 páginas disponibles; resumen, introducción y §5 consultados |
| [10] `shahzadi2026incompletitud` | Registros incompletos y variantes de HMM; aplicación empírica a erupciones | Antecedente metodológico de faltantes, no evidencia sísmica directa | HTML y PDF editorial de 29 páginas disponibles; resumen e introducción consultados |
| [11] `rabiner1989tutorial` | Referencia clásica de HMM | Base del marco teórico; no se cuenta como trabajo reciente | Copia de autor de 30 páginas disponible en UCSB y registro bibliográfico. Lectura crítica del tutorial y erratas pendiente |

## Criterios de interpretación

1. Una tasa de ocurrencia, un tiempo entre eventos, una representación espectral y una categoría de magnitud son observaciones diferentes.
2. La cantidad de estados elegida para un conjunto de datos no se transfiere automáticamente a otro. Tres estados es una decisión del experimento sintético.
3. El aprendizaje con datos reales y la decodificación con parámetros generadores conocidos responden a preguntas distintas.
4. Las síntesis se limitan a los pasajes consultados. No se transfieren matrices, cifras de desempeño, validez geofísica ni afirmaciones de novedad.
5. El acceso gratuito permite lectura; por sí solo no acredita calidad metodológica, indexación ni permiso de redistribución.

## Fechas y versiones

Para [6], la referencia publicada es de 2023 y la publicación anticipada de 2022; el enlace gratuito corresponde a un manuscrito de autor. Para [10], la ficha editorial distingue publicación en línea en 2025 y edición en 2026. Se registra una sola entrada por artículo.

El catálogo y los programas de [8] se anuncian en [Zenodo](https://doi.org/10.5281/zenodo.15850311). Se identificó su disponibilidad, pero no se descargaron ni ejecutaron para este estudio.
