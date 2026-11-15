"""Punto de entrada: caso analítico y Monte Carlo definidos en src."""

import argparse
from pathlib import Path

from src.experimento import export_results, run_experiment


def main():
    parser = argparse.ArgumentParser(description="Reproduce el experimento HMM del artículo.")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).resolve().parent / "resultados",
                        help="Carpeta de exportación JSON y CSV.")
    args = parser.parse_args()
    report, records = run_experiment()
    print("CASO BASE: Baja, Baja, Media, Media, Alta")
    print("Desempate común: primer índice; magnitud media -> s2.")
    for name, result in report["base"]["models"].items():
        path = ", ".join(f"s{s+1}" for s in result["path"])
        print(f"{name:8s}: ({path}) | P={result['probability']:.10g} "
              f"| ln P={result['log_probability']:.4f}")
    print("\nCELOSIA: delta y psi (indices base cero)")
    for t, (delta, psi) in enumerate(zip(report["base"]["delta"], report["base"]["psi"]), 1):
        print(f"t={t}: delta={delta} | psi={psi}")
    print("\nMONTE CARLO: N=100, T=50, RandomState/MT19937, seed=42")
    print("Generacion intercalada; desviacion muestral (ddof=1).")
    for name, stats in report["monte_carlo"]["summary"].items():
        lower, upper = stats["ci95"]
        print(f"{name:8s}: media={stats['mean']*100:.2f}% | s={stats['std']:.4f} "
              f"| min={stats['min']:.2f} | max={stats['max']:.2f} "
              f"| IC95%=[{lower*100:.2f}%, {upper*100:.2f}%]")
    export_results(report, records, args.salida)
    print(f"\nResultados JSON y CSV: {args.salida}")


if __name__ == "__main__":
    main()

