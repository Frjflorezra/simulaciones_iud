# Evaluación Experimental del Algoritmo de Viterbi frente a Clasificadores Estáticos en la Inferencia de Regímenes Sísmicos Latentes: Un Estudio Metodológico de Simulación Computacional

**Autor:** Francisco Javier Florez Ramirez  
**Docente asesor:** Dr. Julián Andrés Loaiza López  
Curso de Simulación · Ingeniería de Software y Datos · IU Digital de Antioquia.

El estudio compara la decodificación de estados ocultos con parámetros conocidos. Los datos y estados son hipotéticos; los resultados no constituyen una validación ni un pronóstico sismológico.

## Experimento reproducible

Se utilizan las matrices originales de [caso-sismico.md](materiales/caso-sismico.md). La implementación común está en `src/hmm_model.py`, y la ejecución y exportación en `src/experimento.py`.

- Caso base: Baja, Baja, Media, Media y Alta.
- Monte Carlo: 100 secuencias de 50 eventos.
- Generador: instancia local de `numpy.random.RandomState(42)` (MT19937), inicializada una sola vez.
- Muestreo: estado y emisión en cada evento, antes de avanzar al siguiente.
- Desempate: primer índice; ante magnitud media se selecciona s2 en ambas fases.
- Desviación estándar muestral: `ddof=1`.
- IC95 % aproximado de la media: media ± 1.96 · s / √100.

No se informa un valor p ni se interpreta la separación de intervalos individuales como una prueba pareada.

## Ejecución

Entorno verificado: Python 3.13.3, NumPy 2.3.3 y Matplotlib 3.10.8.

```bash
pip install -r requirements.txt
python run_viterbi_caso.py
python scripts/sincronizar_articulo.py
python generar_figuras.py
python -m unittest discover -s tests -v
```

En Windows puede utilizarse `py -3 -X utf8` en lugar de `python`.

La ejecución exporta `resultados/experimento.json`, `resultados/monte_carlo.csv` y `resultados/secuencias.csv`. Para elegir otra carpeta:

```bash
python run_viterbi_caso.py --salida otra_carpeta
```

La sincronización actualiza las tablas y cifras de ambos manuscritos desde el experimento. No modifica las referencias ni las bitácoras históricas. Las figuras se generan después con los mismos parámetros y métodos.

## Resultados

| Método | Secuencia del caso base | ln P | Exactitud media Monte Carlo | IC95 % |
| --- | --- | ---: | ---: | --- |
| Viterbi | (s1,s1,s2,s3,s3) | -7.2538 | 72.62 % | [70.48 %,74.76 %] |
| Máxima emisión | (s1,s1,s2,s2,s3) | -7.4361 | 69.72 % | [68.07 %,71.37 %] |
| Bayesiano estático | (s1,s1,s1,s1,s1) | -8.9453 | 61.54 % | [58.56 %,64.52 %] |

La exactitud se calcula únicamente para Monte Carlo, donde se conocen los estados generados. Los valores completos, sin redondear, se guardan en JSON. Los CSV permiten recalcular exactitudes desde los 5000 eventos.

## Archivos principales

| Archivo o carpeta | Contenido |
| --- | --- |
| `anteproyecto_hmm_sismico.md` | Manuscrito en Markdown |
| `main.tex` | Artículo en LaTeX |
| `referencias.bib` | Bibliografía |
| `src/hmm_model.py` | Parámetros y funciones de cálculo comunes |
| `src/experimento.py` | Evaluación conjunta y exportación |
| `run_viterbi_caso.py` | Punto de entrada del experimento completo |
| `scripts/sincronizar_articulo.py` | Sincronización de tablas y cifras |
| `generar_figuras.py` | Generación de las cuatro figuras |
| `resultados/` | Configuración, estadísticas y datos reproducibles |
| `sustentacion/` | Guion individual y presentación HTML de ocho diapositivas para el video |
| `tests/` | Comprobaciones numéricas, de reproducción y coherencia documental |
| `materiales/` | Caso didáctico y materiales de consulta |
| `overleaf_articulo_hmm.zip` | Artículo, bibliografía y figuras para Overleaf |

Las pruebas incluyen el contraste de Viterbi con las 243 trayectorias posibles del caso, los resultados Monte Carlo de referencia, la repetibilidad de exportaciones y la correspondencia entre las tablas de Markdown, LaTeX y el código.

## Material para el video

La carpeta [sustentacion/](sustentacion/README.md) contiene el [guion individual](sustentacion/guion.md) y la [presentación HTML](sustentacion/presentacion.html), preparados para una exposición de aproximadamente 4 minutos y 30 segundos. Abrir el HTML con el navegador; no requiere instalación ni conexión a internet.

La presentación tiene ocho diapositivas, avance con flechas, pantalla completa con F, notas con N, modo de grabación sin controles con G y cronómetro de ensayo con T. El cronómetro no cambia las diapositivas ni graba el video.

## Estructura de carpetas

```
Actividad_2/
|-- README.md
|-- anteproyecto_hmm_sismico.md
|-- main.tex
|-- referencias.bib
|-- run_viterbi_caso.py
|-- generar_figuras.py
|-- requirements.txt
|-- overleaf_articulo_hmm.zip
|-- BITACORA_DECISIONES_EQUIPO.md
|-- src/
|   |-- hmm_model.py
|   `-- experimento.py
|-- scripts/
|   `-- sincronizar_articulo.py
|-- resultados/
|   |-- experimento.json
|   |-- monte_carlo.csv
|   `-- secuencias.csv
|-- figures/
|   |-- fig1_matrices_hmm.png
|   |-- fig2_celosia_viterbi.png
|   |-- fig3_comparacion_logp.png
|   `-- fig4_monte_carlo_boxplot.png
|-- sustentacion/
|   |-- presentacion.html
|   |-- guion.md
|   `-- README.md
|-- tests/
|   |-- test_stochastic.py
|   |-- test_experimento.py
|   `-- test_documentacion.py
|-- docs/
|   `-- superpowers/plans/
`-- materiales/
    |-- caso-sismico.md
    |-- articulo.pdf
    |-- articulo_hmm_sismico_openalex.pdf
    |-- articulo_openalex_sismico.pdf
    `-- stats-07-00047.pdf
```
