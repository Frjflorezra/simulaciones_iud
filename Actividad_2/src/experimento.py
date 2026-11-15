"""Evaluación y exportación del experimento HMM, sin cálculos duplicados."""

import csv
import json
from pathlib import Path
import platform

import numpy as np

from . import hmm_model as h


def run_experiment(N_runs=100, T=50, seed=42):
    h.verify_model(h.A, h.B, h.PI)
    vit, _, delta, psi = h.viterbi(h.OBS_BASE, h.A, h.B, h.PI)
    b1, ties = h.baseline1(h.OBS_BASE, h.B)
    b2 = h.baseline2(h.OBS_BASE, h.B, h.PI)
    base = {}
    for name, path in {"viterbi": vit, "b1": b1, "b2": b2}.items():
        log_probability = float(h.joint_log_prob(path, h.OBS_BASE, h.A, h.B, h.PI))
        base[name] = {"path": path.tolist(), "probability": float(np.exp(log_probability)),
                      "log_probability": log_probability}
    accuracy, records = h.monte_carlo_experiment(N_runs, T, seed)
    report = {
        "configuration": {"N_runs": N_runs, "T": T, "seed": seed,
                          "generator": "numpy.random.RandomState / MT19937",
                          "draw_order": "state_then_emission_each_event",
                          "tie_break": "first_index", "state_index_base": 0,
                          "std_ddof": 1, "ci95_multiplier": 1.96},
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "parameters": {"A": h.A.tolist(), "B": h.B.tolist(), "pi": h.PI.tolist()},
        "base": {"observations": list(h.OBS_BASE), "models": base,
                 "delta": delta.tolist(), "psi": psi.tolist(), "b1_ties": ties},
        "monte_carlo": {"accuracy": {k: v.tolist() for k, v in accuracy.items()},
                        "summary": {k: h.summarize_accuracy(v) for k, v in accuracy.items()}}
    }
    return report, records


def export_results(report, records, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'experimento.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    with (output_dir / 'monte_carlo.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['replica', 'viterbi', 'b1', 'b2'])
        accuracy = report['monte_carlo']['accuracy']
        for replica, values in enumerate(zip(accuracy['viterbi'], accuracy['b1'], accuracy['b2']), 1):
            writer.writerow([replica, *values])
    with (output_dir / 'secuencias.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['replica', 't', 'state', 'observation',
                                                   'viterbi', 'b1', 'b2'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
