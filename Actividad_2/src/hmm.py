"""HMM categórico con parámetros fijados e inferencia en logaritmos."""

from dataclasses import dataclass
from numbers import Integral

import numpy as np


def _probabilities(values, name):
    raw = np.asarray(values)
    if raw.dtype.kind not in "iuf":
        raise ValueError(f"{name} debe contener probabilidades numéricas reales.")
    array = np.array(raw, dtype=np.float64, copy=True)
    if not np.all(np.isfinite(array)) or np.any(array < 0) or np.any(array > 1):
        raise ValueError(f"{name} debe ser finita y estar entre cero y uno.")
    return array


def _log_probabilities(array):
    with np.errstate(divide="ignore"):
        result = np.log(array)
    result.setflags(write=False)
    return result


@dataclass(frozen=True, eq=False)
class HMM:
    """Filas de A: estado actual; filas de B: estado emisor.

    Las entradas se copian y quedan de solo lectura. La configuración no se
    normaliza automáticamente: un parámetro inválido debe corregirse en origen.
    """

    pi: np.ndarray
    A: np.ndarray
    B: np.ndarray

    def __post_init__(self):
        pi = _probabilities(self.pi, "pi")
        A = _probabilities(self.A, "A")
        B = _probabilities(self.B, "B")
        if pi.ndim != 1 or pi.size == 0:
            raise ValueError("pi debe ser un vector no vacío.")
        n_states = pi.size
        if A.shape != (n_states, n_states):
            raise ValueError("A debe ser cuadrada y compatible con pi.")
        if B.ndim != 2 or B.shape[0] != n_states or B.shape[1] == 0:
            raise ValueError("B debe tener una fila por estado y al menos una columna.")
        if not np.isclose(pi.sum(), 1, rtol=0, atol=1e-12):
            raise ValueError("pi debe sumar uno.")
        for name, array in (("A", A), ("B", B)):
            if not np.allclose(array.sum(axis=1), 1, rtol=0, atol=1e-12):
                raise ValueError(f"Cada fila de {name} debe sumar uno.")
        for name, array in (("pi", pi), ("A", A), ("B", B)):
            array.setflags(write=False)
            object.__setattr__(self, name, array)
            object.__setattr__(self, f"_log_{name}", _log_probabilities(array))

    @property
    def n_states(self):
        return self.pi.size

    @property
    def n_symbols(self):
        return self.B.shape[1]

    def _observations(self, observations):
        # Conserva los tipos originales: [0, True] no debe convertirse en [0, 1].
        array = np.asarray(observations, dtype=object)
        if array.ndim != 1:
            raise ValueError("Las observaciones deben formar una secuencia de dimensión uno.")
        if array.size == 0:
            return np.empty(0, dtype=np.int64)
        if any(isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral)
               for value in array):
            raise ValueError("Las observaciones deben ser índices enteros, sin booleanos.")
        if np.any(array < 0) or np.any(array >= self.n_symbols):
            raise ValueError("Índice de observación fuera del alfabeto del modelo.")
        return array.astype(np.int64, copy=False)

    def sample(self, n_events, rng):
        """Genera estados y símbolos, con dos uniformes por evento.

        rng es un Generator explícito. La primera emisión se extrae desde el
        estado inicial y solo después se utiliza A para el siguiente evento.
        """
        if isinstance(n_events, bool) or not isinstance(n_events, Integral) or n_events < 1:
            raise ValueError("El número de eventos debe ser un entero positivo.")
        if not isinstance(rng, np.random.Generator):
            raise TypeError("rng debe ser un numpy.random.Generator explícito.")
        initial_cdf = np.cumsum(self.pi)
        transition_cdf = np.cumsum(self.A, axis=1)
        emission_cdf = np.cumsum(self.B, axis=1)
        # Corrige exclusivamente el extremo de la CDF por redondeo en float64.
        initial_cdf[-1] = 1.0
        transition_cdf[:, -1] = 1.0
        emission_cdf[:, -1] = 1.0
        uniforms = rng.random((n_events, 2))
        states = np.empty(n_events, dtype=np.int64)
        observations = np.empty(n_events, dtype=np.int64)
        for t, (state_uniform, emission_uniform) in enumerate(uniforms):
            cdf = initial_cdf if t == 0 else transition_cdf[states[t - 1]]
            states[t] = np.searchsorted(cdf, state_uniform, side="right")
            observations[t] = np.searchsorted(emission_cdf[states[t]], emission_uniform, side="right")
        return states, observations

    def forward_log_likelihood(self, observations):
        """Devuelve log P(observaciones); para secuencias imposibles, −infinito."""
        observations = self._observations(observations)
        if observations.size == 0:
            return 0.0
        alpha = self._log_pi + self._log_B[:, observations[0]]
        for symbol in observations[1:]:
            alpha = self._log_B[:, symbol] + np.logaddexp.reduce(
                alpha[:, None] + self._log_A, axis=0
            )
        return float(np.logaddexp.reduce(alpha))

    def viterbi(self, observations):
        """Devuelve (trayectoria, log P(trayectoria, observaciones)).

        El puntaje no es la verosimilitud marginal de las observaciones. Los
        empates se resuelven por el primer índice del máximo en cada operación.
        """
        observations = self._observations(observations)
        if observations.size == 0:
            return np.empty(0, dtype=np.int64), 0.0
        predecessors = np.zeros((observations.size, self.n_states), dtype=np.int64)
        scores = self._log_pi + self._log_B[:, observations[0]]
        for t in range(1, observations.size):
            candidates = scores[:, None] + self._log_A
            predecessors[t] = np.argmax(candidates, axis=0)
            scores = self._log_B[:, observations[t]] + np.max(candidates, axis=0)
        last_state = int(np.argmax(scores))
        best_score = float(scores[last_state])
        if not np.isfinite(best_score):
            raise ValueError("La secuencia tiene probabilidad nula; no existe trayectoria de Viterbi.")
        path = np.empty(observations.size, dtype=np.int64)
        path[-1] = last_state
        for t in range(observations.size - 2, -1, -1):
            path[t] = predecessors[t + 1, path[t + 1]]
        return path, best_score

    def decode_independent(self, observations):
        """Decide argmax_i q_t(i) B_i,k, con q_t=pi A^(t−1).

        Solo usa el símbolo actual, no las otras observaciones ni estados reales.
        Las decisiones aisladas no garantizan una trayectoria conjunta posible.
        """
        observations = self._observations(observations)
        path = np.empty(observations.size, dtype=np.int64)
        prior = self._log_pi.copy()
        for t, symbol in enumerate(observations):
            weights = prior + self._log_B[:, symbol]
            if not np.any(np.isfinite(weights)):
                raise ValueError("La observación tiene probabilidad nula bajo su prior marginal.")
            path[t] = np.argmax(weights)
            prior = np.logaddexp.reduce(prior[:, None] + self._log_A, axis=0)
        return path
