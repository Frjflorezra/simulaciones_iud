"""Entrada del proyecto: python main.py jugar / experimentos."""
import argparse
import json
from pathlib import Path
from yahtzee import play_game,print_scoreboard
from experimentos import run_experiments

def main():
    parser=argparse.ArgumentParser(description="Yahtzee y Montecarlo: USA, MODIFICA y CREA")
    parser.add_argument("accion",choices=["jugar","experimentos"])
    parser.add_argument("--semilla",type=int,default=42)
    parser.add_argument("--simulaciones",type=int,default=100,help="Simulaciones por máscara de la IA")
    parser.add_argument("--n",type=int,default=100000,help="Muestras por experimento estadístico")
    parser.add_argument("--salida",default="resultados")
    parser.add_argument("--detalle",action="store_true")
    parser.add_argument("--sin-comparar-presupuestos",action="store_true",help="Omite comparación costosa de 32 máscaras")
    args=parser.parse_args()
    if args.simulaciones<1 or args.n<1: parser.error("Los tamaños de muestra deben ser positivos.")
    if args.accion=="jugar":
        state=play_game(args.semilla,args.simulaciones,verbose_each_turn=args.detalle)
        print_scoreboard(state)
        out=Path(args.salida); out.mkdir(parents=True,exist_ok=True)
        (out/"partida_manual.json").write_text(json.dumps(state.to_dict(),ensure_ascii=False,indent=2),encoding="utf-8")
    else:
        print("Ejecutando estudios y comparación de presupuestos; puede tardar unos minutos.")
        data=run_experiments(args.salida,args.n,args.semilla,args.simulaciones,not args.sin_comparar_presupuestos)
        print(json.dumps({"partida":data["game_summary"],"convergencia":data["convergence"],
                          "dados":data["distributions"],"riesgo":data["risk"]},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
