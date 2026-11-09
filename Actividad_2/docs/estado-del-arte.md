# Estado del arte: revisión preliminar

## Alcance de la revisión

Se estudia la relación entre modelos ocultos de Markov, regímenes sísmicos y simulación de catálogos. Con corte al 9 de noviembre de 2026, la selección de trabajo contiene diez artículos recientes con texto completo consultable gratuitamente y una referencia clásica adicional. La [matriz bibliográfica](../referencias/matriz-bibliografica.md) delimita pertinencia y alcance de lectura; la [verificación de acceso](../referencias/acceso-a-fuentes.md) documenta las vías de consulta. Los registros estructurados se conservan en [BibTeX](../referencias/bibliografia.bib).

La revisión es exploratoria dirigida, todavía no una revisión sistemática cerrada. Combina antecedentes directamente sísmicos con trabajos metodológicos identificados como tales. No se ha consultado directamente Scopus o Web of Science ni comprobado la indexación de cada revista. La lectura crítica integral sigue abierta aunque se haya comprobado la disponibilidad del texto.

## Observaciones, modelos e incertidumbre

Wang et al. [1] comparan procesos de renovación para registros paleosísmicos y consideran incertidumbre de modelo y de medición. Este antecedente apoya discutir alternativas y limitaciones, pero no es un HMM categórico. El empleo de MCMC para estimar parámetros no debe confundirse con una cadena oculta que genere categorías observadas.

Willis et al. [2] utilizan HMM dentro de un procedimiento de extracción de características espectrales de microseismicidad inducida, seguido de agrupamiento y análisis focal. Su pertinencia es metodológica: demuestra otra función de los estados latentes en datos sísmicos, sin equivalencia entre sus observaciones espectrales y las categorías de magnitud del presente catálogo sintético.

Georgakopoulou et al. [3] y Rizal et al. [4] utilizan PHMM o extensiones para estudiar frecuencias sísmicas. Las observaciones son conteos y los estados se relacionan con tasas. Sus intensidades y cantidades de estados no justifican directamente las matrices de un modelo categórico por evento.

Rizal et al. [5] comparan modelos gaussianos independientes con GHMM para máximos anuales de magnitud. Es un antecedente cercano a las observaciones de magnitud y ofrece una comparación entre modelos con y sin dependencia secuencial. Sin embargo, un máximo anual no equivale a la categoría de cada evento y una densidad continua no es una fila de una matriz B finita.

## Simulación, memoria y validación

Neely et al. [6] incorporan memoria de falla mediante estados no observados vinculados con acumulación y liberación de deformación. Este antecedente permite contrastar hipótesis físicas con etiquetas didácticas; la versión gratuita consultable es un manuscrito de autor, que debe distinguirse de la edición publicada.

Kravchinsky y van der Baan [7] conectan autómatas celulares con cadenas absorbentes para comparar estadísticas de secuencias simuladas. Barani et al. [8] presentan un generador estocástico de catálogos basado en restricciones físicas, acompañado de código y salidas disponibles. Son antecedentes de simulación reproducible, sin constituir ambos un HMM categórico ni validar los parámetros de este ejercicio.

Köhler et al. [9] describen dificultades de generalización temporal en modelos neuronales, markovianos e híbridos. Shahzadi et al. [10] estudian registros incompletos con variantes de HMM, con aplicación empírica a erupciones. Estos trabajos delimitan retos de futuras extensiones con datos reales; no representan experimentos ya efectuados en el presente estudio.

Para el marco teórico se conserva la referencia clásica de Rabiner [11], disponible en la página académica del autor y fuera del conteo de publicaciones recientes.

## Posicionamiento del estudio

La comparación distingue tres ejes: unidad de observación, interpretación de estados y tipo de evaluación. El estudio se sitúa en la simulación de categorías por evento con parámetros fijados y estados generadores conocidos. Evalúa decodificación y sensibilidad controlada de A, B y π, sin inferir tasas de ocurrencia ni pronosticar terremotos reales.

El aporte previsto consiste en documentar esa comparación mediante réplicas, métricas y evidencia de reproducción. La revisión inicial no demuestra un vacío científico global ni permite afirmar una contribución inédita. La evaluación final requerirá contrastar experimentos ejecutados con los antecedentes pertinentes y completar la lectura crítica.

## Referencias

[1] T. Wang et al., “Earthquake forecasting from paleoseismic records,” *Nature Communications*, vol. 15, art. 1944, 2024. [doi: 10.1038/s41467-024-46258-z](https://doi.org/10.1038/s41467-024-46258-z).

[2] R. M. Willis, H. Yoon, J. A. Silva, R. Juanes, S. Williams-Stroud y S. M. Frailey, “Unsupervised Clustering of Microseismic Events and Focal Mechanism Analysis at the CO2 Injection Site in Decatur, Illinois,” *Journal of Geophysical Research: Machine Learning and Computation*, vol. 2, no. 3, art. e2024JH000544, 2025. [doi: 10.1029/2024JH000544](https://doi.org/10.1029/2024JH000544).

[3] E. Georgakopoulou et al., “Seismic Evaluation Based on Poisson Hidden Markov Models—The Case of Central and South America,” *Stats*, vol. 7, no. 3, pp. 777–792, 2024. [doi: 10.3390/stats7030047](https://doi.org/10.3390/stats7030047).

[4] J. Rizal, A. Y. Gunawan, S. W. Indratno e I. Meilano, “Seismic activity analysis of five major earthquake source segments in the Sumatra megathrust zone: Each segment and two adjacent segments points of view,” *Bulletin of the New Zealand Society for Earthquake Engineering*, vol. 56, no. 2, pp. 55–70, 2023. [doi: 10.5459/bnzsee.1555](https://doi.org/10.5459/bnzsee.1555).

[5] J. Rizal, A. Y. Gunawan, S. Yosmar y A. Nuryaman, “Seismicity Pattern Recognition in the Sumatra Megathrust Zone Through Mathematical Modeling of the Maximum Earthquake Magnitude Using Gaussian Mixture Models,” *Mathematical Modelling of Engineering Problems*, vol. 11, no. 5, pp. 1179–1188, 2024. [doi: 10.18280/mmep.110506](https://doi.org/10.18280/mmep.110506).

[6] J. S. Neely, L. Salditch, B. D. Spencer y S. Stein, “A More Realistic Earthquake Probability Model Using Long-Term Fault Memory,” *Bulletin of the Seismological Society of America*, vol. 113, no. 2, pp. 843–855, 2023. [doi: 10.1785/0120220083](https://doi.org/10.1785/0120220083).

[7] E. Kravchinsky y M. van der Baan, “Magnitude-Frequency Distributions and Slip-History Predictions for Earthquakes Using Cellular Automata and Absorbing Markov Chains,” *Journal of Geophysical Research: Solid Earth*, vol. 127, no. 4, art. e2021JB022480, 2022. [doi: 10.1029/2021JB022480](https://doi.org/10.1029/2021JB022480).

[8] S. Barani, M. Taroni, D. Zaccagnino, P. Artale Harris y G. Petrillo, “A physics-informed stochastic model for the long-term correlation of earthquakes,” *Communications Earth & Environment*, vol. 6, art. 674, 2025. [doi: 10.1038/s43247-025-02608-3](https://doi.org/10.1038/s43247-025-02608-3).

[9] J. Köhler et al., “Neural Earthquake Forecasting with Minimal Information: Limits, Interpretability, and the Role of Markov Structure,” *Pure and Applied Geophysics*, vol. 183, pp. 913–934, 2026. [doi: 10.1007/s00024-026-03910-7](https://doi.org/10.1007/s00024-026-03910-7).

[10] A. Shahzadi, T. Wang, M. Parry y M. Bebbington, “Modelling time-inhomogeneous incomplete records of point processes using variants of hidden Markov models,” *Advances in Data Analysis and Classification*, vol. 20, pp. 663–691, 2026. [doi: 10.1007/s11634-025-00632-x](https://doi.org/10.1007/s11634-025-00632-x).

[11] L. R. Rabiner, “A tutorial on hidden Markov models and selected applications in speech recognition,” *Proceedings of the IEEE*, vol. 77, no. 2, pp. 257–286, 1989. [doi: 10.1109/5.18626](https://doi.org/10.1109/5.18626).
