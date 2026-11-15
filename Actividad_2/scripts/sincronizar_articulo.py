"""Sincroniza parámetros, tablas y cifras del artículo desde el experimento.

No modifica referencias, autoría ni las bitácoras históricas.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experimento import run_experiment

REPORT, _ = run_experiment()
BASE = REPORT['base']
STATS = REPORT['monte_carlo']['summary']
NAMES = {'viterbi': 'Algoritmo de Viterbi', 'b1': 'Baseline 1 (Máxima Emisión)',
         'b2': 'Baseline 2 (Bayesiano Estático)'}
BS = chr(92)
ROW = ' ' + BS * 2 + '\n'
LISTING = '''from src.hmm_model import A, B, PI, OBS_BASE, viterbi
from src.experimento import run_experiment, export_results

path, log_prob, delta, psi = viterbi(OBS_BASE, A, B, PI)
report, records = run_experiment(N_runs=100, T=50, seed=42)
export_results(report, records, "resultados")'''


def common(text):
    replacements = {
        '-7.5415': '-7.4361',
        'Evaluación comparativa neutral y reproducible que aísla analíticamente el aporte marginal de la matriz de transición $A$.':
            'Evaluación comparativa reproducible de un decodificador secuencial y dos clasificadores puntuales sobre las mismas observaciones.',
        'Para aislar objetivamente el aporte marginal de la memoria de transición temporal (matriz $A$), se implementaron dos baselines de clasificación estática puntual sin memoria:':
            'Para comparar la decodificación secuencial con reglas puntuales, se implementaron dos baselines estáticos sin memoria. Los métodos difieren en objetivo, prior y acceso a la secuencia completa; la comparación no aísla el efecto de A por separado:',
        'Para garantizar que las discrepancias observadas se deban exclusivamente a la estructura algorítmica y no al azar del muestreo,':
            'Para evitar que cada método reciba una muestra diferente,',
        'en este entorno controlado se aísla con precisión el costo algorítmico del sesgo a priori rígido (el cual reduce la precisión del Baseline 2 a un $61.54\\%$).':
            'en este entorno controlado se comparan métodos completos: el Baseline 2 obtiene una precisión media de $61.54\\%$, sin que esta comparación permita atribuir la diferencia exclusivamente al prior.',
        'Aísla analíticamente cómo la matriz $A$ desempata lecturas idénticas ($P=0.50$) y supera sesgos estáticos.':
            'Compara decodificación secuencial y clasificación puntual ante emisiones ambiguas.',
        'Aísla analíticamente cómo la matriz de transición $A$ desempata observaciones intermedias idénticas ($P=0.50$) y supera la ceguera por sesgo a priori de modelos estáticos.':
            'Compara decodificación secuencial y clasificación puntual ante emisiones ambiguas.',
        'sufre un empate exacto e irresoluble': 'presenta un empate exacto que exige una convención de desempate',
        'cualquier algoritmo sin memoria temporal experimenta un empate estocástico irresoluble, forzando decisiones arbitrarias ajenas a la física del proceso.':
            'el clasificador por máxima emisión presenta un empate y requiere una convención. En este experimento selecciona el primer índice, s2. El clasificador bayesiano estático pondera las emisiones por el prior y obtiene un máximo único en s1 ante magnitud media.',
        'El modelo sufre un empate irresoluble y queda ciego, incapaz de decidir sin forzar una convención externa.':
            'El clasificador presenta un empate de emisiones y lo resuelve mediante la convención fijada: elegir Actividad Menor, tanto en el caso base como en Monte Carlo.',
        'los clasificadores reactivos carecen de criterio objetivo de decisión, mientras que los clasificadores bayesianos con distribución a priori fija quedan paralizados por el sesgo del estado dominante':
            'el clasificador por máxima emisión necesita la convención de desempate hacia s2, mientras que el bayesiano estático asigna reposo por el peso del prior',
        'superando con significancia estadística al modelo bayesiano estático':
            'obteniendo una precisión media mayor que la del modelo bayesiano estático',
        'determinando si la incorporación de la matriz de transición temporal genera diferencias estadísticamente significativas.':
            'describiendo las diferencias de precisión y su incertidumbre entre métodos.',
        'desambigua causalmente': 'reconstruye retrospectivamente',
        'retroceso causal': 'retroceso',
        'Reconstrucción Causal': 'Reconstrucción Global',
        'Resolución Causal': 'Resolución Secuencial',
        'sumen exactamente': 'sumen, dentro de la tolerancia numérica,',
        'clasificando toda la secuencia erróneamente como Reposo constante':
            'asignando Reposo a los cinco eventos del caso, sin etiquetas verdaderas para evaluar esos aciertos',
        'superando significativamente al bayesiano estático':
            'obteniendo una precisión media mayor que la del bayesiano estático',
        'La modelación explícita de transiciones de primer orden actúa como un regularizador causal indispensable para dotar de plausibilidad física y consistencia matemática a la inferencia de estados latentes ante señales discretas solapadas.':
            'La modelación de transiciones de primer orden permite incorporar dependencia temporal en la decodificación retrospectiva de estos escenarios sintéticos. Este resultado no establece validez física ni capacidad predictiva sobre sismos reales.',
        ' (45 operaciones elementales de producto-máximo)': '',
        'Esto garantiza una solución exacta y en tiempo real, muy superior a la búsqueda exhaustiva que requeriría':
            'La reconstrucción utiliza la secuencia completa y no es una predicción en tiempo real. La búsqueda exhaustiva requeriría',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def markdown_results():
    lines = [r'''## 5. Resultados y Análisis Estadístico

Los resultados proceden del experimento centralizado en `src`, con las matrices del caso didáctico y el mismo desempate en ambas fases. Las salidas completas se conservan en `resultados/experimento.json`, las exactitudes por réplica en `resultados/monte_carlo.csv` y los estados, observaciones y predicciones por evento en `resultados/secuencias.csv`. Los índices de los archivos de datos comienzan en cero.

### 5.1. Evolución Analítica de la Celosía de Viterbi sobre la Secuencia Base ($T = 5$)

Se evaluaron las observaciones Baja, Baja, Media, Media y Alta. La Figura 2 presenta las probabilidades de camino parcial máximo y los predecesores.

![Figura 2 — Celosía de Viterbi y Trayectorias Comparadas](figures/fig2_celosia_viterbi.png)

*Panel A: los enlaces azules reconstruyen la trayectoria óptima; los grises muestran otros predecesores seleccionados por ψ. Panel B: una fila por método evita ocultar estados coincidentes. Los recuadros discontinuos señalan los empates de B1, resueltos hacia s2.*

| t | Observación | δ(s1) | δ(s2) | δ(s3) | ψ (índices base cero) |
| --- | --- | ---: | ---: | ---: | --- |
''']
    for t, (d, psi) in enumerate(zip(BASE['delta'], BASE['psi']), 1):
        obs = ['Baja', 'Media', 'Alta'][BASE['observations'][t-1]]
        lines.append(f'| {t} | {obs} | {d[0]:.9f} | {d[1]:.9f} | {d[2]:.9f} | {psi} |\n')
    lines.append(r'''
El retroceso desde $s_3$ en el quinto evento recupera $(s_1,s_1,s_2,s_3,s_3)$. El camino óptimo puede diferir de los máximos locales de $\delta_t$. Su probabilidad conjunta es $P^*=0.000707472$ y $\ln P^*=-7.2538$.

![Figura 3 — Comparación de Log-verosimilitud Conjunta](figures/fig3_comparacion_logp.png)

*Cada punto muestra la log-probabilidad conjunta de una trayectoria. Los valores mayores se encuentran a la derecha. Se indica la secuencia realmente devuelta por cada método.*

Tabla 2: Desempeño comparativo en la secuencia representativa determinista ($T = 5$).

| Método de Clasificación | Secuencia Inferida | Manejo de empate | Probabilidad conjunta | Log-verosimilitud conjunta |
| --- | --- | --- | ---: | ---: |
'''.replace('\x05', BS))
    for key, name in NAMES.items():
        result = BASE['models'][key]
        path = '(' + ', '.join(f's{s+1}' for s in result['path']) + ')'
        rule = {'viterbi': 'Trayectoria global según A, B y π',
                'b1': 'Primer índice: s2 ante magnitud media', 'b2': 'Prior inicial fijo'}[key]
        lines.append(f"| {name} | {path} | {rule} | {result['probability']:.10g} | {result['log_probability']:.4f} |\n")
    lines.append('''
No se calcula exactitud para estos cinco eventos porque el caso ilustrativo no aporta estados verdaderos.

### 5.2. Evaluación Estadística Inferencial mediante Simulación Monte Carlo ($N = 100, T = 50$)

Se generaron 100 secuencias de 50 eventos con `RandomState(42)`, sorteando estado y emisión de forma intercalada. Los tres métodos evaluaron las mismas secuencias. La unidad independiente es la secuencia, no cada uno de los 5000 eventos.

![Figura 4 — Evaluación Monte Carlo IC95%](figures/fig4_monte_carlo_boxplot.png)

*Panel A: distribución de exactitudes, con un punto por réplica, mediana y media. Panel B: medias e intervalos aproximados del 95 %, calculados con desviación estándar muestral.*

Tabla 3: Métricas estadísticas de precisión de decodificación tras 100 simulaciones independientes.

| Modelo / Método | Media | Desv. Est. (s) | Mínimo | Máximo | IC95 % |
| --- | ---: | ---: | ---: | ---: | --- |
''')
    for key, name in NAMES.items():
        s = STATS[key]
        lines.append(f"| {name} | {s['mean']:.4f} ({s['mean']*100:.2f} %) | {s['std']:.4f} | {s['min']:.4f} | {s['max']:.4f} | [{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}] |\n")
    lines.append('''
Viterbi obtuvo una precisión media mayor en 2.90 puntos porcentuales que B1 y en 11.08 puntos que B2. Los intervalos individuales de Viterbi y B2 no se solapan; no se calculó una prueba de hipótesis pareada ni un valor p. La dispersión de Viterbi (s=0.1094) es mayor que la de B1 (s=0.0839) y menor que la de B2 (s=0.1518).

''')
    return ''.join(lines)


def latex_results():
    text = r'''\section{Resultados y Análisis Estadístico}

\subsection{Evolución Analítica de la Celosía de Viterbi sobre la Secuencia Base ($T=5$)}

Se evaluó la secuencia Baja, Baja, Media, Media y Alta con las matrices del caso didáctico. La Tabla~\ref{tab:celosia_viterbi} presenta los valores calculados por el núcleo común.

\begin{table}[htbp]
\centering
\small
\caption{Probabilidades de camino parcial máximo y predecesores. Los índices de $\psi$ comienzan en cero.}
\label{tab:celosia_viterbi}
\begin{tabular}{clrrrl}
\toprule
$t$ & Observación & $\delta_t(s_1)$ & $\delta_t(s_2)$ & $\delta_t(s_3)$ & $\psi_t$ \\
\midrule
'''
    for t, (d, psi) in enumerate(zip(BASE['delta'], BASE['psi']), 1):
        obs = ['Baja', 'Media', 'Alta'][BASE['observations'][t-1]]
        text += f'{t} & {obs} & {d[0]:.9f} & {d[1]:.9f} & {d[2]:.9f} & {psi}' + ROW
    text += r'''\bottomrule
\end{tabular}
\end{table}

El retroceso desde $s_3$ en el quinto evento recupera $(s_1,s_1,s_2,s_3,s_3)$. El camino óptimo puede diferir de los máximos locales de $\delta_t$; la reconstrucción utiliza la secuencia completa.
\begin{equation}
P^*=0.000707472,\qquad \ln P^*=\ln(0.000707472)=-7.2538.
\end{equation}

\subsection{Contraste frente a los Baselines en la Secuencia Base}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/fig2_celosia_viterbi.png}
\caption{Panel A: celosía con valores $\delta_t$ y enlaces seleccionados por $\psi$; el camino óptimo aparece en azul. Panel B: estados inferidos por cada método; los recuadros discontinuos marcan los empates de B1 resueltos por primer índice hacia $s_2$.}
\label{fig:celosia}
\end{figure}

La Tabla~\ref{tab:comparacion_secuencia} compara las trayectorias devueltas por los métodos. No se calcula exactitud para este caso ilustrativo porque no se conocen estados verdaderos.

\begin{table}[htbp]
\centering
\small
\caption{Trayectorias y log-probabilidad conjunta en la secuencia base.}
\label{tab:comparacion_secuencia}
\begin{tabular}{lcr}
\toprule
Método & Trayectoria inferida & $\ln P$ \\
\midrule
'''
    for key, name in NAMES.items():
        result = BASE['models'][key]
        path = '(' + ', '.join(f's_{s+1}' for s in result['path']) + ')'
        text += f"{name} & ${path}$ & {result['log_probability']:.4f}" + ROW
    text += r'''\bottomrule
\end{tabular}
\end{table}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/fig3_comparacion_logp.png}
\caption{Log-verosimilitud conjunta: Viterbi ($-7.2538$), B1 ($-7.4361$) y B2 ($-8.9453$). Los valores mayores se sitúan a la derecha. B1 aplica el mismo desempate hacia $s_2$ utilizado en Monte Carlo.}
\label{fig:logp}
\end{figure}

\subsection{Evaluación Estadística mediante Simulación Monte Carlo ($N=100,T=50$)}

Se generaron 100 secuencias de 50 eventos con \texttt{RandomState(42)}, sorteando estado y emisión de forma intercalada. Los tres métodos evaluaron las mismas secuencias. La unidad independiente es la secuencia, no cada uno de los 5000 eventos. La Tabla~\ref{tab:monte_carlo} usa desviación muestral e intervalos normales aproximados:
\begin{equation}
IC_{95\%}=\bar{X}\pm1.96\frac{s}{\sqrt{100}}.
\end{equation}

\begin{table}[htbp]
\centering
\small
\caption{Exactitud por secuencia: resumen de las 100 réplicas.}
\label{tab:monte_carlo}
\begin{tabular}{lrrrrl}
\toprule
Método & Media & $s$ & Mínimo & Máximo & $IC_{95\%}$ \\
\midrule
'''
    for key, name in NAMES.items():
        s = STATS[key]
        text += f"{name} & {s['mean']:.4f} & {s['std']:.4f} & {s['min']:.4f} & {s['max']:.4f} & [{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}]" + ROW
    text += r'''\bottomrule
\end{tabular}
\end{table}

Viterbi obtuvo una precisión media de $72.62\%$, frente a $69.72\%$ de B1 y $61.54\%$ de B2: diferencias de 2.90 y 11.08 puntos porcentuales. Los intervalos individuales de Viterbi y B2 no se solapan; no se calculó una prueba de hipótesis pareada ni un valor p. La desviación de Viterbi ($s=0.1094$) supera la de B1 ($s=0.0839$) y es menor que la de B2 ($s=0.1518$).

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/fig4_monte_carlo_boxplot.png}
\caption{Panel A: distribución de exactitudes por réplica, mediana y media. Panel B: medias e intervalos aproximados del 95\%, calculados con desviación muestral. Viterbi: $72.62\%$ e IC $[70.48\%,74.76\%]$; B1: $69.72\%$ e IC $[68.07\%,71.37\%]$; B2: $61.54\%$ e IC $[58.56\%,64.52\%]$.}
\label{fig:montecarlo}
\end{figure}

Las salidas completas se conservan en \texttt{resultados/experimento.json}, \texttt{resultados/monte\_carlo.csv} y \texttt{resultados/secuencias.csv}. Los índices de estados y observaciones en estos archivos comienzan en cero.

'''
    return text


def main():
    md_path, tex_path = ROOT / 'anteproyecto_hmm_sismico.md', ROOT / 'main.tex'
    md = common(md_path.read_text(encoding='utf-8-sig'))
    md = md.replace('## 4. Metodología e Implementación\n\n## 4. Metodología e Implementación', '## 4. Metodología e Implementación')
    md = md.replace('Asimismo, la semilla pseudoaleatoria evoluciona de manera continua (`seed = 42`) sin reinicios artificiales entre réplicas.', 'Se inicializa una sola instancia local de `numpy.random.RandomState(42)` (MT19937), sin reinicios entre réplicas. En cada evento se sortea el estado y después su emisión, antes de avanzar al siguiente evento. El orden de generación forma parte del protocolo reproducible.')
    config_md = '\n\n**Convenciones del experimento:** B1 resuelve empates exactos por el primer índice ($s_2$ ante magnitud media), en ambas fases. La desviación muestral se calcula con `ddof=1`; el IC95 % es la aproximación normal de la media entre secuencias. No se calcula un valor p ni se sustituye una prueba pareada por intervalos individuales.\n\n'
    if '**Convenciones del experimento:**' not in md:
        md = md.replace('### 4.4. Implementación', config_md + '### 4.4. Implementación')
    md = md.replace('El algoritmo de Viterbi fue codificado en Python 3.13 con NumPy v1.26, garantizando determinismo estricto:', 'El núcleo se encuentra en `src/hmm_model.py`, y la evaluación y exportación en `src/experimento.py`. La ejecución se verificó con Python 3.13.3 y NumPy 2.3.3:')
    md = re.sub(r'```python\n.*?\n```', lambda _: '```python\n' + LISTING + '\n```', md, count=1, flags=re.S)
    md = md.replace('emplea `np.where` para identificar empates y explicita formalmente la necesidad de una regla de desempate convencional.', 'emplea `np.flatnonzero` para identificar empates y selecciona el primer índice tanto en el caso base como en Monte Carlo.')
    md = md.replace('generaría secuencias desconectadas o prohibidas por la matriz de transición.', 'no garantiza maximizar la probabilidad conjunta de la trayectoria.')
    future = '### 5.3.' + md.split('### 5.3.', 1)[1].split('## 6. Discusión', 1)[0]
    md = md.split('## 5. Resultados', 1)[0] + markdown_results() + future + '## 6. Discusión' + md.split('## 6. Discusión', 1)[1]
    md = md.replace('Esta precisión supera de manera estadísticamente significativa (sin solapamiento de intervalos) al clasificador bayesiano estático', 'Esta precisión media es mayor que la del clasificador bayesiano estático')
    md = md.replace('demostrando que la modelación de transiciones reduce la dispersión y el error de clasificación en series estocásticas discretas.', 'mostrando una menor proporción media de errores en estos escenarios. Viterbi no presenta la menor dispersión: su desviación supera a la de B1. No se calculó una prueba pareada de significancia.')
    old = r'Una interpretación superficial sugeriría que prescindir de la memoria temporal conlleva un costo marginal bajo ($2.9\%$). Sin embargo, este desempeño se explica por el diseño diagonal de la matriz de emisión $B$, altamente específica en los extremos ($B_{1,1} = 0.85$ y $B_{3,3} = 0.40$). En sistemas de monitoreo con mayor ruido observacional o solapamiento en todas las bandas de emisión, el rendimiento de los métodos reactivos colapsaría drásticamente.'
    md = md.replace(old, 'La diferencia observada es de 2.90 puntos porcentuales. B1 aprovecha las emisiones y el desempate fijo hacia $s_2$. Este resultado depende de esos parámetros y de la regla de desempate; no se ejecutó un análisis de sensibilidad que permita extrapolarlo a emisiones más ruidosas.')
    md_path.write_text(md, encoding='utf-8')

    tex = common(tex_path.read_text(encoding='utf-8-sig'))
    for name in ('A', 'B'):
        matrix = REPORT['parameters'][name]
        body = '\n' + (' ' + BS*2 + '\n').join('    ' + ' & '.join(f'{v:.2f}' for v in row) for row in matrix) + '\n    '
        tex = re.sub(name + r' = \\begin\{pmatrix\}.*?\\end\{pmatrix\}', lambda _: name + r' = \begin{pmatrix}' + body + r'\end{pmatrix}', tex, count=1, flags=re.S)
    for old, new in [
        ('Fila 2: $0.20 + 0.50 + 0.30', 'Fila 2: $0.30 + 0.50 + 0.20'),
        ('Fila 3: $0.05 + 0.25 + 0.70', 'Fila 3: $0.10 + 0.30 + 0.60'),
        ('Fila 1: $0.70 + 0.25 + 0.05', 'Fila 1: $0.85 + 0.12 + 0.03'),
        ('Fila 2: $0.10 + 0.50 + 0.40', 'Fila 2: $0.40 + 0.50 + 0.10'),
        ('Fila 3: $0.00 + 0.50 + 0.50', 'Fila 3: $0.10 + 0.50 + 0.40')]:
        tex = tex.replace(old, new)
    tex = re.sub(r'\\begin\{lstlisting\}\[language=Python,.*?\\end\{lstlisting\}', lambda _: r'\begin{lstlisting}[language=Python, caption={Uso del núcleo y ejecución del experimento reproducible.}, label={lst:viterbi}]' + '\n' + LISTING + '\n' + r'\end{lstlisting}', tex, count=1, flags=re.S)
    tex = tex.replace(r'En el Listado~\ref{lst:viterbi} se presenta la implementación modular del núcleo computacional desarrollada en el script \texttt{run\_viterbi\_caso.py}.', r'En el Listado~\ref{lst:viterbi} se muestra el uso de \texttt{src/hmm\_model.py} y \texttt{src/experimento.py}. El script \texttt{run\_viterbi\_caso.py} es el punto de entrada y exporta los resultados.')
    config_tex = r'''\noindent \textbf{Configuración reproducible:} Se inicializa una sola instancia local de \texttt{numpy.random.RandomState(42)} (MT19937). En cada evento se sortea el estado y después su emisión; no se reinicia la semilla entre réplicas. B1 resuelve empates por el primer índice ($s_2$ ante magnitud media) en ambas fases. Se usa desviación muestral (\texttt{ddof=1}) e intervalo normal aproximado $\bar{X}\pm1.96s/\sqrt{N}$. No se calcula un valor p ni se sustituye una prueba pareada por intervalos individuales. La ejecución se verificó con Python 3.13.3 y NumPy 2.3.3.

'''
    if r'\textbf{Configuración reproducible:}' not in tex:
        tex = tex.replace(r'\subsection{Prevención de Fuga', config_tex + r'\subsection{Prevención de Fuga')
    tex = tex.replace('Para dotar al estudio de significancia estadística sin inventar datos empíricos,', 'Para cuantificar la variación entre secuencias sintéticas,')
    tex = tex.split(r'\section{Resultados y Análisis Estadístico}', 1)[0] + latex_results() + r'\section{Discusión}' + tex.split(r'\section{Discusión}', 1)[1]
    old = r'Una explicación alternativa para la superioridad de Viterbi podría ser la mayor dimensionalidad paramétrica del modelo completo (inclusión de la matriz $A$). No obstante, la evaluación de Monte Carlo demostró que la dispersión de Viterbi ($s = 0.1092$) es moderada y su ganancia sistemática responde al acoplamiento temporal estocástico.'
    tex = tex.replace(old, r'Viterbi utiliza las transiciones y la secuencia completa, mientras que los baselines clasifican cada observación por separado. La precisión media mayor no demuestra una menor dispersión: Viterbi tiene $s=0.1094$, B1 $s=0.0839$ y B2 $s=0.1518$. No se ejecutaron escenarios de sensibilidad ni una prueba pareada que permitan generalizar la ventaja observada.')
    tex = tex.replace('superando con significancia estadística disjunta al clasificador bayesiano estático', 'obteniendo una precisión media mayor que la del clasificador bayesiano estático')
    tex = tex.replace(r'[58.91\%, 64.17\%]', r'[58.56\%, 64.52\%]')
    tex = tex.replace(r'y mejorando en un $+2.90\%$ al clasificador por máxima emisión.', 'y aventajando en 2.90 puntos porcentuales al clasificador por máxima emisión. Estas diferencias son descriptivas; no se calculó una prueba pareada de significancia.')
    tex = tex.replace('el clasificador reactivo quedó indeterminado ante observaciones medias,', 'el clasificador reactivo necesitó un desempate convencional hacia $s_2$ ante observaciones medias,')
    tex_path.write_text(tex, encoding='utf-8')
    print('Parámetros y tablas de ambos manuscritos sincronizados con src.')


if __name__ == '__main__':
    main()
