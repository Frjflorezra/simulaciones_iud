"""Escenarios controlados y contrato de ejecución/exportación por consola."""

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from src.escenarios import cargar_escenarios


ROOT = Path(__file__).resolve().parents[1]


def temporary_workspace():
    """Mantiene archivos temporales de pruebas dentro del proyecto."""
    parent = (ROOT / "resultados_verificacion").resolve()
    if not parent.is_relative_to(ROOT.resolve()):
        raise ValueError("La carpeta temporal debe permanecer dentro de la actividad.")
    parent.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(prefix="test_", dir=parent)


class ScenarioTests(unittest.TestCase):
    def test_each_scenario_changes_only_its_factor(self):
        config, models = cargar_escenarios(ROOT / "configuracion/modelo_base.json")
        self.assertEqual(set(models), {"base", "mayor_persistencia", "emisiones_menos_informativas", "inicio_diferente"})
        base = models["base"]
        persistence = models["mayor_persistencia"]
        emission = models["emisiones_menos_informativas"]
        initial = models["inicio_diferente"]
        np.testing.assert_array_equal(base.A, config["A"])
        np.testing.assert_allclose(persistence.A, 0.5 * base.A + 0.5 * np.eye(3))
        np.testing.assert_array_equal(persistence.B, base.B)
        np.testing.assert_array_equal(persistence.pi, base.pi)
        np.testing.assert_allclose(emission.B, 0.7 * base.B + 0.3 / 3)
        np.testing.assert_array_equal(emission.A, base.A)
        np.testing.assert_array_equal(emission.pi, base.pi)
        np.testing.assert_array_equal(initial.pi, [0.05, 0.15, 0.80])
        np.testing.assert_array_equal(initial.A, base.A)
        np.testing.assert_array_equal(initial.B, base.B)

    def test_invalid_configuration_is_rejected(self):
        original = json.loads((ROOT / "configuracion/modelo_base.json").read_text(encoding="utf-8"))
        cases = [
            {k: v for k, v in original.items() if k != "A"},
            {**original, "estados": ["R", "M"]},
            {**original, "estados": ["R", "R", "E"]},
            {**original, "observaciones": ["baja", "media", 123]},
            {**original, "A": [[0.2, 0.2, 0.2]] * 3},
        ]
        with temporary_workspace() as directory:
            path = Path(directory) / "config.json"
            for config in cases:
                with self.subTest(config=config):
                    path.write_text(json.dumps(config), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        cargar_escenarios(path)


class CommandTests(unittest.TestCase):
    def run_command(self, output, *extra):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "main.py"), "simular",
             "--eventos", "30", "--semilla", "2026", "--salida", str(output), *extra],
            cwd=Path(output).parent, text=True, encoding="utf-8", capture_output=True,
            check=False,
        )

    def test_csv_summary_and_repetition_are_consistent(self):
        with temporary_workspace() as directory:
            outputs = [Path(directory) / name for name in ("primera", "segunda")]
            for output in outputs:
                process = self.run_command(output)
                self.assertEqual(process.returncode, 0, process.stderr)
            for filename in ("secuencia.csv", "resumen.json"):
                self.assertEqual((outputs[0] / filename).read_bytes(), (outputs[1] / filename).read_bytes())
            with (outputs[0] / "secuencia.csv").open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            summary = json.loads((outputs[0] / "resumen.json").read_text(encoding="utf-8"))
            self.assertEqual(len(rows), 30)
            self.assertEqual(summary["eventos"], 30)
            self.assertEqual(summary["semilla"], 2026)
            self.assertEqual(summary["tipo_ejecucion"], "demostracion_secuencia_unica")
            self.assertEqual(summary["generador"], "numpy.random.PCG64")
            self.assertEqual(summary["escenario"], "base")
            for decoder in ("viterbi", "independiente"):
                accuracy = sum(row["estado_real"] == row[decoder] for row in rows) / len(rows)
                self.assertAlmostEqual(summary["metricas"]["exactitud_" + decoder], accuracy)
            for t, row in enumerate(rows, start=1):
                self.assertEqual(int(row["evento"]), t)
                self.assertEqual(row["etiqueta_real"], summary["modelo"]["estados"][int(row["estado_real"])])
                self.assertEqual(row["categoria"], summary["modelo"]["observaciones"][int(row["observacion"])])
            self.assertLessEqual(summary["metricas"]["log_posterior_trayectoria_viterbi"], 1e-12)
            self.assertIn("python", summary["entorno"])
            self.assertIn("numpy", summary["entorno"])

    def test_output_directory_cannot_be_overwritten(self):
        with temporary_workspace() as directory:
            output = Path(directory) / "ejecucion"
            first = self.run_command(output)
            self.assertEqual(first.returncode, 0, first.stderr)
            previous = {p.name: p.read_bytes() for p in output.iterdir()}
            second = self.run_command(output, "--semilla", "99")
            self.assertEqual(second.returncode, 2)
            self.assertEqual(previous, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_all_scenarios_run_and_single_event_has_no_transition_rate(self):
        with temporary_workspace() as directory:
            for name in ("base", "mayor_persistencia", "emisiones_menos_informativas", "inicio_diferente"):
                with self.subTest(scenario=name):
                    output = Path(directory) / name
                    process = self.run_command(output, "--escenario", name, "--eventos", "1")
                    self.assertEqual(process.returncode, 0, process.stderr)
                    summary = json.loads((output / "resumen.json").read_text(encoding="utf-8"))
                    self.assertEqual(summary["escenario"], name)
                    self.assertIsNone(summary["metricas"]["frecuencia_cambios_estado"])

    def test_invalid_arguments_do_not_create_output(self):
        with temporary_workspace() as directory:
            for i, args in enumerate((("--eventos", "0"), ("--semilla", "-1"),
                                      ("--escenario", "inexistente"),
                                      ("--configuracion", str(Path(directory) / "ausente.json")))):
                output = Path(directory) / str(i)
                process = self.run_command(output, *args)
                self.assertEqual(process.returncode, 2, process.stderr)
                self.assertFalse(output.exists())

    def test_default_output_preserves_delivered_demonstration(self):
        with temporary_workspace() as directory:
            cwd = Path(directory)
            evidence = cwd / "resultados/demostracion"
            evidence.mkdir(parents=True)
            marker = evidence / "resumen.json"
            marker.write_text("evidencia previa", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-X", "utf8", str(ROOT / "main.py"), "simular", "--eventos", "2"],
                cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertTrue((cwd / "resultados/ejecucion/secuencia.csv").is_file())
            self.assertEqual(marker.read_text(encoding="utf-8"), "evidencia previa")


if __name__ == "__main__":
    unittest.main()
