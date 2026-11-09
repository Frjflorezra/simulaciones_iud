"""Demostración de una secuencia y exportación de evidencias reproducibles."""

import csv
import io
import json
from numbers import Integral
from pathlib import Path
import platform

import numpy as np


CSV_FIELDS = (
    "evento", "estado_real", "etiqueta_real", "observacion", "categoria",
    "viterbi", "etiqueta_viterbi", "independiente", "etiqueta_independiente",
)


def ejecutar(model, configuration, scenario, n_events, seed):
    """Evalúa una secuencia con etiquetas de la configuración validada.

    Los estados reales se utilizan únicamente después de la decodificación
    para calcular métricas y conservar la referencia sintética en el CSV.
    """
    if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
        raise ValueError("La semilla debe ser un entero no negativo.")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    states, observations = model.sample(n_events, rng)
    viterbi, log_joint = model.viterbi(observations)
    independent = model.decode_independent(observations)
    log_likelihood = model.forward_log_likelihood(observations)
    n_events = len(states)
    state_labels = configuration["estados"]
    symbol_labels = configuration["observaciones"]
    rows = [
        {
            "evento": t + 1,
            "estado_real": int(state),
            "etiqueta_real": state_labels[state],
            "observacion": int(symbol),
            "categoria": symbol_labels[symbol],
            "viterbi": int(viterbi[t]),
            "etiqueta_viterbi": state_labels[viterbi[t]],
            "independiente": int(independent[t]),
            "etiqueta_independiente": state_labels[independent[t]],
        }
        for t, (state, symbol) in enumerate(zip(states, observations))
    ]
    summary = {
        "tipo_ejecucion": "demostracion_secuencia_unica",
        "escenario": scenario,
        "eventos": n_events,
        "semilla": int(seed),
        "generador": "numpy.random.PCG64",
        "muestreo": "inversa_cdf_dos_uniformes_por_evento",
        "unidad_secuencial": "evento",
        "tipo_datos": "sinteticos",
        "entorno": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sistema": platform.system(),
            "arquitectura": platform.machine(),
        },
        "modelo": {
            "pi": model.pi.tolist(), "A": model.A.tolist(), "B": model.B.tolist(),
            "estados": list(state_labels), "observaciones": list(symbol_labels),
        },
        "metricas": {
            "exactitud_viterbi": float(np.mean(viterbi == states)),
            "exactitud_independiente": float(np.mean(independent == states)),
            "log_verosimilitud": log_likelihood,
            "log_verosimilitud_por_evento": log_likelihood / n_events,
            "log_probabilidad_conjunta_viterbi": log_joint,
            "log_posterior_trayectoria_viterbi": log_joint - log_likelihood,
            "frecuencia_cambios_estado": (
                float(np.mean(states[1:] != states[:-1])) if n_events > 1 else None
            ),
            "proporcion_estados": (np.bincount(states, minlength=model.n_states) / n_events).tolist(),
            "proporcion_observaciones": (
                np.bincount(observations, minlength=model.n_symbols) / n_events
            ).tolist(),
        },
    }
    return rows, summary


def guardar(rows, summary, output_directory):
    """Escribe en una carpeta nueva: no sobrescribe una ejecución previa."""
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "secuencia.csv").write_text(csv_buffer.getvalue(), encoding="utf-8", newline="")
    (directory / "resumen.json").write_text(summary_text, encoding="utf-8", newline="")
