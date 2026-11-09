"""Comprobaciones del HMM con oráculos independientes de la implementación."""

import itertools
import json
import math
from pathlib import Path
import unittest

import numpy as np

from src.hmm import HMM


ROOT = Path(__file__).resolve().parents[1]


def base_model():
    config = json.loads((ROOT / "configuracion/modelo_base.json").read_text(encoding="utf-8"))
    return HMM(config["pi"], config["A"], config["B"])


def enumerate_paths(model, observations):
    """Definición conjunta explícita, sin recurrencias Forward/Viterbi."""
    result = []
    for path in itertools.product(range(model.n_states), repeat=len(observations)):
        probability = model.pi[path[0]] * model.B[path[0], observations[0]]
        for t in range(1, len(observations)):
            probability *= model.A[path[t - 1], path[t]] * model.B[path[t], observations[t]]
        result.append((path, probability))
    return result


class InferenceTests(unittest.TestCase):
    def test_analytic_example(self):
        model = base_model()
        self.assertAlmostEqual(math.exp(model.forward_log_likelihood([2, 2])), 0.008733, places=14)
        path, log_joint = model.viterbi([2, 2])
        np.testing.assert_array_equal(path, [2, 2])
        self.assertAlmostEqual(math.exp(log_joint), 0.0048, places=14)
        self.assertAlmostEqual(math.exp(log_joint - model.forward_log_likelihood([2, 2])),
                               0.0048 / 0.008733, places=14)

    def test_all_short_sequences_against_exhaustive_enumeration(self):
        model = HMM([0.35, 0.65], [[0.8, 0.2], [0.3, 0.7]],
                    [[0.15, 0.6, 0.25], [0.7, 0.2, 0.1]])
        for length in range(1, 5):
            for observations in itertools.product(range(3), repeat=length):
                with self.subTest(observations=observations):
                    oracle = enumerate_paths(model, observations)
                    expected_total = math.fsum(float(p) for _, p in oracle)
                    expected_best = max(p for _, p in oracle)
                    self.assertAlmostEqual(model.forward_log_likelihood(observations),
                                           math.log(expected_total), places=12)
                    path, score = model.viterbi(observations)
                    self.assertAlmostEqual(score, math.log(expected_best), places=12)
                    actual = dict(oracle)[tuple(path)]
                    self.assertAlmostEqual(float(actual), float(expected_best), places=14)

    def test_marginal_decoder_uses_initial_and_time_dependent_prior(self):
        model = base_model()
        np.testing.assert_array_equal(model.decode_independent([2, 2]), [0, 2])
        # Cambiar otra observación no debe cambiar la decisión del evento actual.
        for prefix in ([0, 0], [1, 2], [2, 1]):
            expected = model.decode_independent([*prefix, 2])[2]
            self.assertEqual(expected, model.decode_independent([2, 2, 2])[2])

    def test_long_sequence_does_not_underflow(self):
        model = HMM([1.0], [[1.0]], [[1e-250, 1.0]])
        observations = np.zeros(2000, dtype=int)
        expected = len(observations) * math.log(1e-250)
        score = model.forward_log_likelihood(observations)
        self.assertTrue(math.isfinite(score))
        self.assertAlmostEqual(score / len(observations), expected / len(observations), places=9)
        path, best_score = model.viterbi(observations)
        np.testing.assert_array_equal(path, observations)
        self.assertAlmostEqual(best_score / len(observations), expected / len(observations), places=9)

    def test_impossible_sequence_has_no_viterbi_path(self):
        model = HMM([0.5, 0.5], [[1, 0], [0, 1]], [[1, 0], [0, 1]])
        self.assertEqual(model.forward_log_likelihood([0, 1]), -math.inf)
        with self.assertRaisesRegex(ValueError, "probabilidad nula"):
            model.viterbi([0, 1])

    def test_zero_probability_symbol_is_rejected_by_decoders(self):
        model = HMM([1], [[1]], [[1, 0]])
        self.assertEqual(model.forward_log_likelihood([1]), -math.inf)
        with self.assertRaisesRegex(ValueError, "probabilidad nula"):
            model.decode_independent([1])
        with self.assertRaisesRegex(ValueError, "probabilidad nula"):
            model.viterbi([1])

    def test_empty_sequence_and_deterministic_ties(self):
        model = HMM([0.5, 0.5], [[0.5, 0.5], [0.5, 0.5]], [[0.5, 0.5], [0.5, 0.5]])
        self.assertEqual(model.forward_log_likelihood([]), 0.0)
        path, score = model.viterbi([])
        self.assertEqual(len(path), 0)
        self.assertEqual(score, 0.0)
        self.assertEqual(len(model.decode_independent([])), 0)
        np.testing.assert_array_equal(model.viterbi([0, 0, 0])[0], [0, 0, 0])


class SamplingTests(unittest.TestCase):
    def test_initial_emission_precedes_first_transition(self):
        model = HMM([1, 0], [[0, 1], [0, 1]], [[1, 0], [0, 1]])
        states, observations = model.sample(5, np.random.Generator(np.random.PCG64(9)))
        np.testing.assert_array_equal(states, [0, 1, 1, 1, 1])
        np.testing.assert_array_equal(observations, states)

    def test_reproducible_local_random_stream(self):
        model = base_model()
        before = np.random.get_state()
        first = model.sample(100, np.random.Generator(np.random.PCG64(2026)))
        second = model.sample(100, np.random.Generator(np.random.PCG64(2026)))
        after = np.random.get_state()
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a, b)
        self.assertEqual(before[0], after[0])
        np.testing.assert_array_equal(before[1], after[1])
        self.assertEqual(before[2:], after[2:])

    def test_categorical_sampling_frequencies(self):
        model = HMM([1], [[1]], [[0.2, 0.3, 0.5]])
        states, observations = model.sample(30000, np.random.Generator(np.random.PCG64(17)))
        np.testing.assert_array_equal(states, np.zeros(30000, dtype=int))
        np.testing.assert_allclose(np.bincount(observations, minlength=3) / len(observations),
                                   [0.2, 0.3, 0.5], rtol=0, atol=0.01)


class ValidationTests(unittest.TestCase):
    def test_invalid_probabilities_and_dimensions(self):
        cases = [
            ([0.2, 0.2], [[1, 0], [0, 1]], [[1], [1]]),
            ([1], [[-0.1]], [[1]]),
            ([1], [[math.nan]], [[1]]),
            ([1], [[1]], [[math.inf]]),
            ([1], [[1, 0]], [[1]]),
            ([0.5, 0.5], [[1, 0], [0, 1]], [[1]]),
            ([[1]], [[1]], [[1]]),
            ([], [], []),
            ([1], [[1]], [[]]),
        ]
        for pi, A, B in cases:
            with self.subTest(pi=pi, A=A, B=B), self.assertRaises(ValueError):
                HMM(pi, A, B)

    def test_invalid_observation_indices(self):
        model = base_model()
        for observations in ([-1], [3], [0.5], [1.0], [True], [0, True],
                             [np.bool_(False), 1], [[0, 1]], ["1"]):
            for method in (model.forward_log_likelihood, model.viterbi, model.decode_independent):
                with self.subTest(observations=observations, method=method.__name__), self.assertRaises(ValueError):
                    method(observations)

    def test_parameters_are_copied_and_read_only(self):
        pi = np.array([0.4, 0.6])
        model = HMM(pi, [[1, 0], [0, 1]], [[1], [1]])
        pi[0] = 0.9
        np.testing.assert_array_equal(model.pi, [0.4, 0.6])
        for array in (model.pi, model.A, model.B):
            with self.assertRaises(ValueError):
                array.flat[0] = 0

    def test_sample_requires_positive_integer_length_and_explicit_generator(self):
        model = base_model()
        for length in (0, -1, 1.5, True):
            with self.subTest(length=length), self.assertRaises(ValueError):
                model.sample(length, np.random.Generator(np.random.PCG64(1)))
        with self.assertRaises(TypeError):
            model.sample(2, 123)


if __name__ == "__main__":
    unittest.main()
