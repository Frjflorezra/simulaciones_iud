"""Estudios reproducibles independientes de las decisiones adaptativas del juego."""
from collections import Counter
import csv
from html import escape
from itertools import product
import json
import math
from pathlib import Path
import platform
import random
from time import perf_counter
from yahtzee import (FAIR,LOADED,roll_single_die,score_hand,validate_probabilities,
                      PlayerState,choose_keep_mask_montecarlo,play_game)

FIXED_CATEGORIES=("threes","threeOfKind","fullHouse","chance")


def theoretical_yahtzee(probabilities):
    p=validate_probabilities(probabilities)
    return float(sum(x**5 for x in p))


def fixed_payoff(a,b,c):
    dice=[3,3,a,b,c]
    return max(score_hand(cat,dice) for cat in FIXED_CATEGORIES)


def exact_fixed_ev(probabilities=FAIR):
    p=validate_probabilities(probabilities)
    mean=second=0.
    for a,b,c in product(range(1,7),repeat=3):
        value=fixed_payoff(a,b,c); weight=p[a-1]*p[b-1]*p[c-1]
        mean+=weight*value; second+=weight*value*value
    return mean,max(0.,second-mean*mean)


def exact_risk(probabilities):
    """Solo chance libre; otras casillas en cero, incluida Yahtzee. Sin bonos."""
    p=validate_probabilities(probabilities)
    outcomes=[(18+a+b,p[a-1]*p[b-1]) for a,b in product(range(1,7),repeat=2)]
    return {"stop":21,"reroll_ev":sum(value*w for value,w in outcomes),
            "yahtzee_probability":p[5]**2,
            "lose_probability":sum(w for v,w in outcomes if v<21),
            "tie_probability":sum(w for v,w in outcomes if v==21)}


def wilson(successes,n,z=1.959963984540054):
    """Intervalo de Wilson bilateral al 95 %, válido incluso con cero éxitos."""
    if n<1 or not 0<=successes<=n: raise ValueError("Conteos inválidos.")
    phat=successes/n; den=1+z*z/n
    center=(phat+z*z/(2*n))/den
    radius=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    return max(0.,center-radius),min(1.,center+radius)


def save_csv(path,rows):
    if not rows: return
    with Path(path).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def line_svg(path,title,xs,series,ylabel,reference=None,log_x=False,xlabel="Número de muestras"):
    """Gráfico vectorial simple y portable sin dependencias de visualización."""
    width,height=860,430; left,right,top,bottom=85,35,65,85
    tx=[math.log10(x) if log_x else x for x in xs]
    ys=[v for _,values,_ in series for v in values]
    if reference is not None: ys.append(reference)
    ymin,ymax=min(ys),max(ys); pad=max((ymax-ymin)*.16,.025)
    ymin-=pad; ymax+=pad
    def px(v): return left+(v-min(tx))/(max(tx)-min(tx) or 1)*(width-left-right)
    def py(v): return height-bottom-(v-ymin)/(ymax-ymin)*(height-top-bottom)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<g font-family="Arial,sans-serif" font-size="12" fill="#26364a">',
           f'<text x="{left}" y="29" font-size="20" font-weight="bold">{escape(title)}</text>',
           f'<text x="{left}" y="49">{escape(ylabel)}</text>']
    for i in range(6):
        value=ymin+(ymax-ymin)*i/5; yy=py(value)
        parts.extend([f'<line x1="{left}" y1="{yy}" x2="{width-right}" y2="{yy}" stroke="#e2e8f0"/>',
                      f'<text x="{left-10}" y="{yy+4}" text-anchor="end">{value:.3f}</text>'])
    for x,t in zip(xs,tx):
        parts.append(f'<text x="{px(t)}" y="{height-bottom+24}" text-anchor="middle">{x:,}</text>')
    if reference is not None:
        yy=py(reference)
        parts.extend([f'<line x1="{left}" y1="{yy}" x2="{width-right}" y2="{yy}" stroke="#b65818" stroke-dasharray="6 4"/>',
                      f'<text x="{left}" y="{height-14}" fill="#b65818">Referencia exacta = {reference:.6f}</text>'])
    for j,(name,values,color) in enumerate(series):
        points=" ".join(f"{px(t):.2f},{py(v):.2f}" for t,v in zip(tx,values))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for t,v in zip(tx,values): parts.append(f'<circle cx="{px(t)}" cy="{py(v)}" r="3.5" fill="{color}"/>')
        parts.append(f'<text x="{left+250*j}" y="{height-38}" fill="{color}">{escape(name)}</text>')
    parts.append(f'<text x="{width/2}" y="{height-bottom+48}" text-anchor="middle">{escape(xlabel)}{" (escala logarítmica)" if log_x else ""}</text></g></svg>')
    Path(path).write_text("".join(parts),encoding='utf-8')


def flow_svg(path,original=False):
    labels=(["Inicio: dos jugadores y hojas vacías","Tirada inicial de cinco dados",
             "¿Quedan repeticiones? Si no, anotar","Evaluar 32 máscaras con Montecarlo",
             "Conservar máscara de mayor valor esperado","¿Conservar todos? Sí: anotar y cerrar turno",
             "Lanzar libres y volver a evaluar","Anotar categoría y avanzar jugador (26 turnos)"]
            if original else
            ["Inicio: semilla, dos jugadores, hojas vacías","Tirada inicial: cinco dados uniformes",
             "Evaluar 32 máscaras para la siguiente tirada","Elegir mayor incremento esperado de puntos",
             "Conservar todos: anotar; de lo contrario, repetir",
             "Contar solo caras nuevas; hasta tres tiradas",
             "Anotar casilla legal y aplicar bonos / Joker","Alternar jugadores; terminar tras 13 rondas"])
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="740" viewBox="0 0 820 740">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#52677c"/></marker></defs>',
       '<g font-family="Arial,sans-serif" font-size="15" fill="#15324d">',
       f'<text x="80" y="30" font-size="22" font-weight="bold">Flujo {"del código base" if original else "de la adaptación"}</text>']
    for i,label in enumerate(labels):
        yy=52+i*79
        s.extend([f'<rect x="80" y="{yy}" width="660" height="54" rx="9" fill="#eef4f8" stroke="#6c8da5"/>',
                  f'<text x="410" y="{yy+32}" text-anchor="middle">{escape(label)}</text>'])
        if i<7: s.append(f'<line x1="410" y1="{yy+54}" x2="410" y2="{yy+76}" stroke="#52677c" marker-end="url(#arrow)"/>')
    s.append('<text x="80" y="715" font-size="12">Las decisiones de repetir vuelven a la evaluación hasta agotar tiradas o plantarse.</text></g></svg>')
    Path(path).write_text("".join(s),encoding='utf-8')


def run_experiments(output_dir='resultados',n=100000,seed=42,sims_per_mask=100,benchmark=True):
    if type(n) is not int or n<1: raise ValueError("n debe ser entero positivo.")
    if type(seed) is not int: raise ValueError("Semilla entera requerida.")
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    checkpoints=sorted({k for k in [10,100,1000,5000,10000,50000,100000,n] if k<=n})
    exact,variance=exact_fixed_ev()
    rng=random.Random(seed+100); cumulative=0.; convergence=[]; t0=perf_counter()
    for i in range(1,n+1):
        cumulative+=fixed_payoff(*(roll_single_die(rng) for _ in range(3)))
        if i in checkpoints:
            ev=cumulative/i
            convergence.append({"n":i,"ev":ev,"exact_ev":exact,"absolute_error":abs(ev-exact),
                                "theoretical_se":math.sqrt(variance/i),"elapsed_s":perf_counter()-t0})
    save_csv(out/'convergencia.csv',convergence)
    distributions=[]; face_rows=[]; risk=[]
    for scenario_index,(name,probs) in enumerate([("uniforme",FAIR),("cargado",LOADED)]):
        rng=random.Random(seed+200+scenario_index); faces=Counter(); successes=0
        for _ in range(n):
            hand=[roll_single_die(rng,probs) for _ in range(5)]
            faces.update(hand); successes+=int(len(set(hand))==1)
        low,high=wilson(successes,n)
        distributions.append({"scenario":name,"n_hands":n,"yahtzees":successes,"estimate":successes/n,
                              "theory":theoretical_yahtzee(probs),"ci95_low":low,"ci95_high":high})
        face_rows.extend({"scenario":name,"face":f,"count":faces[f],"n_dice":5*n,
                          "estimate":faces[f]/(5*n),"theory":probs[f-1]} for f in range(1,7))
        rng=random.Random(seed+300+scenario_index); total=yahtzees=lose=tie=0
        for _ in range(n):
            a,b=(roll_single_die(rng,probs) for _ in range(2)); value=18+a+b
            total+=value; yahtzees+=int(a==b==6); lose+=int(value<21); tie+=int(value==21)
        reference=exact_risk(probs)
        risk.append({"scenario":name,"n":n,"stop":21,"reroll_ev_mc":total/n,
                     "reroll_ev_exact":reference["reroll_ev"],"yahtzee_mc":yahtzees/n,
                     "yahtzee_exact":reference["yahtzee_probability"],
                     "lose_mc":lose/n,"lose_exact":reference["lose_probability"],
                     "tie_mc":tie/n,"tie_exact":reference["tie_probability"]})
    save_csv(out/'dados_y_yahtzee.csv',distributions); save_csv(out/'caras.csv',face_rows)
    save_csv(out/'riesgo.csv',risk)
    budget=[]
    if benchmark:
        # Mismo estado, distinto presupuesto. No confundir con repeticiones IID.
        for sims in (10,1000,100000):
            p=PlayerState("Prueba")
            for c in p.scores:
                if c not in FIXED_CATEGORIES: p.scores[c]=0
            start=perf_counter()
            mask=choose_keep_mask_montecarlo([3,3,5,2,6],1,p,sims,random.Random(seed+400))
            budget.append({"sims_per_mask":sims,"mask":"".join(str(int(x)) for x in mask),
                           "elapsed_s":perf_counter()-start})
        save_csv(out/'presupuesto_mascaras.csv',budget)
    start=perf_counter(); game=play_game(seed,sims_per_mask)
    game_data=game.to_dict(); game_data["configuration"]={"seed":seed,"sims_per_mask":sims_per_mask,
                                                         "distribution":"uniforme","elapsed_s":perf_counter()-start}
    (out/'partida.json').write_text(json.dumps(game_data,ensure_ascii=False,indent=2),encoding='utf-8')
    save_csv(out/'marcador.csv',[{"category":c,"player_1":game.players[0].scores[c],
                                "player_2":game.players[1].scores[c]} for c in game.players[0].scores])
    results={"configuration":{"n":n,"seed":seed,"python":platform.python_version(),
                              "policy":"Montecarlo de una tirada futura, reevalúa tras tirada real",
                              "sims_per_mask_game":sims_per_mask,"uniform_probabilities":FAIR,"loaded_probabilities":LOADED,
                              "seed_offsets":{"convergence":100,"distribution":200,"risk":300,"budget":400}},
             "convergence":convergence,"fixed_ev_variance":variance,"distributions":distributions,
             "faces":face_rows,"risk":risk,"budget":budget,
             "game_summary":{"totals":[p.total for p in game.players],"winner":game_data["winner"],
                             "physical_dice":game.stats.total_rolls}}
    (out/'resultados.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    line_svg(out/'convergencia.svg',"Convergencia de un experimento fijo",
             [r["n"] for r in convergence],[("Media Montecarlo",[r["ev"] for r in convergence],"#176d8d")],
             "Mejor puntaje de cuatro categorías (puntos)",exact,True)
    line_svg(out/'error.svg',"Error observado y escala teórica",
             [r["n"] for r in convergence],
             [("Error absoluto",[r["absolute_error"] for r in convergence],"#176d8d"),
              ("Error estándar teórico",[r["theoretical_se"] for r in convergence],"#b65818")],
             "Puntos; el error de una trayectoria puede aumentar",None,True)
    line_svg(out/'caras.svg',"Distribución de caras: muestras independientes",list(range(1,7)),
             [(name,[r['estimate']*100 for r in face_rows if r['scenario']==name],color)
              for name,color in [("uniforme","#176d8d"),("cargado","#b65818")]],
             "Frecuencia relativa (%)",100/6,xlabel="Cara del dado")
    flow_svg(out/'flujo_base.svg',True); flow_svg(out/'flujo_adaptado.svg')
    return results
