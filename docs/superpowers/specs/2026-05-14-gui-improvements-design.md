# GUI Improvements — Rovina del Giocatore
**Date:** 2026-05-14  
**File:** `gui.py`  
**Scope:** Small, targeted improvements — no architectural changes

---

## Context

The existing GUI (`gui.py`) shows a P^n matrix and a probability mass bar chart driven by a single slider for step count `n`. Two weaknesses:
1. The starting state `i` is hardcoded to 2 — the viewer cannot explore how outcomes change with different starting capitals.
2. The central theoretical result of the course (the fortune probability x_i from Stewart p.234) is absent from the GUI, making it disconnected from the slides.

The goal is to fix both with minimal changes: add an `i` slider and a third panel showing the x_i curve.

---

## Layout

1 row × 3 columns. Existing panels stay in place; new panel added on the right.

```
┌─────────────────┬─────────────────┬─────────────────┐
│  P^n matrix     │  Bar chart      │  x_i curve      │
│  Stewart normal │  mass at step n │  all states,    │
│  form           │  from state i   │  marker at i    │
│  [Slide 24-25]  │  [Slide 3]      │  [STEW p.234]   │
└─────────────────┴─────────────────┴─────────────────┘
         [Slider n: 1–100   passi (n)]
         [Slider i: 1–N-1   stato partenza (i)]
```

Bottom margin increases to fit both sliders stacked vertically.

---

## Panel Specifications

### Left — P^n matrix (unchanged logic)
- Add small subtitle: `[Slide 24-25]`
- Updates when `n` changes only

### Middle — Bar chart (updated)
- Title: `f"Distribuzione dopo {n} passi da i={i}"`
- Updates when either `n` or `i` changes
- Add horizontal dashed lines at the analytical limits:
  - Rovina bar: dashed line at `1 - x_i` labelled `"limite →"`
  - Fortuna bar: dashed line at `x_i` labelled `"limite →"`
- Source citation: `[Slide 3]` in subtitle

### Right — x_i curve (new panel)
- Line plot of `x_k = prob_fortuna(k, N, p)` for `k = 0..N`
- Vertical dashed marker at current `i`, updating when `i` slider changes
- Annotation at marker: `f"x_{i} = {x_i:.4f}"` and `f"1-x_{i} = {1-x_i:.4f}"`
- Formula as subtitle: `x_i = [1-(q/p)^i] / [1-(q/p)^N]`
- Title: `"Prob. fortuna xᵢ [Stewart p.234]"`
- Curve is static (depends only on N and p, not on n); only the marker moves

---

## Sliders

| Slider | Range | Default | Triggers |
|--------|-------|---------|----------|
| `n` (passi) | 1–100 | 1 | Left + Middle panels |
| `i` (stato partenza) | 1–N-1 | 2 | Middle + Right panels |

Stacked vertically below the plots. Both use `valstep=1`.

---

## Update Logic

```
on n change  →  recompute P^n  →  update left matrix + middle bar chart
on i change  →  recompute x_i  →  update middle bar chart + right marker
```

The x_i curve itself is drawn once at startup and never redrawn (it is fixed for given N and p).

---

## Files Changed

- `gui.py` — only file modified

## Functions Reused from main.py

- `build_matrice_transizione(N, p)` — already imported
- `chapman_kolmogorov(P, n)` — already imported
- `forma_normale_stewart(N)` — already imported
- `prob_fortuna(i, N, p)` — needs to be added to the import line

---

## Verification

1. Run `python gui.py` — window opens without errors
2. Move `n` slider: left matrix and middle bar chart update; right panel unchanged
3. Move `i` slider: middle bar chart updates (new starting state); right marker moves to new i
4. At large `n` (≈80+), middle bar heights should approach the dashed limit lines
5. At `i=1` and `i=N-1`, x_i values match analytical formula manually computed
6. Source citations visible on each panel
