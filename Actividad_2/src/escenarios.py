"""Lectura de parámetros y construcción de comparaciones controladas."""

import json
from pathlib import Path

import numpy as np

from .hmm import HMM


NOMBRES_ESCENARIOS = (
    "base", "mayor_persistencia", "emisiones_menos_informativas", "inicio_diferente"
)


def cargar_escenarios(path):
    """Devuelve la configuración y los cuatro HMM del diseño de tres estados."""
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto JSON.")
    required = {"pi", "A", "B", "estados", "observaciones"}
    missing = required - config.keys()
    if missing:
        raise ValueError("Faltan campos de configuración: " + ", ".join(sorted(missing)))
    base = HMM(config["pi"], config["A"], config["B"])
    if base.n_states != 3 or base.n_symbols != 3:
        raise ValueError("Los escenarios del catálogo requieren tres estados y tres símbolos.")
    for name, size in (("estados", base.n_states), ("observaciones", base.n_symbols)):
        labels = config[name]
        if (not isinstance(labels, list) or len(labels) != size
                or any(not isinstance(label, str) or not label.strip() for label in labels)):
            raise ValueError(f"{name} debe contener {size} etiquetas de texto no vacías.")
        if len(set(labels)) != size:
            raise ValueError(f"Las etiquetas de {name} deben ser únicas.")
    models = {
        "base": base,
        "mayor_persistencia": HMM(base.pi, 0.5 * base.A + 0.5 * np.eye(3), base.B),
        "emisiones_menos_informativas": HMM(base.pi, base.A, 0.7 * base.B + 0.3 / 3),
        "inicio_diferente": HMM([0.05, 0.15, 0.80], base.A, base.B),
    }
    return config, models
