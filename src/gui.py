# /// script
# dependencies = [
#   "numpy",
#   "matplotlib",
# ]
# ///

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from main import build_matrice_transizione, forma_normale_stewart, prob_fortuna, expected_steps, simula

def run_gui():
    # Valori di partenza predefiniti
    N_init = 5
    p_init = 0.49
    i_init = 2
    n_init = 1

    # Inizializza la figura principale con dimensioni confortevoli per la visualizzazione laterale
    fig = plt.figure(figsize=(16, 9.5))
    fig.canvas.manager.set_window_title("Rovina del Giocatore — Laboratorio DTMC Interattivo")

    # Pannelli grafici (Subplot)
    ax_matrix = fig.add_subplot(1, 2, 1)
    ax_dist   = fig.add_subplot(1, 2, 2)
    
    # Regolazione layout: lascia spazio in basso per gli slider e a destra per la descrizione didattica
    plt.subplots_adjust(bottom=0.38, left=0.08, right=0.76, top=0.88, wspace=0.32)

    # -------------------------------------------------------------------------
    # 1. SETUP DEGLI SLIDER (CONTROLLI INTERATTIVI)
    # -------------------------------------------------------------------------
    
    # Slider N (Capitale Totale dell'economia di gioco)
    ax_slider_N = plt.axes([0.12, 0.24, 0.25, 0.03])
    slider_N = Slider(
        ax=ax_slider_N, label='Capitale Totale (N) ',
        valmin=3, valmax=15, valinit=N_init, valstep=1,
        color='#1a6ead', valfmt='%d'
    )

    # Slider i (Capitale Iniziale del giocatore A)
    ax_slider_i = plt.axes([0.12, 0.16, 0.25, 0.03])
    slider_i = Slider(
        ax=ax_slider_i, label='Capitale Iniziale (i) ',
        valmin=1, valmax=N_init - 1, valinit=i_init, valstep=1,
        color='#1a6ead', valfmt='%d'
    )

    # Slider p (Probabilità di vincita elementare ad ogni singola mano)
    ax_slider_p = plt.axes([0.48, 0.24, 0.25, 0.03])
    slider_p = Slider(
        ax=ax_slider_p, label='Prob. Vincita (p) ',
        valmin=0.05, valmax=0.95, valinit=p_init, valstep=0.01,
        color='#2a8a2a', valfmt='%.2f'
    )

    # Slider n (Passo temporale/frazione temporale discretizzata della DTMC)
    ax_slider_n = plt.axes([0.48, 0.16, 0.25, 0.03])
    slider_n = Slider(
        ax=ax_slider_n, label='Passi Temporali (n) ',
        valmin=1, valmax=100, valinit=n_init, valstep=1,
        color='#2a8a2a', valfmt='%d'
    )

    # Pulsante per Salvare il Report didattico esteso
    ax_btn = plt.axes([0.80, 0.16, 0.12, 0.11])
    btn = Button(ax_btn, 'Salva Report\n(TXT)', color='#2a8a2a', hovercolor='#1e631e')
    btn.label.set_color('white')
    btn.label.set_fontweight('bold')
    btn.label.set_fontsize(10)


    # -------------------------------------------------------------------------
    # 2. LOGICA DI DISEGNO DINGAMICO E CONVERGENZA
    # -------------------------------------------------------------------------
    
    def update_plot(val=None):
        # Estrae i parametri correnti dai controlli
        N = int(slider_N.val)
        p = float(slider_p.val)
        i = int(slider_i.val)
        n = int(slider_n.val)

        # Calcoli Markoviani
        P = build_matrice_transizione(N, p)
        Pn = np.linalg.matrix_power(P, n)
        
        # Riordina per la forma normale secondo Stewart [Slide 24-25]
        ordine = forma_normale_stewart(N)
        idx = np.array(ordine)
        Pn_ord = Pn[np.ix_(idx, idx)]

        # ─────────────────────────────────────────────────────────────────────
        # A. DISEGNO DELLA HEATMAP DELLA MATRICE P^n
        # ─────────────────────────────────────────────────────────────────────
        ax_matrix.clear()
        
        # Disegna la heatmap con colormap elegante
        im = ax_matrix.imshow(Pn_ord, cmap='Blues', aspect='auto', vmin=0, vmax=1)
        ax_matrix.set_title(
            f"Matrice $P^{{{n}}}$ in Forma Normale di Stewart\n"
            f"[Stati Assorbenti in Alto, Transienti in Basso]", 
            pad=12, fontsize=11, fontweight='bold'
        )
        
        # Ticks e configurazione degli stati ordinati
        ax_matrix.set_xticks(range(N + 1))
        ax_matrix.set_yticks(range(N + 1))
        ax_matrix.set_xticklabels([str(s) for s in ordine], fontsize=9)
        ax_matrix.set_yticklabels([str(s) for s in ordine], fontsize=9)
        ax_matrix.set_xlabel("Stato di Arrivo ($j$)", fontsize=9.5)
        ax_matrix.set_ylabel("Stato di Partenza ($i$)", fontsize=9.5)

        # Linee divisorie rosse tratteggiate per separare i blocchi fondamentali I, 0, R, Q
        ax_matrix.axhline(1.5, color='#b03030', lw=2.5, ls='--')
        ax_matrix.axvline(1.5, color='#b03030', lw=2.5, ls='--')

        # Ottimizzazione font in base alla dimensione della matrice
        fontsize_cell = 9 if N <= 6 else (8 if N <= 9 else 6)
        for r in range(N + 1):
            for c in range(N + 1):
                val_cell = Pn_ord[r, c]
                col_text = "white" if val_cell > 0.55 else "black"
                ax_matrix.text(c, r, f"{val_cell:.3f}", ha="center", va="center",
                               color=col_text, fontweight='bold', fontsize=fontsize_cell)

        # Posizionamento etichette giganti dei blocchi (semi-trasparenti)
        x_I = 0.5; y_I = 0.5
        x_0 = (2 + N) / 2.0; y_0 = 0.5
        x_R = 0.5; y_R = (2 + N) / 2.0
        x_Q = (2 + N) / 2.0; y_Q = (2 + N) / 2.0
        
        ax_matrix.text(x_I, y_I, "$I_2$", ha="center", va="center", color="#b03030", fontsize=28, alpha=0.15, fontweight='bold')
        ax_matrix.text(x_0, y_0, "$0$", ha="center", va="center", color="#b03030", fontsize=28, alpha=0.15, fontweight='bold')
        ax_matrix.text(x_R, y_R, "$R$", ha="center", va="center", color="#b03030", fontsize=28, alpha=0.15, fontweight='bold')
        ax_matrix.text(x_Q, y_Q, "$Q$", ha="center", va="center", color="#b03030", fontsize=28, alpha=0.15, fontweight='bold')

        # ─────────────────────────────────────────────────────────────────────
        # B. DISEGNO DELLA DISTRIBUZIONE DI MASSA DI PROBABILITÀ (BARRE)
        # ─────────────────────────────────────────────────────────────────────
        ax_dist.clear()
        
        # Estrae la riga corrispondente allo stato iniziale i
        dist_i = Pn[i, :]
        masse = [dist_i[0], dist_i[N], np.sum(dist_i[1:N])]
        
        bar_labels = ["Rovina\n(Stato 0)", f"Fortuna\n(Stato {N})", "Stati di\nTransito"]
        colori = ['#ffaaaa', '#aaffaa', '#aaddff']
        ecolors = ['#b03030', '#2a8a2a', '#1a6ead']
        
        barre = ax_dist.bar(bar_labels, masse, color=colori, edgecolor=ecolors, lw=2, width=0.55)
        ax_dist.set_ylim(0, 1.15)
        ax_dist.set_ylabel("Probabilità", fontsize=9.5)
        ax_dist.set_title(
            f"Massa di Probabilità al Passo $n = {n}$ da $i = {i}$\n"
            f"[Slide 3: Chapman-Kolmogorov]", 
            pad=12, fontsize=11, fontweight='bold'
        )
        ax_dist.grid(axis='y', alpha=0.3, ls=':')

        # Aggiunta etichette dei valori sopra ogni singola barra
        for barra in barre:
            h = barra.get_height()
            ax_dist.text(barra.get_x() + barra.get_width()/2.0, h + 0.02,
                         f"{h:.4f}", ha='center', va='bottom', fontweight='bold', fontsize=9.5)

        # Calcolo dei limiti asintotici e del tempo atteso
        xi_lim = prob_fortuna(i, N, p)
        t_atteso = expected_steps(i, N, p)
        
        # Disegno delle linee tratteggiate asintotiche sul grafico
        ax_dist.axhline(1.0 - xi_lim, color='#b03030', ls=':', lw=2, alpha=0.8)
        ax_dist.axhline(xi_lim, color='#2a8a2a', ls=':', lw=2, alpha=0.8)
        
        # Etichette di testo dei limiti
        ax_dist.text(2.35, 1.0 - xi_lim, "limite rovina", color='#b03030', fontsize=8, va='bottom', ha='right', fontweight='bold')
        ax_dist.text(2.35, xi_lim, "limite fortuna", color='#2a8a2a', fontsize=8, va='bottom', ha='right', fontweight='bold')

        # ─────────────────────────────────────────────────────────────────────
        # C. SCRITTURA DEL PANNELLO LATERALE DIDATTICO
        # ─────────────────────────────────────────────────────────────────────
        q = 1.0 - p
        tipo_gioco = "EQUO" if abs(p - 0.5) < 1e-9 else ("FAVOREVOLE" if p > 0.5 else "SFAVOREVOLE")
        
        info_text = (
            r"$\bf{PARAMETRI\ CORRENTI}$" + "\n"
            f" Capitale Obiettivo ($N$): {N} €\n"
            f" Capitale Iniziale ($i$): {i} €\n"
            f" Prob. Vincita ($p$): {p:.2f}\n"
            f" Prob. Perdita ($q$): {q:.2f}\n"
            f" Passo Corrente ($n$): {n}\n\n"
            r"$\bf{ANALISI\ ASINTOTICA\ (n \to \infty)}$" + "\n"
            f" Prob. Rovina ($1-x_i$): {1.0 - xi_lim:.4f}\n"
            f" Prob. Fortuna ($x_i$): {xi_lim:.4f}\n"
            f" Durata Media Gioco: {t_atteso:.1f} passi\n\n"
            r"$\bf{STATO\ AL\ PASSO\ n}$" + "\n"
            f" Prob. Rovina: {masse[0]:.4f}\n"
            f" Prob. Fortuna: {masse[1]:.4f}\n"
            f" In Transito (1..{N-1}): {masse[2]:.4f}\n\n"
            r"$\bf{GUIDA\ DIDATTICA}$" + "\n"
            f"• Con $p={p:.2f}$ il gioco è\n"
            f"  {tipo_gioco} per il giocatore A.\n"
            f"• Gli stati 0 e {N} sono\n"
            f"  stati ricorrenti assorbenti.\n"
            f"• La probabilità in transito\n"
            f"  tende a 0 per $n \\to \\infty$.\n"
            f"  Si osserva $Q^n \\to 0$ [Slide 26]."
        )
        
        # Posiziona il box informativo sulla destra
        ax_dist.text(
            1.08, 0.5, info_text, transform=ax_dist.transAxes,
            fontsize=9.5, bbox=dict(boxstyle='round,pad=0.7', facecolor='#fbfcfd', edgecolor='#d0d7de', alpha=1.0),
            verticalalignment='center', linespacing=1.45
        )

        fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # 3. GESTIONE EVENTI DINAMICI E CALLBACK
    # -------------------------------------------------------------------------
    
    def on_N_change(val):
        """Gestisce il cambiamento di N regolando il valore massimo di i"""
        N_val = int(slider_N.val)
        
        # Ricalibra dinamicamente i limiti per lo slider dell'iniziale i
        slider_i.valmax = N_val - 1
        slider_i.ax.set_xlim(1, N_val - 1)
        
        # Assicura che i non superi mai il nuovo limite N-1
        if slider_i.val >= N_val:
            slider_i.set_val(N_val - 1)
        else:
            update_plot()

    # Collega le funzioni di aggancio agli slider
    slider_N.on_changed(on_N_change)
    slider_i.on_changed(lambda val: update_plot())
    slider_p.on_changed(lambda val: update_plot())
    slider_n.on_changed(lambda val: update_plot())

    # -------------------------------------------------------------------------
    # 4. SALVATAGGIO DEL REPORT DIDATTICO CON VALIDAZIONE MONTE CARLO
    # -------------------------------------------------------------------------
    
    def on_click_save(event):
        N = int(slider_N.val)
        i = int(slider_i.val)
        p = float(slider_p.val)
        n = int(slider_n.val)

        # Calcola le probabilità al passo n correntemente selezionato
        P = build_matrice_transizione(N, p)
        Pn = np.linalg.matrix_power(P, n)
        dist_i = Pn[i, :]
        p_rovina_n = dist_i[0]
        p_fortuna_n = dist_i[N]
        p_transito_n = np.sum(dist_i[1:N])

        # Calcoli teorici asintotici
        xi_lim = prob_fortuna(i, N, p)
        exp_steps = expected_steps(i, N, p)

        # Feedback visivo immediato di "Elaborazione in corso"
        btn.label.set_text("Esecuzione MC...")
        btn.ax.set_facecolor('#ffaa00')
        fig.canvas.draw_idle()
        plt.pause(0.05) 

        # Esegue una simulazione Monte Carlo per validazione numerica
        sim = simula(i, N - i, p, n_sim=30_000)

        # Scrive il report su file outputs/report_simulazione.txt
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/report_simulazione.txt", "w", encoding="utf-8") as f:
            f.write("=========================================================\n")
            f.write("    REPORT DI SIMULAZIONE - DTMC INTERATTIVO (GUI)\n")
            f.write("    Lezioni 26-27-28, Prof. Legato | Stewart Sez. 9.7\n")
            f.write("=========================================================\n\n")
            f.write("  [1] PARAMETRI DEL MODELLO:\n")
            f.write(f"      - Capitale Totale (N):      {N} €\n")
            f.write(f"      - Capitale Iniziale (i):    {i} € (giocatore A)\n")
            f.write(f"      - Capitale Iniziale (N-i):  {N-i} € (giocatore B)\n")
            f.write(f"      - Probabilità di Vincita:   {p:.4f} (p)\n")
            f.write(f"      - Probabilità di Perdita:   {1.0-p:.4f} (q)\n")
            f.write(f"      - Gioco:                    " + ("EQUO" if abs(p-0.5)<1e-9 else ("FAVOREVOLE ad A" if p>0.5 else "SFAVOREVOLE ad A")) + "\n\n")
            
            f.write(f"  [2] STATO DELLA CATENA AL PASSO SELEZIONATO (n = {n}):\n")
            f.write(f"      - P(Rovina di A al passo n):    {p_rovina_n:.6f}\n")
            f.write(f"      - P(Fortuna di A al passo n):   {p_fortuna_n:.6f}\n")
            f.write(f"      - P(Ancora in Gioco al passo n): {p_transito_n:.6f}\n\n")
            
            f.write("  [3] ANALISI ASINTOTICA E CONVERGENZA (n -> infinito):\n")
            f.write(f"      - P(Rovina limite di A):       {1.0 - xi_lim:.6f}\n")
            f.write(f"      - P(Fortuna limite di A):      {xi_lim:.6f}\n")
            f.write(f"      - Durata Media Attesa Gioco:    {exp_steps:.2f} passi\n\n")
            
            f.write("  [4] VALIDAZIONE MONTE CARLO (30.000 simulazioni):\n")
            f.write(f"      - P(Rovina di A empirica):      {sim['p_rovina_mc']:.6f}  (Scarto: {abs(sim['p_rovina_mc'] - (1.0-xi_lim)):.6f})\n")
            f.write(f"      - P(Fortuna di A empirica):     {sim['p_fortuna_mc']:.6f}  (Scarto: {abs(sim['p_fortuna_mc'] - xi_lim):.6f})\n")
            f.write(f"      - Durata Media Empirica:        {sim['passi_medi']:.2f} passi  (Scarto: {abs(sim['passi_medi'] - exp_steps):.2f})\n\n")
            f.write("=========================================================\n")
            f.write("  Nota didattica: La catena DTMC della Rovina del Giocatore\n")
            f.write("  è RIDUCIBILE e presenta due classi chiuse (stati 0 e N).\n")
            f.write("  Tutti gli altri stati sono di transito. Con l'aumentare di n,\n")
            f.write("  la probabilità di trovarsi negli stati transienti tende a zero\n")
            f.write("  con tasso geometrico (Q^n -> 0).\n")
            f.write("=========================================================\n")
        
        print(f"  OK  Report salvato da GUI: report_simulazione.txt (N={N}, i={i}, p={p:.2f}, n={n})")
        
        # Animazione del successo sul pulsante
        btn.label.set_text("Generato!")
        btn.ax.set_facecolor('#1a6ead')
        fig.canvas.draw_idle()
        plt.pause(0.5)
        btn.label.set_text("Salva Report\n(TXT)")
        btn.ax.set_facecolor('#2a8a2a')
        fig.canvas.draw_idle()

    # Collega il pulsante all'evento click
    btn.on_clicked(on_click_save)

    # Disegna la prima schermata all'avvio
    update_plot()
    plt.show()

if __name__ == "__main__":
    run_gui()
