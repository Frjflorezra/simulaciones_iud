"""
generar_figuras.py — Genera las 4 figuras científicas del artículo HMM Sísmico.

Figuras producidas (en figures/):
  fig1_matrices_hmm.png       — Visualización de A, B y π como mapas de calor
  fig2_celosia_viterbi.png    — Celosía δ_t y trayectorias comparadas (T=5)
  fig3_comparacion_logp.png   — Puntos de log-verosimilitud conjunta (T=5)
  fig4_monte_carlo_boxplot.png— Distribución de precisión en 100 réplicas MC

Autor: Francisco Javier Florez Ramirez
Curso de Simulación — IU Digital de Antioquia
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# ── Importar núcleo del modelo ────────────────────────────────────────────────
from src.hmm_model import (
    A, B, PI, OBS_BASE, STATES, OBS_LABELS, STATE_SHORT,
    verify_model, viterbi, baseline1, baseline2,
    joint_log_prob, monte_carlo_accuracy, summarize_accuracy
)

FIGDIR = "figures"
os.makedirs(FIGDIR, exist_ok=True)

# Paleta institucional / científica
CMAP_MAT  = "YlOrRd"
C_VIT     = "#1a6faf"   # azul Viterbi
C_B1      = "#e07b39"   # naranja Baseline 1
C_B2      = "#c0392b"   # rojo Baseline 2
FONTSIZE  = 11

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": FONTSIZE + 1,
    "axes.labelsize": FONTSIZE,
    "xtick.labelsize": FONTSIZE - 1,
    "ytick.labelsize": FONTSIZE - 1,
    "legend.fontsize": FONTSIZE - 1,
    "figure.dpi": 150,
})

verify_model(A, B, PI)

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURA 1 — Matrices del modelo λ = (A, B, π)
# ═══════════════════════════════════════════════════════════════════════════════
print("[fig1] Generando mapa de calor de matrices del modelo...")

fig1, axes = plt.subplots(1, 3, figsize=(14, 4.2))
fig1.suptitle("Figura 1. Parámetros del Modelo HMM: Matrices $A$, $B$ y Vector $\\pi$",
              fontsize=FONTSIZE + 2, fontweight="bold", y=1.01)

state_names = ["$s_1$\nReposo", "$s_2$\nAct.\nMenor", "$s_3$\nEnjambre"]
obs_names   = ["$v_1$\nBaja", "$v_2$\nMedia", "$v_3$\nAlta"]

# A — Transición
im0 = axes[0].imshow(A, cmap=CMAP_MAT, vmin=0, vmax=1, aspect="auto")
axes[0].set_title("Matriz de Transición $A$\n$a_{ij} = P(S_t=s_j \\mid S_{t-1}=s_i)$")
axes[0].set_xticks(range(3)); axes[0].set_xticklabels(state_names)
axes[0].set_yticks(range(3)); axes[0].set_yticklabels(state_names)
axes[0].set_xlabel("Estado siguiente $s_j$")
axes[0].set_ylabel("Estado actual $s_i$")
for i in range(3):
    for j in range(3):
        axes[0].text(j, i, f"{A[i,j]:.2f}", ha="center", va="center",
                     fontsize=12, fontweight="bold",
                     color="white" if A[i,j] > 0.6 else "black")
plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Probabilidad")

# B — Emisión
im1 = axes[1].imshow(B, cmap=CMAP_MAT, vmin=0, vmax=1, aspect="auto")
axes[1].set_title("Matriz de Emisión $B$\n$b_j(k) = P(O_t=v_k \\mid S_t=s_j)$")
axes[1].set_xticks(range(3)); axes[1].set_xticklabels(obs_names)
axes[1].set_yticks(range(3)); axes[1].set_yticklabels(state_names)
axes[1].set_xlabel("Observación $v_k$")
axes[1].set_ylabel("Estado $s_j$")
for i in range(3):
    for j in range(3):
        axes[1].text(j, i, f"{B[i,j]:.2f}", ha="center", va="center",
                     fontsize=12, fontweight="bold",
                     color="white" if B[i,j] > 0.5 else "black")
plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04, label="Probabilidad")

# π — Prior
axes[2].bar(range(3), PI, color=[C_VIT, C_B1, C_B2], edgecolor="black", linewidth=0.8, width=0.5)
axes[2].set_title("Distribución Inicial $\\pi$\n$\\pi_i = P(S_1 = s_i)$")
axes[2].set_xticks(range(3)); axes[2].set_xticklabels(state_names)
axes[2].set_ylabel("Probabilidad")
axes[2].set_ylim(0, 1.0)
axes[2].axhline(1.0, color="gray", linestyle="--", linewidth=0.7, alpha=0.5)
for i, v in enumerate(PI):
    axes[2].text(i, v + 0.03, f"{v:.2f}", ha="center", va="bottom",
                 fontsize=12, fontweight="bold")

fig1.tight_layout()
path1 = os.path.join(FIGDIR, "fig1_matrices_hmm.png")
fig1.savefig(path1, bbox_inches="tight")
print(f"Guardada: {path1}")
plt.close(fig1)



# Las figuras de resultados consumen las funciones originales sin alterar
# parámetros, trayectorias, réplicas ni la fórmula de intervalos existente.
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle

MODEL_NAMES = ["Viterbi (HMM)", "Baseline 1 · Máxima emisión",
               "Baseline 2 · Bayesiano estático"]
MODEL_COLORS = [C_VIT, C_B1, C_B2]
INK, MUTED, GRID = "#172b3a", "#526575", "#dce4ea"

obs_seq = OBS_BASE
vit_path, vit_lp, delta, psi = viterbi(obs_seq, A, B, PI)
b1_path, ties = baseline1(obs_seq, B)
b2_path = baseline2(obs_seq, B, PI)
paths = [vit_path, b1_path, b2_path]
T_case = len(obs_seq)
t_axis = np.arange(1, T_case + 1)
obs_names_case = ["Baja", "Media", "Alta"]


def finish(fig, filename):
    """Guarda únicamente el recurso gráfico; no modifica el manuscrito."""
    fig.savefig(os.path.join(FIGDIR, filename), dpi=300,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Guardada: {filename}")


def clean_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED)


# FIGURA 2 — La celosía muestra los predecesores que devuelve psi.
# Las flechas azules corresponden al retroceso de la trayectoria óptima.
fig2 = plt.figure(figsize=(12.2, 8.8), layout="constrained")
gs2 = fig2.add_gridspec(2, 1, height_ratios=[1.8, 1], hspace=0.15)
ax_tree = fig2.add_subplot(gs2[0])
ax_paths = fig2.add_subplot(gs2[1])
fig2.suptitle("Figura 2. Cómo Viterbi reconstruye la secuencia de estados",
              fontsize=15, fontweight="bold", color=INK)
ax_tree.set_title("A  ·  Celosía de probabilidades y enlaces de retroceso",
                  loc="left", fontsize=12, color=INK, pad=18)

for t in range(1, T_case):
    for j in range(len(PI)):
        if delta[t, j] == 0:
            continue
        previous = psi[t, j]
        chosen = vit_path[t] == j and vit_path[t - 1] == previous
        ax_tree.annotate(
            "", xy=(t + 1 - 0.34, 2 - j),
            xytext=(t + 0.34, 2 - previous),
            arrowprops=dict(arrowstyle="-|>", color=C_VIT if chosen else "#bdc9d2",
                            lw=2.6 if chosen else 1.0,
                            mutation_scale=13 if chosen else 10),
            zorder=2 if chosen else 1)

for t in range(T_case):
    for j in range(len(PI)):
        chosen = vit_path[t] == j
        y = 2 - j
        box = FancyBboxPatch(
            (t + 1 - 0.32, y - 0.19), 0.64, 0.38,
            boxstyle="round,pad=0.025,rounding_size=0.04",
            facecolor=C_VIT if chosen else "#f3f6f8",
            edgecolor=C_VIT if chosen else "#c7d1d9",
            linewidth=1.5 if chosen else 0.9, zorder=3)
        ax_tree.add_patch(box)
        value = delta[t, j]
        label = "0" if value == 0 else f"{value:.3g}"
        ax_tree.text(t + 1, y, f"$s_{j+1}$\nδ = {label}",
                     ha="center", va="center", fontsize=9,
                     color="white" if chosen else INK, zorder=4)

ax_tree.set_xlim(0.35, T_case + 0.65)
ax_tree.set_ylim(-0.5, 2.75)
ax_tree.set_xticks(t_axis)
ax_tree.set_xticklabels(
    [f"t = {t}\n{obs_names_case[obs_seq[t-1]]}" for t in t_axis],
    fontsize=10, color=INK)
ax_tree.set_yticks([2, 1, 0])
ax_tree.set_yticklabels(["Reposo · s₁", "Act. menor · s₂", "Enjambre · s₃"],
                        color=INK, fontsize=10)
ax_tree.tick_params(length=0, pad=10)
for spine in ax_tree.spines.values():
    spine.set_visible(False)
ax_tree.legend(
    handles=[Line2D([0], [0], color=C_VIT, lw=2.8, label="Trayectoria óptima"),
             Line2D([0], [0], color="#bdc9d2", lw=1.2,
                    label="Otros predecesores seleccionados por ψ")],
    loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=2,
    frameon=False, fontsize=9)

# Una fila por método evita que trayectorias coincidentes se oculten entre sí.
ax_paths.set_title("B  ·  Estados inferidos ante las mismas observaciones",
                   loc="left", fontsize=12, color=INK, pad=22)
for row, (path, color) in enumerate(zip(paths, MODEL_COLORS)):
    for t, state in enumerate(path):
        ax_paths.add_patch(Rectangle(
            (t + 0.57, row - 0.32), 0.86, 0.64,
            facecolor=color, alpha=0.09, edgecolor="none"))
        ax_paths.text(t + 1, row, f"$s_{state+1}$",
                      ha="center", va="center", fontsize=15,
                      fontweight="bold", color=color)
        if row == 1 and t in ties:
            ax_paths.add_patch(Rectangle(
                (t + 0.57, row - 0.32), 0.86, 0.64,
                facecolor="none", edgecolor=C_B1, lw=1.5, linestyle="--"))
for t in t_axis:
    ax_paths.text(t, -0.62, f"t = {t}", ha="center",
                  color=MUTED, fontsize=10)
ax_paths.set_xlim(0.35, T_case + 0.65)
ax_paths.set_ylim(2.8, -0.9)
ax_paths.set_yticks(range(3))
ax_paths.set_yticklabels(MODEL_NAMES, fontsize=10, color=INK)
ax_paths.set_xticks([])
ax_paths.tick_params(length=0, pad=10)
for spine in ax_paths.spines.values():
    spine.set_visible(False)
ax_paths.text(0.5, -0.08,
              "s₁: Reposo   ·   s₂: Actividad menor   ·   s₃: Enjambre\n"
              "Recuadros discontinuos: empate de B1 resuelto por primer índice, hacia s₂.",
              transform=ax_paths.transAxes, ha="center", va="top",
              color=MUTED, fontsize=9, linespacing=1.6)
finish(fig2, "fig2_celosia_viterbi.png")


# FIGURA 3 — Valores calculados por la misma función joint_log_prob.
lp_vals = [joint_log_prob(path, obs_seq, A, B, PI) for path in paths]
fig3, ax3 = plt.subplots(figsize=(10.8, 5.5))
fig3.subplots_adjust(left=0.30, right=0.96, bottom=0.23, top=0.78)
fig3.suptitle("Figura 3. Comparación de log-verosimilitud conjunta",
              fontsize=15, fontweight="bold", color=INK)
ax3.set_title("Secuencia base de cinco observaciones · Mayor valor hacia la derecha",
               fontsize=11, color=MUTED, pad=20)
left, right = min(lp_vals) - 0.35, max(lp_vals) + 0.35
for row, (value, path, color) in enumerate(zip(lp_vals, paths, MODEL_COLORS)):
    ax3.hlines(row, left, right, color=GRID, lw=0.8, zorder=0)
    ax3.scatter(value, row, s=120, color=color, edgecolor="white",
                linewidth=1.2, zorder=3)
    ax3.annotate(f"{value:.4f}", (value, row),
                 xytext=(0, 15), textcoords="offset points",
                 ha="center", color=color, fontsize=12, fontweight="bold")
    trajectory = " → ".join(f"s{state+1}" for state in path)
    ax3.text(left + 0.02, row + 0.19, trajectory,
              color=MUTED, fontsize=9, ha="left", va="top")
ax3.axvline(lp_vals[0], color=C_VIT, linestyle="--", lw=1.1, alpha=0.65)
ax3.set_xlim(left, right)
ax3.set_ylim(2.55, -0.6)
ax3.set_yticks(range(3))
ax3.set_yticklabels(MODEL_NAMES, fontsize=10)
ax3.set_xlabel(r"Log-verosimilitud conjunta  $\ln P(\mathcal{O}, \hat{S}\mid\lambda)$",
                labelpad=14, color=INK)
ax3.grid(axis="x", color=GRID, alpha=0.55)
clean_axis(ax3)
fig3.text(0.5, 0.025,
           "B1: empate en t = 3 y t = 4; selección convencional de s₂. "
           "Resultados del modelo implementado.",
           ha="center", va="bottom", fontsize=9, color=MUTED)
finish(fig3, "fig3_comparacion_logp.png")


# FIGURA 4 — Resumen estadístico común al experimento y al manuscrito.
mc = monte_carlo_accuracy(N_runs=100, T=50, seed=42)
arrays = [mc["viterbi"], mc["b1"], mc["b2"]]


def ci95(arr):
    stats = summarize_accuracy(arr)
    return stats["ci95"][1] - stats["mean"]


means = [arr.mean() * 100 for arr in arrays]
errors = [ci95(arr) * 100 for arr in arrays]
fig4, (ax4a, ax4b) = plt.subplots(
    1, 2, figsize=(12, 5.8),
    gridspec_kw={"width_ratios": [1.1, 1]})
fig4.subplots_adjust(left=0.075, right=0.985, bottom=0.24, top=0.79, wspace=0.34)
fig4.suptitle("Figura 4. Precisión de decodificación en simulación Monte Carlo",
              fontsize=15, fontweight="bold", color=INK)
ax4a.set_title("A  ·  Variación entre las 100 réplicas",
                loc="left", fontsize=12, color=INK, pad=20)
bp = ax4a.boxplot(
    [arr * 100 for arr in arrays], patch_artist=True, widths=0.48,
    showfliers=False,
    medianprops=dict(color=INK, linewidth=2),
    whiskerprops=dict(color=MUTED, linewidth=1),
    capprops=dict(color=MUTED, linewidth=1))
for i, (patch, color, arr) in enumerate(zip(bp["boxes"], MODEL_COLORS, arrays), 1):
    patch.set_facecolor(color)
    patch.set_alpha(0.18)
    patch.set_edgecolor(color)
    # Desplazamiento horizontal determinista: solo separa los puntos visualmente.
    offsets = 0.15 * np.sin(np.arange(len(arr)) * 2.399963229728653)
    ax4a.scatter(i + offsets, arr * 100, s=11, color=color,
                 alpha=0.48, linewidths=0, zorder=2)
    ax4a.scatter(i, means[i - 1], marker="D", s=40, color=color,
                 edgecolor="white", linewidth=0.8, zorder=4)
ax4a.set_xticks([1, 2, 3])
ax4a.set_xticklabels(["Viterbi", "Baseline 1", "Baseline 2"], fontsize=10)
ax4a.set_ylabel("Precisión por réplica (%)", color=INK)
ax4a.set_ylim(0, 100)
ax4a.grid(axis="y", color=GRID, alpha=0.65)
ax4a.set_axisbelow(True)
ax4a.legend(handles=[
    Line2D([0], [0], marker="o", color=MUTED, linestyle="none",
           markersize=4, label="Una réplica"),
    Line2D([0], [0], color=INK, lw=2, label="Mediana"),
    Line2D([0], [0], marker="D", color=MUTED, linestyle="none",
           markersize=5, label="Media")],
    loc="lower left", frameon=False, fontsize=8.5, ncol=3)
clean_axis(ax4a)

ax4b.set_title("B  ·  Media e intervalo de confianza del 95 %",
                loc="left", fontsize=12, color=INK, pad=20)
for row, (mean, error, color) in enumerate(zip(means, errors, MODEL_COLORS)):
    ax4b.errorbar(mean, row, xerr=error, fmt="o", color=color,
                  markersize=8, capsize=6, elinewidth=2, capthick=1.5)
    ax4b.annotate(
        f"{mean:.2f} %   [{mean-error:.2f}; {mean+error:.2f}]",
        (mean, row), xytext=(0, 17), textcoords="offset points",
        ha="center", fontsize=10, color=color, fontweight="bold")
ax4b.set_yticks([0, 1, 2])
ax4b.set_yticklabels(["Viterbi", "Baseline 1", "Baseline 2"], fontsize=10)
ax4b.set_ylim(2.65, -0.65)
ax4b.set_xlim(0, 100)
ax4b.set_xlabel("Precisión media (%)", color=INK, labelpad=12)
ax4b.grid(axis="x", color=GRID, alpha=0.65)
clean_axis(ax4b)
fig4.text(0.5, 0.035,
           "100 secuencias · 50 eventos por secuencia · RandomState / MT19937 · Semilla 42\n"
           "B1: máxima emisión · B2: bayesiano estático · IC95 % aproximado: media ± 1.96 · s / √100 (s muestral)",
           ha="center", va="bottom", fontsize=9, color=MUTED, linespacing=1.7)
finish(fig4, "fig4_monte_carlo_boxplot.png")
print("Las cuatro figuras corresponden al experimento centralizado en src.")

