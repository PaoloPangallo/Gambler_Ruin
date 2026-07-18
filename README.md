# La Sorte del Giocatore (Rovina del Giocatore) — Analisi DTMC

Questo progetto analizza il classico problema stocastico della **Rovina del Giocatore** (Gambler's Ruin) modellato tramite **Catene di Markov a Tempo Discreto (DTMC)**. Il codice confronta le soluzioni analitiche teoriche derivate dalle equazioni alle differenze con stime empiriche ottenute mediante simulazioni Monte Carlo, offrendo al contempo strumenti di visualizzazione grafica e un'interfaccia interattiva (GUI).

## Obiettivi Didattici
* Modellare il problema come una catena di Markov assorbente.
* Verificare l'equazione di Chapman-Kolmogorov per la convergenza verso gli stati assorbenti.
* Calcolare la probabilità analitica di assorbimento (fortuna o rovina) e il tempo medio di assorbimento (durata media del gioco).
* Validare i risultati teorici tramite simulazioni Monte Carlo ad alta frequenza.
* Studiare la struttura a blocchi della **Forma Normale di Stewart** per matrici di transizione assorbenti.

---

## Formule Principali

### 1. Matrice di Transizione $P$
La catena ha $N+1$ stati $\{0, 1, \dots, N\}$, con due stati assorbenti ($0$ e $N$). La matrice $P$ ha dimensioni $(N+1) \times (N+1)$:
* $P_{0,0} = 1$ (stato assorbente della Rovina)
* $P_{N,N} = 1$ (stato assorbente della Fortuna)
* $P_{i,i+1} = p$ e $P_{i,i-1} = q = 1 - p$ per gli stati transienti $1 \le i \le N-1$

### 2. Probabilità di Fortuna ($x_i$)
Sia $x_i$ la probabilità di raggiungere lo stato $N$ (vittoria) partendo dallo stato iniziale $i$:
$$x_i = \begin{cases} 
\frac{1 - (q/p)^i}{1 - (q/p)^N} & \text{se } p \neq q \\
\frac{i}{N} & \text{se } p = q = 0.5 
\end{cases}$$

La probabilità di rovina (raggiungere lo stato $0$) è data da $1 - x_i$.

### 3. Durata Media del Gioco ($E[T_i]$)
Il numero atteso di passi (transizioni) fino all'assorbimento partendo dallo stato $i$:
$$E[T_i] = \begin{cases} 
\frac{i - N \cdot x_i}{q - p} & \text{se } p \neq q \\
i \cdot (N - i) & \text{se } p = q = 0.5 
\end{cases}$$

### 4. Chapman-Kolmogorov e Distribuzione al Passo $n$
$$P^{(n)} = P^n$$
La distribuzione di probabilità al passo $n$ partendo dallo stato iniziale $i$ è calcolata come:
$$\pi^{(n)} = e_i \cdot P^n$$
dove $e_i$ è il vettore con $1$ all'indice $i$ e $0$ altrove. Al tendere di $n \to \infty$, la distribuzione converge a:
$$\lim_{n \to \infty} \pi^{(n)} = [1-x_i, 0, \dots, 0, x_i]$$

---

## Struttura del Repository

Il repository è organizzato in modo da separare i sorgenti dai report generati e dalla documentazione di supporto:

```
├── .gitignore
├── README.md                  # Questo file di documentazione
├── requirements.txt           # Dipendenze standard del progetto
├── run_gui.bat                # Script batch per avviare rapidamente la GUI su Windows
├── src/                       # Codice sorgente Python
│   ├── main.py                # Modulo matematico principale e script CLI
│   ├── gui.py                 # Interfaccia grafica interattiva in Matplotlib
│   ├── build_pdf.py           # Script di generazione report e compilazione LaTeX
│   ├── generate_5_reports.py  # Generatore di report dettagliati per 5 scenari chiave
│   └── generate_10_reports.py # Generatore esteso per 10 scenari didattici
├── tests/                     # Test automatici di correttezza
│   └── test_markov.py         # Suite di test unitari (unittest)
├── docs/                      # Materiale didattico e relazioni scientifiche
│   ├── la_sorte_del_giocatore.tex  # Sorgente LaTeX della relazione
│   ├── La sorte del giocatore (2024).pptx # Presentazione di supporto
│   ├── Random Walk & Rovina del giocatore (W.J. Stewart book).pdf # Riferimento di Stewart
│   └── Rovina del giocatore.xlsx   # Modello Excel didattico
└── outputs/                   # Grafici, log e report generati (esclusi da Git tranne PDF)
    ├── la_sorte_del_giocatore.pdf  # PDF compilato della relazione
    ├── dtmc_analisi_completa.png   # Grafico riassuntivo completo
    ├── catena_toy.png             # Grafo strutturale del Toy Model (N=5)
    ├── report_simulazione.txt      # Report di simulazione testuale
    ├── sintesi_5_scenari.txt       # Tabella ASCII globale dei 5 scenari
    ├── report_5_scenari/           # Cartella con i report specifici dei 5 scenari
    └── report_simulazioni/         # Cartella con i report dei 10 scenari estesi
```

---

## Installazione ed Esecuzione

Questo progetto utilizza il gestore di pacchetti rapido **`uv`**. Se non lo hai installato, puoi installare le dipendenze classiche tramite `pip`.

### 1. Installazione Dipendenze
Con `pip`:
```bash
pip install -r requirements.txt
```

### 2. Esecuzione dei Componenti

* **Avvio dell'Interfaccia Grafica Interattiva (GUI)**:
  Su Windows, puoi fare doppio clic sul file `run_gui.bat` oppure eseguire da terminale:
  ```bash
  uv run src/gui.py
  ```
  *(La GUI consente di variare interattivamente $N$, $p$, $i$ e $n$ mostrando in tempo reale la matrice di transizione e le distribuzioni di massa.)*

* **Esecuzione dello Script Principale (CLI & Grafici completi)**:
  Genera i grafici analitici principali e compila un report testuale nel terminale:
  ```bash
  uv run src/main.py
  ```

* **Generazione Report Didattici (5 Scenari)**:
  Crea la cartella dei report strutturati in `outputs/report_5_scenari/` e la sintesi ASCII:
  ```bash
  uv run src/generate_5_reports.py
  ```

* **Generazione Relazione PDF in LaTeX**:
  Esegue la simulazione automatica, aggiorna la tabella dei dati nel sorgente LaTeX e compila il PDF finale in `outputs/`:
  ```bash
  uv run src/build_pdf.py
  ```

---

## Test Automatici

Per verificare la correttezza formale delle funzioni matematiche, è stata implementata una suite di unit test che convalida:
1. La stocasticità della matrice di transizione ($\sum_j P_{ij} = 1$).
2. Le condizioni al contorno per la probabilità di successo ($x_0 = 0, x_N = 1$).
3. Il comportamento corretto in regime di gioco equo ($p=0.5 \implies x_i = i/N$).
4. Il rispetto della relazione di ricorrenza Markoviana ($x_i = p \cdot x_{i+1} + q \cdot x_{i-1}$).
5. Il corretto sollevamento di eccezioni per parametri non ammissibili (es. $p > 1$, $i > N$, ecc.).

Esegui i test con il comando:
```bash
python -m unittest tests/test_markov.py
```
