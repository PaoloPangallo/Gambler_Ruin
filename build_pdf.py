import subprocess
import os
import sys
import numpy as np

# Re-implementing the core math functions to be self-contained and highly robust
def prob_fortuna(i: int, N: int, p: float) -> float:
    if i == 0:
        return 0.0
    if i == N:
        return 1.0
    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:
        return i / N
    r = q / p
    return (1.0 - r**i) / (1.0 - r**N)

def prob_rovina(i: int, N: int, p: float) -> float:
    return 1.0 - prob_fortuna(i, N, p)

def expected_steps(i: int, N: int, p: float) -> float:
    if i == 0 or i == N:
        return 0.0
    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:
        return float(i * (N - i))
    xi = prob_fortuna(i, N, p)
    return (i - N * xi) / (q - p)

def simula(a: int, b: int, p: float, n_sim: int = 20000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    N = a + b
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

def main():
    print("Avvio elaborazione scenari per tabella LaTeX...")
    
    scenari = [
        {"nome": "1. Equo Simm.", "a": 20, "b": 20, "p": 0.50},
        {"nome": "2. Sfav. Banco Cap.", "a": 10, "b": 90, "p": 0.49},
        {"nome": "3. Davide vs Golia", "a": 5, "b": 95, "p": 0.60},
        {"nome": "4. Cuscinetto Prot.", "a": 90, "b": 10, "p": 0.40},
        {"nome": "5. Billy/Gerard", "a": 16, "b": 20, "p": 0.60},
    ]

    table_rows = []
    
    for sc in scenari:
        a = sc["a"]
        b = sc["b"]
        p = sc["p"]
        N = a + b
        
        # Analitico
        xf = prob_fortuna(a, N, p)
        xr = prob_rovina(a, N, p)
        es = expected_steps(a, N, p)
        
        # Simulazione Monte Carlo
        print(f"Simulazione in corso per scenario: {sc['nome']}...")
        sim = simula(a, b, p, n_sim=20000, seed=42)
        
        # Formattazione della riga LaTeX
        row = (
            f"{sc['nome']} & {a} & {b} & {p:.2f} & "
            f"{xf:.4f} & {xr:.4f} & {es:.1f} & "
            f"{sim['p_fortuna_mc']:.4f} & {sim['p_rovina_mc']:.4f} & {sim['passi_medi']:.1f} \\\\"
        )
        table_rows.append(row)
        print(f"Scenario {sc['nome']} completato.")

    # Costruzione della tabella LaTeX completa
    table_latex = r"""\begin{table}[H]
\centering
\small
\setlength{\tabcolsep}{3.5pt}
\caption{Confronto dei risultati analitici e Monte Carlo (20.000 simulazioni per scenario)}
\label{tab:risultati}
\begin{tabular}{lcccccccccc}
\toprule
 & & & & \multicolumn{3}{c}{\textbf{Teoria (Analitico)}} & \multicolumn{3}{c}{\textbf{Monte Carlo (Simulazione)}} \\
\cmidrule(r){5-7} \cmidrule(l){8-10}
\textbf{Scenario} & $a$ & $b$ & $p$ & $x_a$ (Fort.) & $1-x_a$ (Rov.) & $E[T_a]$ & Fortuna & Rovina & Passi Medi \\
\midrule
"""
    table_latex += "\n".join(table_rows) + "\n"
    table_latex += r"""\bottomrule
\end{tabular}
\end{table}"""

    # Leggi il file tex
    tex_path = "la_sorte_del_giocatore.tex"
    if not os.path.exists(tex_path):
        print(f"Errore: {tex_path} non trovato!")
        sys.exit(1)
        
    with open(tex_path, "r", encoding="utf-8") as f:
        tex_content = f.read()

    import re
    # Sostituisci il segnaposto %%TABELLA_RISULTATI%% o la tabella precedente per idempotenza
    if "%%TABELLA_RISULTATI%%" in tex_content:
        tex_content = tex_content.replace("%%TABELLA_RISULTATI%%", table_latex)
        print("Tabella inserita correttamente al posto del segnaposto.")
    else:
        match = re.search(r"\\begin\{table\}\[H\].*?\\end\{table\}", tex_content, re.DOTALL)
        if match:
            start, end = match.span()
            tex_content = tex_content[:start] + table_latex + tex_content[end:]
            print("Tabella precedente aggiornata con successo nel sorgente LaTeX.")
        else:
            print("Attenzione: né il segnaposto %%TABELLA_RISULTATI%% né una tabella esistente sono stati trovati.")

    # Scrivi il file tex finale
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    # Compilazione del file LaTeX
    print("Compilazione in corso con pdflatex (Passo 1/2)...")
    res1 = subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path], capture_output=True, text=True)
    if res1.returncode != 0:
        print("Errore nella prima compilazione LaTeX:")
        print(res1.stdout[:1000])
        sys.exit(1)
        
    print("Compilazione in corso con pdflatex (Passo 2/2 per riferimenti)...")
    res2 = subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path], capture_output=True, text=True)
    if res2.returncode != 0:
        print("Errore nella seconda compilazione LaTeX:")
        print(res2.stdout[:1000])
        sys.exit(1)

    print("Successo! PDF generato correttamente: la_sorte_del_giocatore.pdf")

if __name__ == "__main__":
    main()
