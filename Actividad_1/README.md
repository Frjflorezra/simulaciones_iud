# Yahtzee y simulación Montecarlo

Simulador de Yahtzee clásico para dos jugadores automáticos, con decisiones basadas en el método de Montecarlo. Permite ejecutar partidas, consultar su historial y estudiar cómo cambian las estimaciones al aumentar las muestras o modificar las probabilidades de los dados.

El [cuaderno explicativo](Montecarlo_Yahtzee.ipynb) reúne el funcionamiento del programa, los experimentos y sus resultados.

## Funcionalidades

- Partidas con dos jugadores que alternan durante 13 rondas.
- Cinco dados de seis caras y hasta tres lanzamientos por turno.
- Comparación de las 32 alternativas de conservación de dados.
- Puntuación de las 13 categorías, bono superior, bonos por Yahtzee adicional y regla Joker.
- Experimentos de convergencia, dados cargados y decisión de conservar un trío.
- Exportación de datos JSON y CSV y gráficos SVG.

Los jugadores toman sus decisiones automáticamente. La partida utiliza dados uniformes; los dados cargados se estudian por separado.

## Requisitos

- Python 3.10 o superior.
- Jupyter Notebook o soporte para notebooks en VS Code, únicamente para ejecutar el cuaderno.

El juego por consola y los experimentos utilizan la biblioteca estándar de Python y no requieren dependencias adicionales.

## Inicio rápido

Descarga o clona el repositorio y abre una terminal en la carpeta que contiene `main.py`.

### Ejecutar una partida

```console
python main.py jugar --semilla 42 --simulaciones 100
```

El comando muestra el marcador, las bonificaciones, el ganador y el número de dados individuales lanzados. Guarda el historial en `resultados/partida_manual.json`.

Para ver los lanzamientos y las categorías anotadas:

```console
python main.py jugar --semilla 42 --simulaciones 100 --detalle
```

En Windows puede utilizarse `py` en lugar de `python`.

### Probar los experimentos

Esta ejecución usa 1 000 muestras por experimento y omite la comparación de presupuestos de la IA:

```console
python main.py experimentos --n 1000 --semilla 42 --simulaciones 100 --sin-comparar-presupuestos --salida resultados_prueba
```

Para ejecutar el análisis con 100 000 muestras e incluir la comparación de 10, 1 000 y 100 000 simulaciones por máscara:

```console
python main.py experimentos --n 100000 --semilla 42 --simulaciones 100 --salida resultados_nuevos
```

La comparación de presupuestos es la parte más costosa. El tiempo depende del equipo.

La carpeta indicada con `--salida` reúne los archivos de esa ejecución. Si contiene archivos con los mismos nombres, estos se sustituyen. Las carpetas alternativas permiten conservar los datos de referencia de `resultados`, que es la carpeta que lee el cuaderno.

## Ejecutar el cuaderno

1. Conserva la estructura del repositorio, incluidos los módulos Python y la carpeta `resultados`.
2. Abre `Montecarlo_Yahtzee.ipynb` en Jupyter Notebook o VS Code.
3. Ejecuta las celdas en orden desde la raíz del proyecto.

Para utilizar Jupyter localmente:

```console
python -m pip install notebook
python -m notebook
```

El cuaderno calcula una partida al ejecutar su celda correspondiente. En la celda de análisis, `REGENERAR = False` carga los experimentos guardados; `True` vuelve a ejecutarlos y actualiza `resultados`.

Si se cambian los parámetros y se desea actualizar el análisis, debe activarse la regeneración. Con `REGENERAR = False`, los resultados estadísticos corresponden a la configuración registrada en el archivo guardado.

## Parámetros

| Parámetro | Valor predeterminado | Función |
|---|---:|---|
| `accion` | Obligatorio | `jugar` inicia una partida; `experimentos` ejecuta los estudios y una partida de referencia. |
| `--semilla` | 42 | Inicializa las secuencias pseudoaleatorias para reproducir una ejecución. |
| `--simulaciones` | 100 | Simulaciones por máscara para las decisiones de la partida. |
| `--n` | 100000 | Muestras por experimento; se utiliza con `experimentos`. |
| `--salida` | `resultados` | Carpeta de los archivos generados. |
| `--detalle` | Desactivado | Muestra el desarrollo de los turnos con la acción `jugar`. |
| `--sin-comparar-presupuestos` | Desactivado | Omite la comparación adicional de 10, 1 000 y 100 000 simulaciones por máscara. |

El presupuesto `--simulaciones` de la partida es distinto de `--n`, que controla las repeticiones estadísticas. La comparación adicional utiliza sus tres presupuestos fijos.

## Cómo decide qué dados conservar

Cada dado puede conservarse o relanzarse. Para cinco dados existen 2⁵ = 32 máscaras posibles. Por ejemplo:

```text
Dados:    [6,    6,    6,     1,     2]
Máscara:  [True, True, True, False, False]
```

Esta alternativa conserva los tres seises y relanza los dos dados restantes.

El algoritmo:

1. Genera las máscaras de conservación.
2. Simula la siguiente tirada para cada alternativa con dados libres.
3. Calcula el mejor incremento de puntuación permitido por las categorías disponibles y las bonificaciones aplicables.
4. Promedia los puntajes y elige la máscara con mayor valor esperado estimado. Conservar todos los dados se valora directamente.
5. Realiza el lanzamiento elegido y vuelve a evaluar si quedan tiradas. Al plantarse o agotar los lanzamientos, anota en una casilla legal.

La política considera una tirada futura y el puntaje inmediato. No optimiza todas las decisiones de la partida ni el valor de reservar una categoría para turnos posteriores.

Los escenarios hipotéticos y los dados reales utilizan generadores separados. El histograma registra únicamente las caras nuevas de los dados que se lanzan.

## Experimentos

### Convergencia de la media

Se conservan dos treses y se lanzan tres dados. En cada muestra se toma el mejor puntaje entre Treses, Trío, Full y Libre, manteniendo fijas las condiciones del experimento.

La referencia exacta se calcula enumerando los 6³ = 216 resultados posibles: **17,30092593 puntos**.

| Muestras | Media Montecarlo | Error absoluto |
|---:|---:|---:|
| 10 | 17,50000 | 0,19907 |
| 1 000 | 17,27200 | 0,02893 |
| 100 000 | 17,29353 | 0,00740 |

La Ley de los Grandes Números justifica la convergencia bajo los supuestos de independencia, igual distribución y esperanza finita. Los resultados ilustran esa convergencia; el error puede aumentar entre dos tamaños de muestra.

### Dados uniformes y cargados

Se comparan manos independientes de cinco dados:

| Distribución | Probabilidad de cada cara del 1 al 5 | Probabilidad del 6 |
|---|---:|---:|
| Uniforme | 1/6 | 1/6 |
| Cargada | 0,14 | 0,30 |

Para una sola tirada, la probabilidad de Yahtzee es la suma de las quintas potencias de las probabilidades de cada cara.

| Distribución | Probabilidad teórica de Yahtzee | Yahtzees observados en 100 000 manos |
|---|---:|---:|
| Uniforme | 0,07716 % | 72 |
| Cargada | 0,26989 % | 260 |

Estos valores corresponden a una tirada independiente, no a un turno completo con varias tiradas y selección de dados. Se incluyen intervalos de Wilson al 95 % para expresar incertidumbre de muestreo.

### Conservar un trío o arriesgar

Se estudia la mano `[6, 6, 6, 1, 2]`, con una tirada restante y únicamente Libre disponible. Todas las demás casillas están en cero, incluida Yahtzee, por lo que no hay bonos.

- Conservar produce 21 puntos.
- Relanzar los dos dados libres tiene esperanza de 25 puntos con dados uniformes y de 25,8 con los cargados.
- Completar dos seises tiene probabilidad de 1/36, aproximadamente 2,78 %, con dados uniformes y de 9 % con los cargados.

La simulación uniforme obtuvo una media de 24,98487 puntos. Bajo el criterio de maximizar puntos esperados, conviene relanzar en este estado, aunque sigue existiendo la posibilidad de obtener menos de 21 puntos.

## Organización

| Archivo o carpeta | Responsabilidad |
|---|---|
| [yahtzee.py](yahtzee.py) | Dados, reglas, puntuación, estados, máscaras, decisiones y partida. |
| [experimentos.py](experimentos.py) | Referencias exactas, experimentos, intervalos y exportaciones. |
| [main.py](main.py) | Interfaz de consola y lectura de parámetros. |
| [Montecarlo_Yahtzee.ipynb](Montecarlo_Yahtzee.ipynb) | Explicación y presentación de resultados por celdas. |
| [docs](docs/) | Informe técnico y detalle de las modificaciones. |
| [resultados](resultados/) | Datos, gráficos y registros de la ejecución de referencia. |
| [referencias](referencias/) | Materiales originales utilizados como punto de partida. |

## Archivos de resultados

Los experimentos generan:

- `resultados.json`: configuración, convergencia, distribución de caras, probabilidades y análisis de riesgo.
- `partida.json`: marcador e historial de los 26 turnos de la partida de referencia.
- Archivos CSV para consultar las tablas en una hoja de cálculo.
- Gráficos SVG de convergencia, error y distribución de caras.

La acción `jugar` guarda su historial en `partida_manual.json`. Los archivos `diagnostico_base.json` y `ejecucion_base.txt` documentan el análisis del original y no se regeneran con estos comandos.

Los resultados pueden cambiar al utilizar otras semillas, presupuestos o versiones del entorno. Una semilla fija facilita la reproducción en las mismas condiciones.

## Documentación y procedencia

- [Informe técnico](docs/Informe_Montecarlo.docx): metodología, resultados, conclusiones y referencias.
- [Modificaciones y mejoras](docs/MODIFICACIONES.md): comparación con la base, organizada en USA, MODIFICA y CREA.

El proyecto adapta el cuaderno `simulacion_01.ipynb`, suministrado como material docente. Conserva conceptos y funciones de la implementación inicial y documenta sus correcciones y ampliaciones. Los materiales originales están en `referencias`; su inclusión no implica una atribución de autoría ni una licencia nueva.
