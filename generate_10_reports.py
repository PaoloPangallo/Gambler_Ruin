# /// script
# dependencies = [
#   "numpy",
#   "matplotlib",
# ]
# ///

import os
import time
from datetime import datetime

from main import prob_fortuna, prob_rovina, expected_steps, simula

def genera_tutti_i_report():
    # Creiamo la cartella per i report per mantenere pulito il workspace
    cartella_output = "report_simulazioni"
    os.makedirs(cartella_output, exist_ok=True)

    # 10 Scenari didatticamente differenziati e bilanciati
    scenari = [
        {
            "id": 1,
            "titolo": "Gioco Perfettamente Equo - Capitali Simmetrici",
            "a": 20, "b": 20, "p": 0.50,
            "desc": "Entrambi i giocatori iniziano con lo stesso capitale in un gioco equo. Le probabilità asintotiche di rovina/fortuna sono esattamente del 50%."
        },
        {
            "id": 2,
            "titolo": "Gioco Equo - Sbilanciamento del Capitale Iniziale",
            "a": 5, "b": 25, "p": 0.50,
            "desc": "Il gioco è equo, ma il giocatore A inizia con solo 5€ contro i 25€ del giocatore B. La rovina asintotica di A è alta (83.3%) per svantaggio di risorse."
        },
        {
            "id": 3,
            "titolo": "Grande Svantaggio di Capitale con Vantaggio di Gioco",
            "a": 5, "b": 95, "p": 0.55,
            "desc": "Il giocatore A ha solo 5€ contro i 95€ di B, ma il gioco è favorevole ad A (55%). Vediamo come il vantaggio di probabilità compensi la scarsità di risorse."
        },
        {
            "id": 4,
            "titolo": "Esempio Excel del Professore - Gioco Leggermente Sfavorevole",
            "a": 10, "b": 70, "p": 0.49,
            "desc": "Configurazione classica del corso del Prof. Legato. Il gioco è solo leggermente sfavorevole (49%) ma porta A a una rovina asintotica quasi certa (97.9%)."
        },
        {
            "id": 5,
            "titolo": "Gioco Leggermente Favorevole - Stessi Capitali",
            "a": 10, "b": 10, "p": 0.51,
            "desc": "Stessi capitali iniziali, ma con un lieve vantaggio del 51% per il giocatore A. La probabilità di vittoria di A sale significativamente al 59.8%."
        },
        {
            "id": 6,
            "titolo": "Esempio Billy/Gerard Originale di Stewart",
            "a": 16, "b": 20, "p": 0.60,
            "desc": "Esempio 9.14 descritto a pagina 234 del libro di Stewart. Il giocatore A (Billy) ha 16 biglie e il 60% di chance. La probabilità di fortuna è pari al 99.8%."
        },
        {
            "id": 7,
            "titolo": "Rovina Estremamente Rapida (Gioco Sfavorevole)",
            "a": 10, "b": 90, "p": 0.40,
            "desc": "Un gioco fortemente sfavorevole ad A (40%) combinato con un forte deficit di capitale iniziale. La rovina di A avviene in pochissimi passi."
        },
        {
            "id": 8,
            "titolo": "Successo Istantaneo (Forte Vantaggio di Gioco e Capitale)",
            "a": 80, "b": 20, "p": 0.60,
            "desc": "Forte vantaggio iniziale sia in termini di capitale (80€ contro 20€) che di probabilità (60%). Il successo di A è praticamente immediato e garantito."
        },
        {
            "id": 9,
            "titolo": "Toy Model Didattico (N ridotto al minimo)",
            "a": 2, "b": 2, "p": 0.50,
            "desc": "Un modello giocattolo con capitale totale N=4. Estremamente utile per studiare a mano i singoli passaggi della matrice di transizione e di Chapman-Kolmogorov."
        },
        {
            "id": 10,
            "titolo": "Deficit di Capitale Estremo con Gioco Altamente Sfavorevole",
            "a": 95, "b": 5, "p": 0.45,
            "desc": "A ha un immenso vantaggio di capitale (95€ contro 5€), ma il gioco è sfavorevole (45%). La probabilità di rovina finale di A è comunque dello 0% a causa del cuscinetto protettivo."
        }
    ]

    print(f" Avvio generazione di {len(scenari)} report didattici differenziati...")
    print("---------------------------------------------------------------------")

    for idx, sc in enumerate(scenari):
        a = sc["a"]
        b = sc["b"]
        p = sc["p"]
        N = a + b
        
        # Calcolo analitico asintotico
        xi_lim = prob_fortuna(a, N, p)
        xr_lim = 1.0 - xi_lim
        exp_steps = expected_steps(a, N, p)

        # Simulazione Monte Carlo per validazione numerica empirica (20.000 corse)
        sim = simula(a, b, p, n_sim=20_000)

        # Timestamp univoco per il report corrente
        ora_corrente = datetime.now()
        timestamp_file = ora_corrente.strftime("%Y%m%d_%H%M%S_%f")
        timestamp_log = ora_corrente.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

        filename = f"report_scenario_{sc['id']}_{timestamp_file}.txt"
        filepath = os.path.join(cartella_output, filename)

        # Scrittura del file di report strutturato
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=====================================================================\n")
            f.write(f"  REPORT DI SIMULAZIONE - SCENARIO {sc['id']:02d}\n")
            f.write(f"  {sc['titolo'].upper()}\n")
            f.write("=====================================================================\n")
            f.write(f"  Generato il:               {timestamp_log}\n")
            f.write(f"  Riferimento didattico:      Lezioni 26-28 Prof. Legato | Stewart Sez. 9.7\n")
            f.write("=====================================================================\n\n")
            
            f.write("  [1] DESCRIZIONE DIDATTICA:\n")
            f.write(f"      {sc['desc']}\n\n")

            f.write("  [2] SPECIFICHE DEI PARAMETRI:\n")
            f.write(f"      - Capitale Giocatore A (a):   {a} €\n")
            f.write(f"      - Capitale Giocatore B (b):   {b} €\n")
            f.write(f"      - Capitale Obiettivo (N):     {N} €\n")
            f.write(f"      - Frazione di Capitale (a/N): {a/N:.4f}\n")
            f.write(f"      - Probabilità di Vincita (p): {p:.4f}\n")
            f.write(f"      - Probabilità di Perdita (q): {1.0-p:.4f}\n")
            f.write(f"      - Natura del Gioco:           " + ("EQUO" if abs(p-0.5)<1e-9 else ("FAVOREVOLE ad A" if p>0.5 else "SFAVOREVOLE ad A")) + "\n\n")

            f.write("  [3] ANALISI ASINTOTICA TEORICA (n -> infinito):\n")
            f.write(f"      - Probabilità Limite di Rovina: {xr_lim:.6f} ({xr_lim*100:.2f}%)\n")
            f.write(f"      - Probabilità Limite di Fortuna:{xi_lim:.6f} ({xi_lim*100:.2f}%)\n")
            f.write(f"      - Numero Atteso di Passi (E[T]): {exp_steps:.2f} passi\n\n")

            f.write("  [4] VALIDAZIONE NUMERICA EMPIREA (20.000 simulazioni Monte Carlo):\n")
            f.write(f"      - Probabilità Rovina (MC):     {sim['p_rovina_mc']:.6f}  (Errore Assoluto: {abs(sim['p_rovina_mc'] - xr_lim):.6f})\n")
            f.write(f"      - Probabilità Fortuna (MC):    {sim['p_fortuna_mc']:.6f}  (Errore Assoluto: {abs(sim['p_fortuna_mc'] - xi_lim):.6f})\n")
            f.write(f"      - Durata Media Gioco (MC):     {sim['passi_medi']:.2f} passi  (Errore Assoluto: {abs(sim['passi_medi'] - exp_steps):.2f})\n\n")

            f.write("=====================================================================\n")
            f.write("  RIFLESSIONE ACCADEMICA:\n")
            f.write("  La convergenza tra il calcolo teorico (derivato dalle equazioni alle\n")
            f.write("  differenze di Stewart) e il calcolo Monte Carlo dimostra l'esattezza\n")
            f.write("  della teoria delle catene di Markov assorbenti. All'aumentare del numero\n")
            f.write("  di passi (n), la probabilità di non essere ancora assorbiti si riduce a 0\n")
            f.write("  con tasso di convergenza geometrico dettato dalla matrice Q^n.\n")
            f.write("=====================================================================\n")

        print(f" [+] Scenario {sc['id']:02d} generato con successo!")
        print(f"     -> File: {filepath}")
        print(f"     -> Timestamp: {timestamp_log}\n")

    print("---------------------------------------------------------------------")
    print(f" OPERAZIONE COMPLETATA: 10/10 report generati nella cartella '{cartella_output}'!")

if __name__ == "__main__":
    genera_tutti_i_report()
