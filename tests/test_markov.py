import unittest
import sys
import os
import numpy as np

# Aggiunge la cartella src al path per consentire l'importazione diretta di main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main import build_matrice_transizione, prob_fortuna, prob_rovina, expected_steps, valida_parametri

class TestMarkovMath(unittest.TestCase):

    def test_transition_matrix(self):
        """Testa le proprietà strutturali e stocastiche della matrice di transizione."""
        N = 10
        p = 0.45
        P = build_matrice_transizione(N, p)
        
        # 1. Dimensioni corrette
        self.assertEqual(P.shape, (N + 1, N + 1))
        
        # 2. Somma di riga pari a 1 (proprietà stocastica)
        row_sums = P.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, err_msg="La matrice non è stocastica (somma righe != 1)")
        
        # 3. Stati assorbenti (autoanelli con probabilità 1)
        self.assertEqual(P[0, 0], 1.0)
        self.assertEqual(P[N, N], 1.0)
        
        # 4. Transizioni negli stati transienti
        q = 1.0 - p
        for i in range(1, N):
            self.assertEqual(P[i, i + 1], p)
            self.assertEqual(P[i, i - 1], q)
            self.assertEqual(P[i, i], 0.0)  # no autoanelli negli stati transienti

    def test_prob_fortuna_boundaries(self):
        """Testa le condizioni al contorno per la probabilità di fortuna."""
        N = 20
        p = 0.60
        self.assertEqual(prob_fortuna(0, N, p), 0.0)
        self.assertEqual(prob_fortuna(N, N, p), 1.0)

    def test_prob_fortuna_fair_game(self):
        """Testa che per p = 0.5 la probabilità x_i sia lineare: x_i = i/N."""
        N = 15
        p = 0.5
        for i in range(N + 1):
            expected = i / N
            self.assertAlmostEqual(prob_fortuna(i, N, p), expected, places=10)

    def test_prob_fortuna_recurrence(self):
        """Testa la relazione di ricorrenza Markoviana: x_i = p*x_{i+1} + q*x_{i-1}."""
        N = 8
        p = 0.42
        q = 1.0 - p
        for i in range(1, N):
            x_i = prob_fortuna(i, N, p)
            x_ip1 = prob_fortuna(i + 1, N, p)
            x_im1 = prob_fortuna(i - 1, N, p)
            self.assertAlmostEqual(x_i, p * x_ip1 + q * x_im1, places=10)

    def test_prob_fortuna_extreme_p(self):
        """Testa il comportamento con probabilità estreme p=0 e p=1."""
        N = 10
        # Se p = 0, il giocatore va sempre a sinistra (rovina) tranne se parte già da N
        for i in range(N):
            self.assertEqual(prob_fortuna(i, N, 0.0), 0.0)
        self.assertEqual(prob_fortuna(N, N, 0.0), 1.0)

        # Se p = 1, il giocatore va sempre a destra (fortuna) tranne se parte già da 0
        self.assertEqual(prob_fortuna(0, N, 1.0), 0.0)
        for i in range(1, N + 1):
            self.assertEqual(prob_fortuna(i, N, 1.0), 1.0)

    def test_expected_steps_boundaries(self):
        """Testa il tempo medio di assorbimento agli stati limite."""
        N = 25
        p = 0.45
        self.assertEqual(expected_steps(0, N, p), 0.0)
        self.assertEqual(expected_steps(N, N, p), 0.0)

    def test_expected_steps_fair(self):
        """Testa la durata media per gioco equo: E[T_i] = i * (N - i)."""
        N = 12
        p = 0.5
        for i in range(N + 1):
            expected = float(i * (N - i))
            self.assertAlmostEqual(expected_steps(i, N, p), expected, places=10)

    def test_expected_steps_extreme_p(self):
        """Testa expected_steps con p=0 e p=1."""
        N = 10
        # Se p = 0, ogni passo va a sinistra. Da i ci vogliono esattamente i passi per 0 < i < N, e 0 per i=0 e i=N
        for i in range(N + 1):
            if i == 0 or i == N:
                self.assertEqual(expected_steps(i, N, 0.0), 0.0)
            else:
                self.assertEqual(expected_steps(i, N, 0.0), float(i))
        
        # Se p = 1, ogni passo va a destra. Da i ci vogliono esattamente N - i passi per 0 < i < N, e 0 per i=0 e i=N
        for i in range(N + 1):
            if i == 0 or i == N:
                self.assertEqual(expected_steps(i, N, 1.0), 0.0)
            else:
                self.assertEqual(expected_steps(i, N, 1.0), float(N - i))

    def test_expected_steps_recurrence(self):
        """Testa la relazione di ricorrenza del tempo medio: E[T_i] = 1 + p*E[T_{i+1}] + q*E[T_{i-1}]."""
        N = 10
        p = 0.55
        q = 1.0 - p
        for i in range(1, N):
            t_i = expected_steps(i, N, p)
            t_ip1 = expected_steps(i + 1, N, p)
            t_im1 = expected_steps(i - 1, N, p)
            self.assertAlmostEqual(t_i, 1.0 + p * t_ip1 + q * t_im1, places=10)

    def test_parameter_validation(self):
        """Verifica che vengano sollevate le eccezioni per parametri non validi."""
        # 1. N non valido
        with self.assertRaises(ValueError):
            valida_parametri(2, 0, 0.5)
        with self.assertRaises(ValueError):
            valida_parametri(2, -5, 0.5)

        # 2. i non valido
        with self.assertRaises(ValueError):
            valida_parametri(-1, 10, 0.5)
        with self.assertRaises(ValueError):
            valida_parametri(11, 10, 0.5)

        # 3. p non valido
        with self.assertRaises(ValueError):
            valida_parametri(3, 10, -0.1)
        with self.assertRaises(ValueError):
            valida_parametri(3, 10, 1.05)

if __name__ == '__main__':
    unittest.main()
