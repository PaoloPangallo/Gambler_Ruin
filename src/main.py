"""
=============================================================
  Rovina del Giocatore — Catena di Markov nel Discreto (DTMC)
  Lezioni 26-27-28, Prof. Pasquale Legato, A.A. 2024
=============================================================

FONTI USATE (tutto il codice si basa esclusivamente su questi):

  [SLIDE] = Slide "DTMC Lezioni 26-27-28" del Prof. Legato
  [STEW]  = W.J. Stewart, "Probability, Markov Chains, Queues,
             and Simulation", sezione 9.7, pp. 228-234
             (file PDF fornito dal professore)

Concetti implementati e loro fonte:
  - Matrice di transizione P              [STEW p.233] [SLIDE slide 2]
  - Classificazione stati (transito/ric.) [SLIDE slide 20-21]
  - Forma normale secondo Stewart         [SLIDE slide 24-25]
  - Equazione di Chapman-Kolmogorov P^n   [SLIDE slide 3]
  - Formula prob. fortuna x_i             [STEW pp.233-234]
  - Relazione di ricorrenza x_i = p*x_{i+1} + q*x_{i-1} [STEW p.233]
  - Caso p=q: x_i = i/N                  [STEW p.234]
  - Esempio Billy/Gerard (N=36, p=0.6)   [STEW p.234, Esempio 9.14]
  - Teorema 9.7.1 e 9.7.2 (stazionarietà)[STEW pp.229]
  - Distribuzione stazionaria z = zP      [STEW p.229, Teor. 9.7.1]
=============================================================
"""

# /// script
# dependencies = [
#   "numpy",
#   "matplotlib",
# ]
# ///

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import sys
import io

# Fix encoding per Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# ─────────────────────────────────────────────────────────────
# VALIDAZIONE DEI PARAMETRI
# ─────────────────────────────────────────────────────────────

def valida_parametri(i: int, N: int, p: float):
    """
    Valida i parametri d'ingresso per le funzioni probabilistiche.
    """
    if N <= 0:
        raise ValueError("Il capitale totale N deve essere maggiore di 0.")
    if i < 0 or i > N:
        raise ValueError(f"Lo stato iniziale i ({i}) deve soddisfare 0 <= i <= N ({N}).")
    if p < 0.0 or p > 1.0:
        raise ValueError("La probabilità p deve essere compresa nell'intervallo [0, 1].")


# ─────────────────────────────────────────────────────────────
# 1. MATRICE DI TRANSIZIONE
#    Fonte: [STEW p.233] e [SLIDE slide 2]
#
#    Stewart scrive esplicitamente la matrice P con:
#      P[0,0] = 1         (stato 0: assorbente)
#      P[N,N] = 1         (stato N: assorbente)
#      P[i,i+1] = p, P[i,i-1] = q   per 1 <= i <= N-1
# ─────────────────────────────────────────────────────────────

def build_matrice_transizione(N: int, p: float) -> np.ndarray:
    """
    Matrice di transizione P (N+1 x N+1).
    [STEW p.233]: "the transition probability matrix is given by
    [matrice con 1 in P[0,0], 1 in P[N,N], p e q sulle diagonali]"
    """
    if N <= 0:
        raise ValueError("Il capitale totale N deve essere maggiore di 0.")
    if p < 0.0 or p > 1.0:
        raise ValueError("La probabilità p deve essere compresa nell'intervallo [0, 1].")
    q = 1.0 - p
    P = np.zeros((N + 1, N + 1))
    P[0, 0] = 1.0
    P[N, N] = 1.0
    for i in range(1, N):
        P[i, i + 1] = p
        P[i, i - 1] = q
    return P


# ─────────────────────────────────────────────────────────────
# 2. CLASSIFICAZIONE DEGLI STATI
#    Fonte: [SLIDE slide 20-21]
#
#    Slide 20: "Se una DTMC ritorna un numero (atteso) finito
#    di volte nello stato j allora j è detto stato di transito.
#    Se invece la DTMC ritorna nello stato j indefinitamente
#    allora lo stato j è chiamato stato ricorrente."
#
#    Slide 21: "Se uno stato j è raggiungibile da uno stato i
#    e lo stato i è a sua volta raggiungibile da j, allora si
#    dice che gli stati i e j sono comunicanti."
#    "Quando tutti gli stati risultano comunicanti, il grafo è
#    detto irriducibile."
# ─────────────────────────────────────────────────────────────

def classifica_stati(N: int) -> dict:
    """
    Classificazione per la Rovina del Giocatore.

    Stati 0 e N: ricorrenti positivi, aperiodici (autoanello).
    Stati 1..N-1: di transito (il processo li visita un numero
                  atteso FINITO di volte prima di arrivare a 0 o N).
    Catena: RIDUCIBILE — non tutti gli stati comunicano tra loro.
    NON ergodica (slide 21: ergodica = irriducibile + ricorrente
    positiva + aperiodica).
    """
    return {
        "stati_ricorrenti": [0, N],
        "stati_transito":   list(range(1, N)),
        "irriducibile":     False,
        "ergodica":         False,
    }


# ─────────────────────────────────────────────────────────────
# 3. FORMA NORMALE SECONDO STEWART
#    Fonte: [SLIDE slide 24-25]
#    Il professore riporta esplicitamente la "Forma normale
#    secondo William J. Stewart": prima le classi chiuse
#    (stati ricorrenti), poi gli stati di transito.
# ─────────────────────────────────────────────────────────────

def forma_normale_stewart(N: int) -> list[int]:
    """
    Restituisce l'ordine degli stati per la forma normale
    secondo Stewart [SLIDE slide 24-25]:
      Prima: classi chiuse {0} e {N}
      Poi:   stati di transito {1, 2, ..., N-1}
    """
    return [0, N] + list(range(1, N))


# ─────────────────────────────────────────────────────────────
# 4. CHAPMAN-KOLMOGOROV: P^(n)
#    Fonte: [SLIDE slide 3]
#    "Per la catena di Markov e la generica coppia di stati i
#    e j, la P_ij(n) può e deve essere calcolata con l'equazione
#    di Chapman-Kolmogorov appoggiandosi ad un qualunque passo
#    intermedio r, 0 < r < n."
#    In forma matriciale: P^(n) = P^r * P^(n-r) = P^n
# ─────────────────────────────────────────────────────────────

def chapman_kolmogorov(P: np.ndarray, n: int) -> np.ndarray:
    """
    P^(n) = P^n  [SLIDE slide 3]
    Distribuzione al passo n da stato iniziale i:
      pi^(n) = e_i * P^n
    """
    return np.linalg.matrix_power(P, n)


def distribuzione_al_passo_n(P: np.ndarray, i: int, n: int) -> np.ndarray:
    """
    Vettore di distribuzione al passo n partendo dallo stato i.
    pi^(n) = e_i * P^n  [SLIDE slide 3]
    """
    e_i = np.zeros(P.shape[0])
    e_i[i] = 1.0
    return e_i @ chapman_kolmogorov(P, n)


# ─────────────────────────────────────────────────────────────
# 5. PROBABILITÀ DI RAGGIUNGERE N (fortuna)
#    Fonte: [STEW pp.233-234]
#
#    Stewart chiama questa probabilità x_i:
#      x_i = P(raggiungere N | stato iniziale i)
#      x_0 = 0,  x_N = 1
#
#    Relazione di ricorrenza [STEW p.233]:
#      x_i = p * x_{i+1} + q * x_{i-1},  1 <= i <= N-1
#
#    Soluzione [STEW p.234]:
#      Se p ≠ q:
#        x_i = [1 - (q/p)^i] / [1 - (q/p)^N]
#      Se p = q = 1/2:
#        x_i = i / N
# ─────────────────────────────────────────────────────────────

def prob_fortuna(i: int, N: int, p: float) -> float:
    """
    x_i = P(raggiungere N prima di 0 | X_0 = i)
    Formula di Stewart [STEW p.234], Esempio 9.14.

    Se p != q:  x_i = [1 - (q/p)^i] / [1 - (q/p)^N]
    Se p = q:   x_i = i / N
    """
    valida_parametri(i, N, p)
    if i == 0:
        return 0.0
    if i == N:
        return 1.0
    if p == 0.0:
        return 0.0
    if p == 1.0:
        return 1.0
    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:   # caso p = q = 1/2 [STEW p.234]
        return i / N
    r = q / p
    return (1.0 - r**i) / (1.0 - r**N)


def prob_rovina(i: int, N: int, p: float) -> float:
    """
    P(rovina | X_0 = i) = 1 - x_i
    [STEW p.234]: "the probability that Gerard takes all of
    Billy's marbles is only 1 - x_i"
    """
    valida_parametri(i, N, p)
    return 1.0 - prob_fortuna(i, N, p)

def expected_steps(i: int, N: int, p: float) -> float:
    """
    Calcola analiticamente il numero atteso di passi fino all'assorbimento (rovina o vittoria)
    partendo dallo stato i.
    Fonte: [STEW] e teoria delle catene assorbenti.
    Se p = q = 0.5: E[T_i] = i * (N - i)
    Se p != q:     E[T_i] = (i - N * x_i) / (q - p)  dove x_i = prob_fortuna(i, N, p)
    """
    valida_parametri(i, N, p)
    if i == 0 or i == N:
        return 0.0
    if p == 0.0:
        return float(i)
    if p == 1.0:
        return float(N - i)
    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:
        return float(i * (N - i))
    xi = prob_fortuna(i, N, p)
    return (i - N * xi) / (q - p)


# ─────────────────────────────────────────────────────────────
# 6. DISTRIBUZIONE STAZIONARIA z = zP
#    Fonte: [STEW pp.229] Teorema 9.7.1
#
#    "Let P be the single-step transition probability matrix
#    of an irreducible Markov chain. Then all the states of
#    this Markov chain are positive recurrent if and only if
#    the system of linear equations z = zP has a solution
#    with sum_j z_j = 1."
#
#    NOTA: per la Rovina del Giocatore la catena è RIDUCIBILE,
#    quindi il Teorema 9.7.1 non si applica direttamente.
#    La "distribuzione limite" dal capitale iniziale i converge
#    a [P(rovina|i), 0, ..., 0, P(fortuna|i)].
# ─────────────────────────────────────────────────────────────

def distribuzione_limite(i: int, N: int, p: float) -> np.ndarray:
    """
    Distribuzione limite per n -> infinito, partendo da i.
    Tutta la massa si concentra sugli stati assorbenti 0 e N.
    [STEW p.229]: gli stati 1..N-1 sono transienti, quindi
    lim_{n->inf} P^(n)_{i,j} = 0 per j = 1..N-1.
    """
    valida_parametri(i, N, p)
    pi = np.zeros(N + 1)
    pi[0] = prob_rovina(i, N, p)
    pi[N] = prob_fortuna(i, N, p)
    return pi


# ─────────────────────────────────────────────────────────────
# 7. SIMULAZIONE MONTE CARLO
#    Verifica numerica delle formule analitiche di Stewart.
# ─────────────────────────────────────────────────────────────

def simula(a: int, b: int, p: float,
           n_sim: int = 50_000, seed: int = None) -> dict:
    """
    Simula n_sim partite dalla catena DTMC.
    Confronto empirico con le formule di Stewart [STEW p.234].
    """
    if a < 0 or b < 0:
        raise ValueError("I capitali iniziali a e b non possono essere negativi.")
    N = a + b
    valida_parametri(a, N, p)
    
    rng = np.random.default_rng(seed)
    n_rovina = 0
    passi_lista = []

    for _ in range(n_sim):
        capitale = a
        passi = 0
        while 0 < capitale < N:
            capitale += 1 if rng.random() < p else -1
            passi += 1
        passi_lista.append(passi)
        if capitale == 0:
            n_rovina += 1

    return {
        "p_rovina_mc":  n_rovina / n_sim,
        "p_fortuna_mc": 1.0 - n_rovina / n_sim,
        "passi_medi":   float(np.mean(passi_lista)),
    }


# ─────────────────────────────────────────────────────────────
# 8. GRAFICO DELLA CATENA (Toy Model)
# ─────────────────────────────────────────────────────────────

def disegna_grafo(N: int, p: float, path_out: str):
    """
    Grafo della catena di Markov.
    Distingue stati ricorrenti [SLIDE slide 20] da transienti.
    """
    q = 1.0 - p
    fig, ax = plt.subplots(figsize=(max(9, N * 1.15), 3.8))

    for i in range(1, N):
        # freccia avanti (p)
        ax.annotate("", xy=(i + 1 - 0.3, 0.15), xytext=(i + 0.3, 0.15),
                    arrowprops=dict(arrowstyle="->", color="#1a6ead", lw=1.5,
                                   connectionstyle="arc3,rad=-0.25"))
        ax.text(i + 0.5, 0.48, f"p={p}", ha='center', fontsize=8,
                color="#1a6ead")
        # freccia indietro (q)
        ax.annotate("", xy=(i - 1 + 0.3, -0.15), xytext=(i - 0.3, -0.15),
                    arrowprops=dict(arrowstyle="->", color="#b03030", lw=1.5,
                                   connectionstyle="arc3,rad=-0.25"))
        ax.text(i - 0.5, -0.52, f"q={q:.2f}", ha='center', fontsize=8,
                color="#b03030")

    # autoanelli stati assorbenti
    for stato, col in [(0, "#b03030"), (N, "#2a8a2a")]:
        ax.annotate("", xy=(stato + 0.25, 0.55), xytext=(stato - 0.25, 0.55),
                    arrowprops=dict(arrowstyle="->", color=col, lw=2,
                                   connectionstyle="arc3,rad=-1.5"))
        ax.text(stato, 1.0, "1", ha='center', fontsize=9,
                color=col, fontweight='bold')

    for i in range(N + 1):
        if i == 0:
            col, ec = "#ffaaaa", "#b03030"
            lbl = f"{i}\n(rovina)"
        elif i == N:
            col, ec = "#aaffaa", "#2a8a2a"
            lbl = f"{i}\n(fortuna)"
        else:
            col, ec = "#aaddff", "#1a6ead"
            lbl = str(i)
        ax.add_patch(plt.Circle((i, 0), 0.28, color=col, ec=ec,
                                lw=2, zorder=5))
        ax.text(i, 0, lbl, ha='center', va='center',
                fontsize=8 if i in (0, N) else 9,
                fontweight='bold', zorder=6)

    leg = [
        mpatches.Patch(color="#ffaaaa", ec="#b03030",
                       label="Stato ricorrente (assorbente) — rovina [slide 20]"),
        mpatches.Patch(color="#aaffaa", ec="#2a8a2a",
                       label="Stato ricorrente (assorbente) — fortuna [slide 20]"),
        mpatches.Patch(color="#aaddff", ec="#1a6ead",
                       label="Stato di transito [slide 20]"),
    ]
    ax.legend(handles=leg, loc="upper center",
              bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=7.5)
    ax.set_xlim(-0.7, N + 0.7)
    ax.set_ylim(-0.9, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"Grafo della DTMC — Toy Model (N={N}, p={p})\n"
                 f"Catena RIDUCIBILE — 2 classi chiuse + stati di transito "
                 f"[Slide 21, Stewart Teor. 9.7.1-9.7.2]",
                 fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(path_out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  OK  Grafo salvato: {path_out}")


# ─────────────────────────────────────────────────────────────
# 9. VISUALIZZAZIONE COMPLETA
# ─────────────────────────────────────────────────────────────

def plot_analisi(a: int, b: int, p: float, n_sim: int = 40_000):
    N = a + b
    q = 1.0 - p
    stati = np.arange(N + 1)
    P = build_matrice_transizione(N, p)

    # vettori x_i e (1-x_i) per tutti gli stati [STEW p.234]
    xf = np.array([prob_fortuna(i, N, p) for i in stati])
    xr = 1.0 - xf

    sim = simula(a, b, p, n_sim=n_sim)

    # Forma normale di Stewart [SLIDE slide 24-25]
    ordine = forma_normale_stewart(N)
    # Visualizziamo la matrice completa ordinata secondo Stewart
    P_fn = P[np.ix_(ordine, ordine)]

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f"Rovina del Giocatore — DTMC [Lez. 26-27-28, Prof. Legato]\n"
        f"a={a}€, b={b}€, N=a+b={N}, p={p}, q={q:.2f}  "
        f"[Stewart, sez. 9.7, pp. 228-234]",
        fontsize=12, fontweight='bold')
    gs = gridspec.GridSpec(2, 3, hspace=0.45, wspace=0.38)

    # ── (1) x_i = P(fortuna) e 1-x_i = P(rovina) [STEW p.234] ──
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(stati, xr, "r-o", ms=3, lw=1.5,
             label=r"$1-x_i$ = P(rovina)")
    ax1.plot(stati, xf, "g-s", ms=3, lw=1.5,
             label=r"$x_i$ = P(fortuna)")
    ax1.axvline(a, ls="--", color="navy", lw=1.2, label=f"i=a={a}")
    ax1.set_xlabel("Stato iniziale i")
    ax1.set_ylabel("Probabilità")
    ax1.set_title(r"$x_i$ e $1-x_i$ [Stewart p.234]" + "\n"
                  r"$x_i = \frac{1-(q/p)^i}{1-(q/p)^N}$")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # ── (2) Chapman-Kolmogorov: P^n dal capitale a [SLIDE slide 3] ──
    ax2 = fig.add_subplot(gs[0, 1])
    passi_lista = [1, 10, 50, 200, 800]
    colori = plt.cm.viridis(np.linspace(0, 1, len(passi_lista)))
    for n_p, col in zip(passi_lista, colori):
        dist = distribuzione_al_passo_n(P, a, n_p)
        ax2.plot(range(N + 1), dist, "-o", ms=2, lw=1.2,
                 color=col, label=f"n={n_p}")
    ax2.set_xlabel("Stato j")
    ax2.set_ylabel(f"P(X(n)=j | X(0)={a})")
    ax2.set_title(f"Chapman-Kolmogorov: P^(n) [Slide 3]\n"
                  f"Convergenza alla distribuzione limite da i={a}")
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)

    # ── (3) Distribuzione limite [STEW p.229, Teor. 9.7.1] ──
    ax3 = fig.add_subplot(gs[0, 2])
    lim_dist = distribuzione_limite(a, N, p)
    ax3.bar([0, N], [lim_dist[0], lim_dist[N]],
            color=["#d62728", "#2ca02c"], edgecolor="black", width=3)
    ax3.bar(range(1, N), np.zeros(N - 1),
            color="#aaddff", edgecolor="none", width=1)
    ax3.set_xlim(-5, N + 5)
    ax3.set_ylim(0, 1.15)
    ax3.set_xlabel("Stato j")
    ax3.set_ylabel("Probabilità limite")
    ax3.set_title("Distribuzione limite per n→∞\n"
                  "[Stewart Teor. 9.7.1-9.7.2, Slide 27]\n"
                  "Massa su stati assorbenti; 0 sui transienti")
    ax3.annotate(f"{lim_dist[0]:.4f}", xy=(0, lim_dist[0]),
                 xytext=(8, lim_dist[0] - 0.1),
                 arrowprops=dict(arrowstyle="->"), fontsize=9)
    ax3.annotate(f"{lim_dist[N]:.4f}", xy=(N, lim_dist[N]),
                 xytext=(N - 15, lim_dist[N] + 0.08),
                 arrowprops=dict(arrowstyle="->"), fontsize=9)
    ax3.grid(axis="y", alpha=0.3)

    # ── (4) Forma normale di Stewart [SLIDE slide 24-25] ──
    ax4 = fig.add_subplot(gs[1, 0])
    im = ax4.imshow(P_fn, cmap="Blues", aspect="auto", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax4, fraction=0.046)
    
    # Generiamo un sottoinsieme di etichette per evitare sovrapposizioni mantenendo la matrice intera
    tick_positions = []
    tick_labels = []
    tick_positions.extend([0, 1])
    tick_labels.extend(["0", f"{N}"])
    
    step_vis = max(1, (N - 1) // 10)
    for k in range(2, N + 1):
        state_val = ordine[k]
        if (state_val - 1) % step_vis == 0 or state_val == 1 or state_val == N - 1:
            tick_positions.append(k)
            tick_labels.append(str(state_val))
            
    ax4.set_xticks(tick_positions)
    ax4.set_yticks(tick_positions)
    ax4.set_xticklabels(tick_labels, fontsize=7, rotation=45)
    ax4.set_yticklabels(tick_labels, fontsize=7)
    
    ax4.set_title("Matrice P — Forma normale (Stewart)\n"
                  "[Slide 24-25]: assorbenti | transienti")
    # Il blocco I2 è sempre un 2x2 in alto a sinistra (stati 0 e N)
    ax4.add_patch(plt.Rectangle((-0.5, -0.5), 2, 2,
                                fill=False, ec='red', lw=2.5))
    ax4.text(0.5, -1.2, "Blocco I₂\n(assorbenti)",
             ha='center', fontsize=7.5, color='red')

    # ── (5) Verifica formula Stewart: analitico vs Monte Carlo ──
    ax5 = fig.add_subplot(gs[1, 1])
    xr_a = prob_rovina(a, N, p)
    xf_a = prob_fortuna(a, N, p)
    labels = ["P(rovina)\n[STEW p.234]", "P(rovina)\nMonte Carlo",
              "P(fortuna)\n[STEW p.234]", "P(fortuna)\nMonte Carlo"]
    vals   = [xr_a, sim["p_rovina_mc"], xf_a, sim["p_fortuna_mc"]]
    colors = ["#d62728", "#ff7f0e", "#2ca02c", "#98df8a"]
    bars   = ax5.bar(labels, vals, color=colors, edgecolor="black", width=0.55)
    for bar, val in zip(bars, vals):
        ax5.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.01, f"{val:.4f}",
                 ha='center', va='bottom', fontsize=8)
    ax5.set_ylim(0, 1.15)
    ax5.set_title(f"Formula Stewart vs Monte Carlo\n"
                  f"(i=a={a}, N={N}, {n_sim:,} simulazioni)")
    ax5.set_ylabel("Probabilità")
    ax5.grid(axis="y", alpha=0.3)

    # ── (6) Esempio 9.14 di Stewart (Billy/Gerard) ──
    ax6 = fig.add_subplot(gs[1, 2])
    # Esempio 9.14 [STEW p.234]: N=36, p=0.6, i=16 e i=4
    N_eg = 36
    p_eg = 0.6
    stati_eg = np.arange(N_eg + 1)
    xf_eg = np.array([prob_fortuna(i, N_eg, p_eg) for i in stati_eg])
    ax6.plot(stati_eg, xf_eg, "b-", lw=2, label=f"p={p_eg}, N={N_eg}")
    # Punti dell'esempio
    for i_eg, col, lbl in [(16, "green", "i=16: x=0.9985"),
                            (4,  "red",   "i=4:  x=0.8025")]:
        x_val = prob_fortuna(i_eg, N_eg, p_eg)
        ax6.plot(i_eg, x_val, "o", color=col, ms=9, zorder=5)
        ax6.annotate(f"{lbl}\n({x_val:.4f})",
                     xy=(i_eg, x_val),
                     xytext=(i_eg + 2, x_val - 0.12),
                     arrowprops=dict(arrowstyle="->", color=col),
                     fontsize=8, color=col)
    ax6.set_xlabel("Stato iniziale i")
    ax6.set_ylabel(r"$x_i$ = P(fortuna)")
    ax6.set_title("Esempio 9.14 [Stewart p.234]\n"
                  "Billy/Gerard: N=36, p=0.6")
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)

    plt.savefig("outputs/dtmc_analisi_completa.png",
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  Grafici salvati: outputs/dtmc_analisi_completa.png")


# ─────────────────────────────────────────────────────────────
# 10. REPORT A TERMINALE
# ─────────────────────────────────────────────────────────────

def report(a: int, b: int, p: float):
    N = a + b
    q = 1.0 - p
    P = build_matrice_transizione(N, p)
    cls = classifica_stati(N)
    xf_a = prob_fortuna(a, N, p)
    xr_a = prob_rovina(a, N, p)
    sim  = simula(a, b, p)

    sep = "=" * 65

    output_lines = []
    def log(msg=""):
        output_lines.append(msg)
        print(msg)

    log(sep)
    log("  DTMC — ROVINA DEL GIOCATORE")
    log("  Lez. 26-27-28, Prof. Legato | Stewart sez. 9.7")
    log(sep)
    log(f"  Parametri: a={a}€, b={b}€, N={N}, p={p}, q={q:.4f}")
    log()

    log("  ── Classificazione stati [SLIDE slide 20-21] ──")
    log(f"     Ricorrenti (assorbenti): {cls['stati_ricorrenti']}")
    log(f"     Di transito:  1..{N-1}  ({N-1} stati)")
    log(f"     Irriducibile: {cls['irriducibile']}")
    log(f"     Ergodica:     {cls['ergodica']}")
    log()

    log("  ── Matrice P [STEW p.233] ──")
    log(f"     Dimensione: {N+1}x{N+1}, stocastica: "
          f"{np.allclose(P.sum(axis=1), 1.0)}")
    log(f"     Forma normale Stewart [slide 24-25]:")
    log(f"     ordine: [0, {N}, 1, 2, ..., {N-1}]")
    log()

    log("  ── Formula x_i [STEW p.234] ──")
    log(f"     x_i = [1-(q/p)^i] / [1-(q/p)^N]   (p ≠ q)")
    log(f"     x_i = i/N                            (p = q = 1/2)")
    log()
    log(f"     x_{a} = P(fortuna | i={a}) = {xf_a:.8f}")
    log(f"     1-x_{a} = P(rovina | i={a}) = {xr_a:.8f}")
    log()

    log("  ── Verifica Chapman-Kolmogorov [SLIDE slide 3] ──")
    for n_p in [10, 100, 500]:
        dist = distribuzione_al_passo_n(P, a, n_p)
        log(f"     P^({n_p:3d})[{a},{0}] = {dist[0]:.6f}  "
              f"P^({n_p:3d})[{a},{N}] = {dist[N]:.6f}  "
              f"(somma transienti = {dist[1:N].sum():.6f})")
    log(f"     → converge a [P(rovina)={xr_a:.4f}, "
          f"P(fortuna)={xf_a:.4f}]")
    log()

    log("  ── Monte Carlo (50.000 simulazioni) ──")
    log(f"     P(rovina)  MC = {sim['p_rovina_mc']:.6f}  "
          f"[formula: {xr_a:.6f}]")
    log(f"     P(fortuna) MC = {sim['p_fortuna_mc']:.6f}  "
          f"[formula: {xf_a:.6f}]")
    exp_steps = expected_steps(a, N, p)
    log(f"     Passi medi    = {sim['passi_medi']:.1f}  "
          f"[teoria assorbimento: {exp_steps:.1f}]")
    log()

    log("  ── Esempio 9.14 Stewart [STEW p.234] ──")
    log("     Billy/Gerard: N=36, p=0.6")
    x16 = prob_fortuna(16, 36, 0.6)
    x4  = prob_fortuna(4,  36, 0.6)
    steps16 = expected_steps(16, 36, 0.6)
    steps4  = expected_steps(4,  36, 0.6)
    log(f"     x_16 = {x16:.6f}  [Stewart: 0.998478] | Durata media gioco: {steps16:.1f} passi")
    log(f"     x_4  = {x4:.6f}  [Stewart: 0.802517] | Durata media gioco: {steps4:.1f} passi")
    log(f"     P(Gerard vince da i=4) = 1-x4 = {1-x4:.6f}  "
          f"[Stewart: 0.197483]")
    log(sep)

    # Scrittura su file
    with open("outputs/report_simulazione.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")
    print("  OK  Report salvato: outputs/report_simulazione.txt")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Assicuriamoci che la cartella outputs esista
    os.makedirs("outputs", exist_ok=True)

    # Parametri dal file xlsx del professore
    a, b, p = 10, 70, 0.49

    # 1) Grafo didattico Toy Model N=5
    disegna_grafo(N=5, p=0.49,
                  path_out="outputs/catena_toy.png")

    # 2) Report a terminale
    report(a=a, b=b, p=p)

    # 3) Grafici analisi completa
    plot_analisi(a=a, b=b, p=p, n_sim=40_000)