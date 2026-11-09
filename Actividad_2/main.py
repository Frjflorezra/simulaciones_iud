"""Entrada por consola para simular y decodificar un catálogo sintético."""

import argparse
from pathlib import Path

from src.escenarios import NOMBRES_ESCENARIOS, cargar_escenarios
from src.ejecucion import ejecutar, guardar


ROOT = Path(__file__).resolve().parent


def entero_positivo(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("debe ser un entero positivo")
    return number


def entero_no_negativo(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("debe ser un entero no negativo")
    return number


def main():
    parser = argparse.ArgumentParser(description="HMM categórico para un catálogo sísmico sintético.")
    commands = parser.add_subparsers(dest="comando", required=True)
    simulate = commands.add_parser("simular", help="generar y decodificar una secuencia")
    simulate.add_argument("--eventos", type=entero_positivo, default=50)
    simulate.add_argument("--semilla", type=entero_no_negativo, default=2026)
    simulate.add_argument("--escenario", choices=NOMBRES_ESCENARIOS, default="base")
    simulate.add_argument("--configuracion", type=Path, default=ROOT / "configuracion/modelo_base.json")
    simulate.add_argument("--salida", type=Path, default=Path("resultados/ejecucion"),
                          help="carpeta nueva para secuencia.csv y resumen.json")
    args = parser.parse_args()
    try:
        configuration, scenarios = cargar_escenarios(args.configuracion)
        rows, summary = ejecutar(scenarios[args.escenario], configuration, args.escenario,
                                args.eventos, args.semilla)
        guardar(rows, summary, args.salida)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"Escenario: {args.escenario}; eventos: {args.eventos}; semilla: {args.semilla}")
    print(f"Exactitud Viterbi: {summary['metricas']['exactitud_viterbi']:.4f}")
    print(f"Exactitud independiente: {summary['metricas']['exactitud_independiente']:.4f}")
    print(f"Archivos guardados en: {args.salida}")


if __name__ == "__main__":
    main()
