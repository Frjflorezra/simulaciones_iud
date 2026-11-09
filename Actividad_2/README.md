# HMM de tres estados para un catálogo sísmico sintético

Estudio de simulación de un Modelo Oculto de Markov (HMM) categórico para analizar secuencias de magnitudes y la recuperación de estados latentes. El diseño compara los efectos de las probabilidades de transición, emisión e inicio mediante escenarios controlados.

## Alcance

Los datos son sintéticos y los parámetros son hipotéticos. Cada paso representa un evento del catálogo; no representa un intervalo fijo de tiempo. El modelo permite estudiar la generación y decodificación de secuencias bajo supuestos conocidos. No constituye un modelo validado de predicción de terremotos.

## Contenido

| Archivo | Contenido |
|---|---|
| [Planteamiento](docs/planteamiento.md) | Problema, justificación, objetivos y preguntas de investigación |
| [Modelo y diseño experimental](docs/modelo-y-diseno-experimental.md) | Estados, observaciones, matrices, supuestos y escenarios |
| [Parámetros base](configuracion/modelo_base.json) | Especificación estructurada de S, V, A, B y π |

## Diseño del estudio

- Tres estados ocultos y tres categorías observables de magnitud.
- Cuatro escenarios: base, mayor persistencia, emisiones menos informativas e inicio diferente.
- 200 réplicas de 500 eventos por escenario.
- Evaluación de la decodificación, composición de las secuencias y sensibilidad a los parámetros.
- Resúmenes con media, desviación estándar, mínimo, máximo e intervalos de confianza del 95%.

## Estado del desarrollo

Se dispone del planteamiento, la especificación del modelo y el diseño experimental. La implementación, la revisión bibliográfica, los experimentos y el análisis de resultados aún no se han realizado. Las instrucciones de ejecución y las versiones de las dependencias se incorporarán con la implementación verificada.
