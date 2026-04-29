import pytest
from client import (
    ma_sorte,
    trouver_piece,
    est_bloquee,
    coups_possibles,
    score_coup,
    meilleur_coup,
    choose_move,
)

# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

BOARD_COLORS = [
    ["orange", "blue",   "purple", "pink",   "yellow", "red",    "green",  "brown"],
    ["red",    "orange", "pink",   "green",  "blue",   "yellow", "brown",  "purple"],
    ["green",  "pink",   "orange", "red",    "purple", "brown",  "yellow", "blue"],
    ["pink",   "purple", "blue",   "orange", "brown",  "green",  "red",    "yellow"],
    ["yellow", "red",    "green",  "brown",  "orange", "blue",   "purple", "pink"],
    ["blue",   "yellow", "brown",  "purple", "red",    "orange", "pink",   "green"],
    ["purple", "brown",  "yellow", "blue",   "green",  "pink",   "orange", "red"],
    ["brown",  "green",  "red",    "yellow", "pink",   "purple", "blue",   "orange"],
]

def plateau_vide():
    """Plateau sans aucune pièce."""
    return [[[BOARD_COLORS[r][c], None] for c in range(8)] for r in range(8)]

def poser_piece(plateau, ligne, colonne, couleur, sorte):
    """Place une pièce sur le plateau."""
    plateau[ligne][colonne][1] = [couleur, sorte]
    return plateau


# ──────────────────────────────────────────────
#  Tests : ma_sorte
# ──────────────────────────────────────────────

class TestMaSorte:
    def test_joueur_0_est_dark(self):
        state = {"current": 0}
        assert ma_sorte(state) == "dark"

    def test_joueur_1_est_light(self):
        state = {"current": 1}
        assert ma_sorte(state) == "light"


# ──────────────────────────────────────────────
#  Tests : trouver_piece
# ──────────────────────────────────────────────

class TestTrouverPiece:
    def test_trouve_piece_existante(self):
        plateau = plateau_vide()
        poser_piece(plateau, 3, 5, "red", "dark")
        assert trouver_piece(plateau, "red", "dark") == [3, 5]

    def test_retourne_none_si_absente(self):
        plateau = plateau_vide()
        assert trouver_piece(plateau, "blue", "light") is None

    def test_ne_confond_pas_sorte(self):
        plateau = plateau_vide()
        poser_piece(plateau, 2, 2, "green", "dark")
        assert trouver_piece(plateau, "green", "light") is None

    def test_ne_confond_pas_couleur(self):
        plateau = plateau_vide()
        poser_piece(plateau, 4, 4, "orange", "light")
        assert trouver_piece(plateau, "red", "light") is None


# ──────────────────────────────────────────────
#  Tests : est_bloquee
# ──────────────────────────────────────────────

class TestEstBloquee:
    def test_non_bloquee_chemin_libre(self):
        plateau = plateau_vide()
        poser_piece(plateau, 5, 3, "purple", "dark")
        assert est_bloquee(plateau, [5, 3], "dark") is False

    def test_bloquee_par_pieces_adverses(self):
        plateau = plateau_vide()
        poser_piece(plateau, 3, 3, "orange", "dark")
        # Bloquer toutes les cases devant (ligne 2)
        poser_piece(plateau, 2, 2, "red",    "light")
        poser_piece(plateau, 2, 3, "blue",   "light")
        poser_piece(plateau, 2, 4, "green",  "light")
        assert est_bloquee(plateau, [3, 3], "dark") is True

    def test_bloquee_bord_tableau_dark(self):
        # Une pièce dark en ligne 0 ne peut plus avancer
        plateau = plateau_vide()
        poser_piece(plateau, 0, 4, "yellow", "dark")
        assert est_bloquee(plateau, [0, 4], "dark") is True

    def test_bloquee_bord_tableau_light(self):
        # Une pièce light en ligne 7 ne peut plus avancer
        plateau = plateau_vide()
        poser_piece(plateau, 7, 4, "yellow", "light")
        assert est_bloquee(plateau, [7, 4], "light") is True


# ──────────────────────────────────────────────
#  Tests : coups_possibles
# ──────────────────────────────────────────────

class TestCoupsPossibles:
    def test_plateau_vide_milieu(self):
        plateau = plateau_vide()
        poser_piece(plateau, 4, 4, "orange", "dark")
        coups = coups_possibles(plateau, [4, 4], "dark")
        destinations = [c[1] for c in coups]
        # Vers le haut : [3,4],[2,4],[1,4],[0,4]
        assert [3, 4] in destinations
        assert [0, 4] in destinations
        # Diagonale gauche : [3,3],[2,2],[1,1],[0,0]
        assert [3, 3] in destinations
        # Diagonale droite : [3,5],[2,6],[1,7]
        assert [3, 5] in destinations

    def test_bloque_par_piece(self):
        plateau = plateau_vide()
        poser_piece(plateau, 4, 4, "orange", "dark")
        poser_piece(plateau, 3, 4, "red",    "light")  # bloque le chemin droit
        coups = coups_possibles(plateau, [4, 4], "dark")
        destinations = [c[1] for c in coups]
        # [3,4] est occupé → bloqué
        assert [3, 4] not in destinations
        # [2,4] non atteignable non plus
        assert [2, 4] not in destinations

    def test_aucun_coup_si_bloquee_partout(self):
        plateau = plateau_vide()
        poser_piece(plateau, 1, 1, "pink", "dark")
        poser_piece(plateau, 0, 0, "red",  "light")
        poser_piece(plateau, 0, 1, "blue", "light")
        poser_piece(plateau, 0, 2, "green","light")
        coups = coups_possibles(plateau, [1, 1], "dark")
        assert coups == []

    def test_light_avance_vers_le_bas(self):
        plateau = plateau_vide()
        poser_piece(plateau, 3, 3, "orange", "light")
        coups = coups_possibles(plateau, [3, 3], "light")
        destinations = [c[1] for c in coups]
        assert [4, 3] in destinations
        assert [5, 3] in destinations


# ──────────────────────────────────────────────
#  Tests : meilleur_coup
# ──────────────────────────────────────────────

class TestMeilleurCoup:
    def test_retourne_none_si_liste_vide(self):
        plateau = plateau_vide()
        assert meilleur_coup([], "dark", plateau) is None

    def test_prefere_avancer_plus_loin_dark(self):
        plateau = plateau_vide()
        poser_piece(plateau, 5, 4, "orange", "dark")
        coups = [
            [[5, 4], [4, 4]],
            [[5, 4], [3, 4]],
            [[5, 4], [1, 4]],
        ]
        coup = meilleur_coup(coups, "dark", plateau)
        # Sans pièce adverse, l'avancement prime → ligne 1
        assert coup[1][0] <= 3


# ──────────────────────────────────────────────
#  Tests : choose_move
# ──────────────────────────────────────────────

class TestChooseMove:
    def _state(self, plateau, couleur, current=0):
        return {
            "board":   plateau,
            "color":   couleur,
            "current": current,
            "players": ["A", "B"],
        }

    def test_premier_coup_retourne_un_coup(self):
        plateau = plateau_vide()
        poser_piece(plateau, 7, 0, "brown", "dark")
        state = self._state(plateau, None, current=0)
        coup = choose_move(state, 3, [])
        assert coup is not None
        assert len(coup) == 2

    def test_coup_normal_retourne_un_coup(self):
        plateau = plateau_vide()
        poser_piece(plateau, 5, 5, "orange", "dark")
        state = self._state(plateau, "orange", current=0)
        coup = choose_move(state, 3, [])
        assert coup is not None

    def test_piece_bloquee_retourne_position_identique(self):
        plateau = plateau_vide()
        poser_piece(plateau, 1, 1, "pink", "dark")
        poser_piece(plateau, 0, 0, "red",  "light")
        poser_piece(plateau, 0, 1, "blue", "light")
        poser_piece(plateau, 0, 2, "green","light")
        state = self._state(plateau, "pink", current=0)
        coup = choose_move(state, 3, [])
        assert coup == [[1, 1], [1, 1]]

    def test_retourne_none_si_piece_introuvable(self):
        plateau = plateau_vide()
        state = self._state(plateau, "red", current=0)
        coup = choose_move(state, 3, [])
        assert coup is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
