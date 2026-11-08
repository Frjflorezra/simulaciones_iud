"""Adaptación del motor de simulacion_01.ipynb (material del profesor).

Conserva categorías, estructuras y búsqueda de máscaras. Cambios documentados
en docs/MODIFICACIONES.md. La política Montecarlo mira UNA tirada futura;
no es una solución óptima de todos los turnos de la partida.
"""
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
import math
import random

CATEGORIES_ORDER = [
    "ones","twos","threes","fours","fives","sixes",
    "threeOfKind","fourOfKind","fullHouse","smallStraight",
    "largeStraight","yahtzee","chance"
]
LABELS = ["Unos","Doses","Treses","Cuatros","Cincos","Seises",
          "Trío","Póquer","Full","Escalera corta","Escalera larga","Yahtzee","Libre"]
FAIR = (1/6,)*6
LOADED = (.14,.14,.14,.14,.14,.30)


def validate_probabilities(probabilities):
    p=tuple(probabilities)
    if len(p)!=6 or any(not math.isfinite(x) or x<0 for x in p) or not math.isclose(sum(p),1,abs_tol=1e-12):
        raise ValueError("Se requieren seis probabilidades no negativas que sumen 1.")
    return p


def validate_dice(dice):
    if len(dice)!=5 or any(type(d) is not int or not 1<=d<=6 for d in dice):
        raise ValueError("La mano debe contener cinco enteros entre 1 y 6.")


def roll_single_die(rng, probabilities=FAIR):
    """Muestreo uniforme o por distribución acumulada (parámetro validado al entrar)."""
    if probabilities==FAIR:
        return rng.randint(1,6)
    u=rng.random(); cumulative=0.
    for face,p in enumerate(probabilities,1):
        cumulative+=p
        if u<cumulative: return face
    return 6  # Protección frente a redondeo en la suma acumulada.


def roll_dice(values, locked, rng, probabilities=FAIR):
    """Actualiza solo dados libres y devuelve únicamente las caras NUEVAS."""
    if len(values)!=5 or len(locked)!=5:
        raise ValueError("Se requieren cinco dados y cinco bloqueos.")
    new_faces=[]
    for i,keep in enumerate(locked):
        if not keep:
            values[i]=roll_single_die(rng,probabilities)
            new_faces.append(values[i])
    return new_faces


def has_sequence(values, needed_len):
    faces=set(values)
    return any(set(range(start,start+needed_len))<=faces for start in range(1,8-needed_len))


@lru_cache(maxsize=252)
def _scores(sorted_dice):
    """Solo hay C(10,5)=252 multiconjuntos de cinco dados."""
    counts=Counter(sorted_dice); freqs=counts.values(); total=sum(sorted_dice)
    return tuple(counts.get(i,0)*i for i in range(1,7)) + (
        total if max(freqs)>=3 else 0,
        total if max(freqs)>=4 else 0,
        25 if sorted(freqs)==[2,3] else 0,
        30 if has_sequence(sorted_dice,4) else 0,
        40 if has_sequence(sorted_dice,5) else 0,
        50 if len(counts)==1 else 0, total)


def score_hand(category,dice):
    """Puntos de una categoría aislada, sin bono ni Joker."""
    validate_dice(dice)
    if category not in CATEGORIES_ORDER: raise ValueError("Categoría desconocida.")
    return _scores(tuple(sorted(dice)))[CATEGORIES_ORDER.index(category)]


def best_category_score(dice,available):
    if not available: raise ValueError("No hay categorías disponibles.")
    return max(((cat,score_hand(cat,dice)) for cat in available),key=lambda x:x[1])


@dataclass
class PlayerState:
    name: str
    scores: dict=field(default_factory=lambda:{c:None for c in CATEGORIES_ORDER})
    yahtzee_bonus: int=0

    @property
    def upper_subtotal(self):
        return sum(self.scores[c] or 0 for c in CATEGORIES_ORDER[:6])

    @property
    def upper_bonus(self):
        return 35 if self.upper_subtotal>=63 else 0

    @property
    def total(self):
        return sum(v or 0 for v in self.scores.values())+self.upper_bonus+self.yahtzee_bonus

    def available_categories(self):
        return [c for c in CATEGORIES_ORDER if self.scores[c] is None]

    def legal_categories(self,dice):
        """Prioridad Joker de Hasbro, incluso cuando la casilla Yahtzee vale cero."""
        available=self.available_categories()
        if len(set(dice))==1 and self.scores["yahtzee"] is not None:
            upper=CATEGORIES_ORDER[dice[0]-1]
            if upper in available: return [upper]
            lower=[c for c in available if c in CATEGORIES_ORDER[6:]]
            return lower or available
        return available

    def options(self,dice):
        """(categoría, puntos de casilla, incremento total), para decisiones."""
        raw=_scores(tuple(sorted(dice)))
        repeated=len(set(dice))==1 and self.scores["yahtzee"] is not None
        extra=100 if repeated and self.scores["yahtzee"]==50 else 0
        choices=[]
        for cat in self.legal_categories(dice):
            index=CATEGORIES_ORDER.index(cat); points=raw[index]
            if repeated and cat in ("fullHouse","smallStraight","largeStraight"):
                points={"fullHouse":25,"smallStraight":30,"largeStraight":40}[cat]
            upper_delta=35 if index<6 and self.upper_subtotal<63<=self.upper_subtotal+points else 0
            choices.append((cat,points,points+extra+upper_delta))
        return choices

    def record_hand(self,category,dice):
        validate_dice(dice)
        options={c:(points,delta) for c,points,delta in self.options(dice)}
        if category not in options: raise ValueError("Casilla usada o no permitida por Joker.")
        points,_=options[category]
        if len(set(dice))==1 and self.scores["yahtzee"]==50:
            self.yahtzee_bonus+=100
        self.scores[category]=points
        return points


@dataclass
class GameStats:
    total_rolls: int=0  # Dados individuales nuevos, no manos observadas.
    face_hist: Counter=field(default_factory=Counter)

    def update_from_roll(self,new_faces):
        self.total_rolls+=len(new_faces)
        self.face_hist.update(new_faces)


@dataclass
class GameState:
    players: list
    dice_rng: random.Random
    mc_rng: random.Random
    stats: GameStats=field(default_factory=GameStats)
    turns: list=field(default_factory=list)

    @classmethod
    def create(cls,seed=42):
        return cls([PlayerState("Jugador 1"),PlayerState("Jugador 2")],
                   random.Random(seed),random.Random(seed+1))

    def to_dict(self):
        totals=[p.total for p in self.players]
        winner="Empate" if totals[0]==totals[1] else self.players[totals.index(max(totals))].name
        return {"players":[{"name":p.name,"scores":p.scores.copy(),
                            "upper_subtotal":p.upper_subtotal,"upper_bonus":p.upper_bonus,
                            "yahtzee_bonus":p.yahtzee_bonus,"total":p.total} for p in self.players],
                "winner":winner,"physical_dice":self.stats.total_rolls,
                "face_hist":dict(sorted(self.stats.face_hist.items())),"turns":self.turns}


def all_keep_masks():
    return [[bool((m>>i)&1) for i in range(5)] for m in range(32)]


def simulate_expected_value_after_keeps(current_values,keep_mask,rolls_remaining,
                                        player,sims,rng,probabilities=FAIR):
    """EV de la SIGUIENTE tirada. No se resta uno a rolls_remaining.

    El límite de un paso es intencional: la decisión se recalcula después de
    cada tirada real. Las opciones valoran puntos inmediatos y bonos activados.
    """
    if sims<1: raise ValueError("Las simulaciones deben ser positivas.")
    if len(keep_mask)!=5: raise ValueError("Máscara de longitud cinco requerida.")
    if rolls_remaining<=0 or all(keep_mask):
        return float(max(option[2] for option in player.options(current_values)))
    total=0.
    for _ in range(sims):
        future=current_values[:]
        roll_dice(future,keep_mask,rng,probabilities)
        total+=max(option[2] for option in player.options(future))
    return total/sims


def choose_keep_mask_montecarlo(current_values,rolls_remaining,player,sims_per_mask,rng,probabilities=FAIR):
    validate_dice(current_values)
    if sims_per_mask<1: raise ValueError("Las simulaciones deben ser positivas.")
    if rolls_remaining<=0: return [True]*5
    # En empate exacto se conservan más dados. "Plantarse" no requiere muestreo.
    best_mask=[True]*5
    best_ev=simulate_expected_value_after_keeps(current_values,best_mask,0,player,sims_per_mask,rng,probabilities)
    for mask in all_keep_masks():
        if all(mask): continue
        ev=simulate_expected_value_after_keeps(current_values,mask,rolls_remaining,player,sims_per_mask,rng,probabilities)
        if ev>best_ev or (ev==best_ev and sum(mask)>sum(best_mask)):
            best_mask,best_ev=mask,ev
    return best_mask


def play_one_turn(state,player,round_number,sims_per_mask=100,probabilities=FAIR,verbose=False):
    dice=[0]*5; mask=[False]*5; history=[]
    for roll_index in range(3):
        if roll_index:
            mask=choose_keep_mask_montecarlo(dice,3-roll_index,player,sims_per_mask,state.mc_rng,probabilities)
            if all(mask): break
        new=roll_dice(dice,mask,state.dice_rng,probabilities)
        state.stats.update_from_roll(new)
        history.append({"dice":dice[:],"kept":mask[:],"new_faces":new})
        if verbose: print(f"{player.name} | ronda {round_number} | tirada {roll_index+1}: {dice}")
    cat,points,delta=max(player.options(dice),key=lambda x:x[2])
    player.record_hand(cat,dice)
    state.turns.append({"round":round_number,"player":player.name,"rolls":history,
                        "category":cat,"points":points,"total_increment":delta,"total":player.total})
    if verbose: print(f"  Anota {cat}: {points}; total con bonos: {player.total}")


def play_game(seed=42,sims_per_mask=100,probabilities=FAIR,verbose_each_turn=False):
    """Dos jugadores automáticos. Una casilla por turno, 26 turnos en total."""
    if type(seed) is not int: raise ValueError("La semilla debe ser un entero.")
    if type(sims_per_mask) is not int or sims_per_mask<1: raise ValueError("Presupuesto MC entero positivo requerido.")
    probabilities=validate_probabilities(probabilities)
    state=GameState.create(seed)
    for round_number in range(1,14):
        for player in state.players:
            play_one_turn(state,player,round_number,sims_per_mask,probabilities,verbose_each_turn)
    return state


def print_scoreboard(state):
    print(f"{'Categoría':20s} {'Jugador 1':>10s} {'Jugador 2':>10s}")
    for cat,label in zip(CATEGORIES_ORDER,LABELS):
        print(f"{label:20s} {state.players[0].scores[cat]:10d} {state.players[1].scores[cat]:10d}")
    for label,attr in [("Bono superior","upper_bonus"),("Bonos Yahtzee","yahtzee_bonus"),("TOTAL","total")]:
        print(f"{label:20s} {getattr(state.players[0],attr):10d} {getattr(state.players[1],attr):10d}")
    print("Ganador:",state.to_dict()["winner"])
    print("Dados individuales nuevos:",state.stats.total_rolls)
