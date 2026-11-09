# HMM de tres estados para un catálogo sísmico sintético

Estudio de simulación de un Modelo Oculto de Markov (HMM) categórico para analizar secuencias de magnitudes y la recuperación de estados latentes. El diseño compara los efectos de las probabilidades de transición, emisión e inicio mediante escenarios controlados.

## Alcance

Los datos son sintéticos y los parámetros son hipotéticos. Cada paso representa un evento del catálogo; no representa un intervalo fijo de tiempo. El modelo permite estudiar la generación y decodificación de secuencias bajo supuestos conocidos. No constituye un modelo validado de predicción de terremotos.

## Inicio rápido

Desde `Actividad_2`, con Python 3.13 y NumPy:

```console
py -m pip install -r requirements.txt
py main.py simular --eventos 50 --semilla 2026 --escenario base --salida resultados/mi_ejecucion
```

La salida contiene `secuencia.csv` y `resumen.json`. La carpeta debe ser nueva: una ejecución nunca sobrescribe otra. En sistemas con el comando `python`, puede utilizarse en lugar de `py`. El entorno verificado es Python 3.13.3 con NumPy 2.3.3.

Para comprobar la implementación:

```console
py -X utf8 -W error -m unittest discover -s tests -v
```

## Contenido

| Archivo | Contenido |
|---|---|
| [Planteamiento](docs/planteamiento.md) | Problema, justificación, objetivos y preguntas de investigación |
| [Marco teórico](docs/marco-teorico.md) | Distribuciones, propiedad de Markov, Forward, Viterbi, Baum-Welch y ejemplo analítico |
| [Modelo y diseño experimental](docs/modelo-y-diseno-experimental.md) | Estados, observaciones, matrices, supuestos y escenarios |
| [Parámetros base](configuracion/modelo_base.json) | Especificación estructurada de S, V, A, B y π |
| [Estado del arte](docs/estado-del-arte.md) | Revisión preliminar y referencias numeradas |
| [Matriz bibliográfica](referencias/matriz-bibliografica.md) | Comparación de antecedentes y alcance de la evidencia consultada |
| [Bibliografía BibTeX](referencias/bibliografia.bib) | Diez artículos recientes y una referencia clásica |
| [Acceso a las fuentes](referencias/acceso-a-fuentes.md) | Enlaces de lectura gratuita y distinción entre textos editoriales y copias de autor |
| [Implementación](docs/implementacion.md) | Arquitectura, algoritmos, escenarios, ejecución y validación |
| [Demostración reproducible](resultados/demostracion/README.md) | Una secuencia ejecutada, métricas y comprobación de reproducción |

## Diseño del estudio

- Tres estados ocultos y tres categorías observables de magnitud.
- Cuatro escenarios: base, mayor persistencia, emisiones menos informativas e inicio diferente.
- 200 réplicas de 500 eventos por escenario.
- Evaluación de la decodificación, composición de las secuencias y sensibilidad a los parámetros.
- Resúmenes con media, desviación estándar, mínimo, máximo e intervalos de confianza del 95%.

## Estado del desarrollo

Se dispone del planteamiento, el marco teórico, el diseño experimental, la revisión bibliográfica preliminar y el núcleo ejecutable de simulación e inferencia. Los cuatro escenarios están configurados y hay una demostración de una secuencia, repetida con archivos idénticos en el mismo entorno. El código incluye comprobaciones matemáticas y de exportación.

Siguen pendientes los experimentos de 200 réplicas por escenario, sus intervalos y comparaciones, las figuras finales y las conclusiones experimentales. Los ejemplos del marco teórico son cálculos analíticos, distintos de la demostración ejecutada. La revisión bibliográfica requiere completar lecturas críticas y verificar indexación.
