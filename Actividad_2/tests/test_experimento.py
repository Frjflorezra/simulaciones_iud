import ast
import csv
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src import hmm_model as h


class TestExperimentoReproducible(unittest.TestCase):
    def test_parametros_coinciden_con_el_caso_didactico(self):
        text = (Path(__file__).resolve().parents[1] / 'materiales/caso-sismico.md').read_text(encoding='utf-8')
        values = {}
        for line in text.splitlines():
            if line.startswith(('A = ', 'B = ', 'pi = ')):
                name, literal = line.split(' = ', 1)
                values[name] = ast.literal_eval(literal)
        for actual, name in [(h.A, 'A'), (h.B, 'B'), (h.PI, 'pi')]:
            np.testing.assert_array_equal(actual, values[name])

    def test_baseline1_desempata_por_primer_estado_en_ambas_fases(self):
        path, ties = h.baseline1(h.OBS_BASE, h.B)
        np.testing.assert_array_equal(path, [0, 0, 1, 1, 2])
        self.assertEqual(ties, [2, 3])

    def test_probabilidades_del_caso_base(self):
        v, lp, _, _ = h.viterbi(h.OBS_BASE, h.A, h.B, h.PI)
        np.testing.assert_array_equal(v, [0, 0, 1, 2, 2])
        b1, _ = h.baseline1(h.OBS_BASE, h.B)
        b2 = h.baseline2(h.OBS_BASE, h.B, h.PI)
        np.testing.assert_array_equal(b2, [0, 0, 0, 0, 0])
        for path, expected in [(v, 0.000707472), (b1, 0.00058956), (b2, 0.0001303428726)]:
            self.assertAlmostEqual(np.exp(h.joint_log_prob(path, h.OBS_BASE, h.A, h.B, h.PI)), expected, places=14)
        self.assertAlmostEqual(np.exp(lp), 0.000707472, places=14)

    def test_viterbi_alcanza_el_maximo_exhaustivo(self):
        probabilities = []
        for path in itertools.product(range(3), repeat=5):
            prob = h.PI[path[0]] * h.B[path[0], h.OBS_BASE[0]]
            for t in range(1, 5):
                prob *= h.A[path[t-1], path[t]] * h.B[path[t], h.OBS_BASE[t]]
            probabilities.append(prob)
        _, lp, _, _ = h.viterbi(h.OBS_BASE, h.A, h.B, h.PI)
        self.assertAlmostEqual(np.exp(lp), max(probabilities), places=14)

    def test_monte_carlo_reproduce_la_tabla_original(self):
        results = h.monte_carlo_accuracy()
        expected = {'viterbi': (0.7262, 0.1094225430580597, 0.42, 0.94),
                    'b1': (0.6972, 0.08394418540093329, 0.48, 0.88),
                    'b2': (0.6154, 0.15183337491267768, 0.30, 0.92)}
        for key, (mean, std, minimum, maximum) in expected.items():
            values = results[key]
            self.assertEqual(len(values), 100)
            np.testing.assert_allclose([values.mean(), values.std(ddof=1), values.min(), values.max()],
                                       [mean, std, minimum, maximum], rtol=1e-12)

    def test_semilla_no_altera_el_generador_global(self):
        before = np.random.get_state()
        one = h.monte_carlo_accuracy(N_runs=3, T=10, seed=42)
        two = h.monte_carlo_accuracy(N_runs=3, T=10, seed=42)
        after = np.random.get_state()
        np.testing.assert_array_equal(before[1], after[1])
        self.assertEqual(before[2:], after[2:])
        for key in one:
            np.testing.assert_array_equal(one[key], two[key])
        self.assertGreater(len(np.unique(one['b2'])), 1)

    def test_resumen_usa_desviacion_muestral(self):
        self.assertTrue(hasattr(h, 'summarize_accuracy'), 'Falta el resumen estadístico común')
        values = np.array([0.4, 0.6, 0.8])
        stats = h.summarize_accuracy(values)
        self.assertAlmostEqual(stats['std'], 0.2)
        self.assertAlmostEqual(stats['ci95'][0], 0.6 - 1.96 * 0.2 / np.sqrt(3))
        self.assertAlmostEqual(stats['ci95'][1], 0.6 + 1.96 * 0.2 / np.sqrt(3))

    def test_exportacion_conserva_evidencia_y_es_reproducible(self):
        self.assertIsNotNone(importlib.util.find_spec('src.experimento'), 'Falta el experimento centralizado')
        from src.experimento import run_experiment, export_results
        report, records = run_experiment(N_runs=3, T=10)
        self.assertEqual(len(records), 30)
        self.assertEqual(report['configuration']['tie_break'], 'first_index')
        for key in ('viterbi', 'b1', 'b2'):
            for replica in range(3):
                rows = [r for r in records if r['replica'] == replica + 1]
                expected = np.mean([r['state'] == r[key] for r in rows])
                self.assertAlmostEqual(report['monte_carlo']['accuracy'][key][replica], expected)
        with tempfile.TemporaryDirectory() as root:
            first, second = Path(root) / 'uno', Path(root) / 'dos'
            export_results(report, records, first)
            export_results(report, records, second)
            for name in ('experimento.json', 'monte_carlo.csv', 'secuencias.csv'):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            saved = json.loads((first / 'experimento.json').read_text(encoding='utf-8'))
            self.assertEqual(saved, report)
            with (first / 'monte_carlo.csv').open(encoding='utf-8', newline='') as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 3)


if __name__ == '__main__':
    unittest.main()
