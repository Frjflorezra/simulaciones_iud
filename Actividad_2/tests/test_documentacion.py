"""Comprobaciones de las cifras publicadas frente al experimento ejecutable."""

from pathlib import Path
import re
import unittest

import numpy as np

from src.experimento import run_experiment
from src import hmm_model as h

ROOT = Path(__file__).resolve().parents[1]


class TestCoherenciaDocumental(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, _ = run_experiment()
        cls.md = (ROOT / 'anteproyecto_hmm_sismico.md').read_text(encoding='utf-8')
        cls.tex = (ROOT / 'main.tex').read_text(encoding='utf-8')

    def test_matrices_de_ambos_manuscritos(self):
        for text in (self.md, self.tex):
            for name, expected in [('A', h.A), ('B', h.B)]:
                block = re.search(name + r' = \\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', text, re.S)
                self.assertIsNotNone(block)
                values = [float(x) for x in re.findall(r'\d+\.\d+', block.group(1))]
                np.testing.assert_array_equal(np.array(values).reshape(3, 3), expected)

    def test_tablas_analiticas_coinciden(self):
        md = self.md.split('Tabla 2:', 1)[1].split('### 5.2.', 1)[0]
        tex = self.tex.split(r'\label{tab:comparacion_secuencia}', 1)[1].split(r'\end{table}', 1)[0]
        for key, label in [('viterbi', 'Algoritmo de Viterbi'), ('b1', 'Baseline 1'), ('b2', 'Baseline 2')]:
            expected = f"{self.report['base']['models'][key]['log_probability']:.4f}"
            for block in (md, tex):
                row = next(line for line in block.splitlines() if label in line)
                self.assertIn(expected, row)

    def test_tablas_monte_carlo_coinciden(self):
        md = self.md.split('Tabla 3:', 1)[1].split('### 5.3.', 1)[0]
        tex = self.tex.split(r'\label{tab:monte_carlo}', 1)[1].split(r'\end{table}', 1)[0]
        for key, label in [('viterbi', 'Algoritmo de Viterbi'), ('b1', 'Baseline 1'), ('b2', 'Baseline 2')]:
            stats = self.report['monte_carlo']['summary'][key]
            values = [stats[k] for k in ('mean', 'std', 'min', 'max')] + stats['ci95']
            for block in (md, tex):
                row = next(line for line in block.splitlines() if label in line)
                for value in values:
                    self.assertIn(f'{value:.4f}', row)

    def test_no_se_publican_valores_p_no_calculados(self):
        for text in (self.md, self.tex):
            self.assertNotIn('p < 0.05', text)
            self.assertNotIn('0.0012245', text)
            self.assertNotIn('-7.5415', text)


if __name__ == '__main__':
    unittest.main()
