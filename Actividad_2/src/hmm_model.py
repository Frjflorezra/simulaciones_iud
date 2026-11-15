"""
hmm_model.py — Núcleo del modelo HMM para inferencia de regímenes sísmicos.
Autor: Francisco Javier Florez Ramirez
Curso de Simulación — IU Digital de Antioquia
"""

import numpy as np

# ── Parámetros canónicos del modelo λ = (A, B, π) ────────────────────────────
STATES       = ["Reposo Sísmico (s1)", "Actividad Menor (s2)", "Enjambre Sísmico (s3)"]
OBS_LABELS   = ["Magnitud Baja (<3)", "Magnitud Media ([3,5])", "Magnitud Alta (>5)"]
STATE_SHORT  = ["Reposo (s1)", "Act. Menor (s2)", "Enjambre (s3)"]

A = np.array([
    [0.85, 0.12, 0.03],
    [0.30, 0.50, 0.20],
    [0.10, 0.30, 0.60],
])

B = np.array([
    [0.85, 0.12, 0.03],
    [0.40, 0.50, 0.10],
    [0.10, 0.50, 0.40],
])

PI = np.array([0.80, 0.15, 0.05])

# Secuencia base del caso: Baja, Baja, Media, Media, Alta
OBS_BASE = [0, 0, 1, 1, 2]


def verify_model(A, B, pi):
    """Verifica cierre estocástico de las matrices."""
    assert np.allclose(A.sum(axis=1), 1.0, atol=1e-9), "Filas de A no suman 1"
    assert np.allclose(B.sum(axis=1), 1.0, atol=1e-9), "Filas de B no suman 1"
    assert np.isclose(pi.sum(), 1.0, atol=1e-9),       "π no suma 1"


def viterbi(obs_seq, A, B, pi):
    """
    Decodificación óptima de estados latentes mediante Viterbi.
    Retorna: (best_path, log_prob, delta, psi)
    """
    T, N = len(obs_seq), len(pi)
    delta = np.zeros((T, N))
    psi   = np.zeros((T, N), dtype=int)

    delta[0] = pi * B[:, obs_seq[0]]
    psi[0]   = 0

    for t in range(1, T):
        for j in range(N):
            candidates   = delta[t-1] * A[:, j]
            psi[t, j]    = np.argmax(candidates)
            delta[t, j]  = np.max(candidates) * B[j, obs_seq[t]]

    path = np.zeros(T, dtype=int)
    path[-1] = np.argmax(delta[-1])
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]

    log_prob = np.log(delta[-1, path[-1]]) if delta[-1, path[-1]] > 0 else -np.inf
    return path, log_prob, delta, psi


def baseline1(obs_seq, B):
    """Máxima emisión; los empates exactos se resuelven por primer índice."""
    path = []
    ties = []
    for t, o in enumerate(obs_seq):
        emissions  = B[:, o]
        max_val    = emissions.max()
        candidates = np.flatnonzero(emissions == max_val)
        path.append(candidates[0])
        if len(candidates) > 1:
            ties.append(t)
    return np.array(path), ties


def baseline2(obs_seq, B, pi):
    """Clasificador bayesiano puntual estático (π · B)."""
    path = []
    for o in obs_seq:
        posterior = pi * B[:, o]
        path.append(np.argmax(posterior))
    return np.array(path)


def joint_log_prob(path, obs_seq, A, B, pi):
    """Calcula log P(O, S | λ) para una trayectoria dada."""
    lp = np.log(pi[path[0]]) + np.log(B[path[0], obs_seq[0]])
    for t in range(1, len(obs_seq)):
        lp += np.log(A[path[t-1], path[t]] + 1e-300) + np.log(B[path[t], obs_seq[t]] + 1e-300)
    return lp


def monte_carlo_experiment(N_runs=100, T=50, seed=42):
    """Experimento pareado: RandomState/MT19937 y generación intercalada.

    La semilla se aplica una vez por experimento; no se reinicia por réplica.
    Los estados verdaderos se consultan únicamente después de decodificar.
    Retorna exactitudes y registros por evento, con estados base cero.
    """
    rng = np.random.RandomState(seed)
    results = {"viterbi": [], "b1": [], "b2": []}
    records = []

    for replica in range(N_runs):
        states_seq = np.zeros(T, dtype=int)
        obs_seq = np.zeros(T, dtype=int)
        states_seq[0] = rng.choice(len(PI), p=PI)
        obs_seq[0] = rng.choice(B.shape[1], p=B[states_seq[0]])
        for t in range(1, T):
            states_seq[t] = rng.choice(len(PI), p=A[states_seq[t - 1]])
            obs_seq[t] = rng.choice(B.shape[1], p=B[states_seq[t]])

        vit_path, _, _, _ = viterbi(obs_seq, A, B, PI)
        b1_path, _ = baseline1(obs_seq, B)
        b2_path = baseline2(obs_seq, B, PI)
        predictions = {"viterbi": vit_path, "b1": b1_path, "b2": b2_path}
        for key, path in predictions.items():
            results[key].append(float((path == states_seq).mean()))
        for t in range(T):
            records.append({"replica": replica + 1, "t": t + 1,
                            "state": int(states_seq[t]), "observation": int(obs_seq[t]),
                            **{key: int(path[t]) for key, path in predictions.items()}})

    return {k: np.array(v) for k, v in results.items()}, records


def monte_carlo_accuracy(N_runs=100, T=50, seed=42):
    """Exactitudes del experimento reproducible, una por secuencia y método."""
    return monte_carlo_experiment(N_runs, T, seed)[0]


def summarize_accuracy(values):
    """Resumen por réplica: desviación muestral y aproximación normal al IC95%."""
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    half_width = 1.96 * std / np.sqrt(len(values))
    return {"mean": mean, "std": std, "min": float(values.min()),
            "max": float(values.max()),
            "ci95": [float(mean - half_width), float(mean + half_width)]}
