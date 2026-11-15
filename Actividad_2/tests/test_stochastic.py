import unittest
import numpy as np
from src.hmm_model import A, B, PI

class TestHMMStochasticProperties(unittest.TestCase):
    def setUp(self):
        self.A = A
        self.B = B
        self.pi = PI

    def test_transition_rows_sum_to_one(self):
        row_sums = np.sum(self.A, axis=1)
        np.testing.assert_allclose(row_sums, 1.0, err_msg="Las filas de la matriz A deben sumar 1.0")

    def test_emission_rows_sum_to_one(self):
        row_sums = np.sum(self.B, axis=1)
        np.testing.assert_allclose(row_sums, 1.0, err_msg="Las filas de la matriz B deben sumar 1.0")

    def test_initial_vector_sums_to_one(self):
        pi_sum = np.sum(self.pi)
        self.assertAlmostEqual(pi_sum, 1.0, places=7, msg="El vector pi debe sumar 1.0")

    def test_probabilities_within_valid_range(self):
        self.assertTrue(np.all((self.A >= 0.0) & (self.A <= 1.0)), "Valores de A fuera de [0, 1]")
        self.assertTrue(np.all((self.B >= 0.0) & (self.B <= 1.0)), "Valores de B fuera de [0, 1]")
        self.assertTrue(np.all((self.pi >= 0.0) & (self.pi <= 1.0)), "Valores de pi fuera de [0, 1]")

if __name__ == '__main__':
    unittest.main()
