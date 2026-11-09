# Implementación y validación computacional

## Entorno

| Componente | Versión utilizada |
|---|---|
| Python | 3.13.3 |
| NumPy | 2.3.3 |
| Sistema | Windows, AMD64 |
| Generador pseudoaleatorio | PCG64, mediante Generator explícito |
| Aritmética probabilística | float64; inferencia en logaritmos |

La única dependencia externa del núcleo es NumPy, fijada en `requirements.txt`. Las pruebas utilizan `unittest`, incluido en Python. No se utiliza una implementación externa de HMM ni se entrenan parámetros.

## Organización

| Archivo | Función |
|---|---|
| [hmm.py](../src/hmm.py) | Clase HMM, validación, generación de secuencias, Forward, Viterbi y decodificación aislada |
| [escenarios.py](../src/escenarios.py) | Lectura del JSON y construcción de cuatro modelos controlados |
| [ejecucion.py](../src/ejecucion.py) | Ejecución de una secuencia, métricas y exportación |
| [main.py](../main.py) | Argumentos de consola y presentación de resultados |
| [test_hmm.py](../tests/test_hmm.py) | Oráculos de probabilidad, estabilidad y validación del modelo |
| [test_ejecucion.py](../tests/test_ejecucion.py) | Escenarios, archivos de salida, repetición y protección de ejecuciones |

## Correspondencia con el marco teórico

### Generación

Para cada secuencia se generan T pares de uniformes en [0,1). La primera componente de cada par determina el estado y la segunda su emisión mediante la CDF categórica. En t=1 se utiliza π; para t>1, la fila de A del estado anterior. La emisión siempre se extrae desde el estado del evento actual.

```text
generar T pares de uniformes con el generador recibido
para cada evento t:
    seleccionar Z_t usando π si t=1, o A[Z_(t−1)] si t>1
    seleccionar O_t usando B[Z_t]
devolver estados y observaciones
```

El consumo de dos uniformes por evento no depende del estado alcanzado. No se reinicia una semilla global dentro del bucle. La interfaz recibe un Generator, por lo que el diseño posterior de réplicas podrá asignar flujos separados sin cambiar el núcleo.

### Evaluación y decodificación

Forward implementa la suma de trayectorias en logaritmos mediante `logaddexp.reduce`. Viterbi utiliza máximos en logaritmos y conserva los predecesores para reconstruir la trayectoria. Ambos requieren O(TN²) operaciones para N estados. Forward conserva un vector de N valores; Viterbi conserva además TN predecesores.

El decodificador aislado calcula q_t=πA^(t−1) y selecciona argmax_i q_t(i)B_i,k_t. Se evalúa en logaritmos y no recibe estados verdaderos ni observaciones de otros eventos. Las decisiones aisladas no tienen por qué formar una trayectoria conjunta posible.

En Viterbi, los empates se resuelven por el primer índice en cada máximo. El puntaje devuelto es log P(trayectoria, observaciones), mientras que Forward devuelve log P(observaciones). Su diferencia es el log-posterior de la trayectoria seleccionada.

### Escenarios

La clase HMM acepta dimensiones generales. El constructor de escenarios de esta aplicación exige tres estados y tres símbolos, según el diseño sísmico.

| Identificador de consola | Cambio respecto del base |
|---|---|
| `base` | Ninguno |
| `mayor_persistencia` | A'=0.5A+0.5I |
| `emisiones_menos_informativas` | B'=0.7B+0.3U, con U_ik=1/3 |
| `inicio_diferente` | π'=[0.05,0.15,0.80] |

Cada escenario es un modelo separado. Las matrices del caso base no se modifican para producir los otros escenarios.

## Validación de entradas y casos límite

π, A y B deben ser finitos y estar en [0,1], tener dimensiones compatibles y sumar uno por fila, con tolerancia absoluta 1e-12. Las matrices se copian y exponen como arreglos de solo lectura. No se normalizan silenciosamente entradas incorrectas.

Las observaciones deben ser una secuencia unidimensional de índices enteros válidos. Se rechazan decimales, textos y booleanos, incluso cuando se mezclan con enteros. El muestreo requiere un número positivo de eventos y un Generator explícito. La semilla de consola debe ser un entero no negativo.

La secuencia vacía tiene log-probabilidad cero y trayectoria vacía en los métodos de inferencia. Las secuencias imposibles tienen log-probabilidad −∞ en Forward; Viterbi rechaza una trayectoria sin soporte. La regla aislada rechaza una observación de probabilidad marginal nula. La consola no genera secuencias de longitud cero.

## Ejecución

Desde la carpeta `Actividad_2`, instalar las dependencias en el entorno de Python destinado al proyecto:

```console
py -m pip install -r requirements.txt
```

Generar una secuencia:

```console
py main.py simular --eventos 50 --semilla 2026 --escenario base --salida resultados/mi_ejecucion
```

Para otro escenario:

```console
py main.py simular --eventos 500 --semilla 2026 --escenario mayor_persistencia --salida resultados/mi_persistencia
```

Las carpetas indicadas deben ser nuevas. Si ya existen, el programa termina con error y conserva su contenido. Sin `--salida`, se utiliza `resultados/ejecucion`; la demostración distribuida se encuentra en una carpeta distinta. La ruta de configuración predeterminada se resuelve respecto de `main.py`, mientras que la salida relativa se resuelve respecto de la carpeta de ejecución.

Consultar opciones y ejecutar pruebas:

```console
py main.py simular --help
py -X utf8 -W error -m unittest discover -s tests -v
```

En un entorno donde el comando sea `python`, puede sustituirse `py` por `python`. La versión utilizada para las evidencias de este bloque es la de la tabla de entorno.

## Archivos producidos

Cada ejecución produce:

- `secuencia.csv`: índice de evento, estado generador, observación, ambas decodificaciones y etiquetas legibles. Codificación UTF-8.
- `resumen.json`: semilla, generador, método de muestreo, versiones, parámetros activos y métricas. No contiene fechas variables ni rutas personales.

Las métricas incluyen exactitud de ambos decodificadores, log-verosimilitud total y por evento, puntaje conjunto de Viterbi, log-posterior de su trayectoria, composición de estados/observaciones y frecuencia de cambios de estado. Para un solo evento esta última es `null`, porque no hay transiciones disponibles.

Se registra el modelo activo, no únicamente el nombre del escenario. Las etiquetas de los estados generadores se emplean para evaluar y exportar después de inferir, sin alimentar a los decodificadores.

## Comprobaciones realizadas

La suite compara todas las observaciones de longitud 1–4 de un modelo asimétrico de dos estados y tres símbolos con una enumeración exhaustiva independiente de trayectorias. También reproduce el ejemplo analítico de dos magnitudes altas del marco teórico.

En la comprobación del 9 de noviembre de 2026 pasaron las 21 pruebas, tratando las advertencias como errores. Además, se ejecutó cada uno de los cuatro escenarios con una secuencia de 500 eventos como comprobación funcional de consola y exportación. Estas cuatro ejecuciones individuales no equivalen al diseño estadístico de 200 réplicas por escenario.

Se comprueban secuencias largas con emisiones de probabilidad 1e-250, ceros exactos, trayectorias imposibles, empates, entradas inválidas, emisión inicial, frecuencias categóricas, flujo aleatorio local, factores de cada escenario y coherencia CSV/JSON. Las pruebas de consola se ejecutan también desde otra carpeta y verifican que no se sobrescriban resultados anteriores.

La [demostración conservada](../resultados/demostracion/README.md) corresponde a una secuencia real de 50 eventos, repetida en el mismo entorno con CSV y JSON idénticos byte a byte. Es evidencia de ejecución del núcleo, no el análisis de 200 réplicas por escenario.

## Alcance de la reproducibilidad

Se utilizan explícitamente PCG64 y una semilla registrada. La reproducción exacta requiere conservar también versiones y condiciones de ejecución; no se presupone identidad universal entre versiones, compilaciones o plataformas distintas. Véase la [política de compatibilidad aleatoria de NumPy](https://numpy.org/doc/2.3/reference/random/compatibility.html).

Siguen pendientes el ejecutor de réplicas independientes, los intervalos de confianza, las comparaciones estadísticas, las figuras finales y las respuestas experimentales a P1–P3. Baum-Welch permanece como fundamento teórico y no forma parte del código de inferencia con parámetros conocidos.
