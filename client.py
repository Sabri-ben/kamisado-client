import socket
import json
import struct

# ─── CONFIG ────────────────────────────────────────────────────────────────────
SERVER_HOST = "localhost"   # ← adresse IP du serveur du prof
SERVER_PORT = 3000          # ← port du serveur du prof
MY_PORT     = 8888          # ← port sur lequel TON client écoute
MY_NAME     = "MonEquipe"   # ← nom de ton équipe
MATRICULES  = ["12345", "67890"]  # ← vos vrais matricules

# ─── COMMUNICATION ─────────────────────────────────────────────────────────────

def envoyer_message(sock, data: dict):
    """Envoie un message JSON précédé de sa taille en 4 octets."""
    payload = json.dumps(data).encode("utf-8")
    taille  = struct.pack(">I", len(payload))
    sock.sendall(taille + payload)

def recevoir_message(sock) -> dict:
    """Reçoit un message JSON précédé de sa taille."""
    taille_brute = recevoir_exact(sock, 4)
    if not taille_brute:
        raise ConnectionError("Connexion fermée par le serveur")
    taille = struct.unpack(">I", taille_brute)[0]
    donnees = recevoir_exact(sock, taille)
    return json.loads(donnees.decode("utf-8"))

def recevoir_exact(sock, n: int) -> bytes:
    """Lit exactement n octets depuis le socket."""
    buf = b""
    while len(buf) < n:
        morceau = sock.recv(n - len(buf))
        if not morceau:
            return b""
        buf += morceau
    return buf

# ─── LOGIQUE DU JEU ────────────────────────────────────────────────────────────

def trouver_piece(plateau, couleur, sorte):
    """Trouve la position de la pièce de la couleur et sorte données."""
    for ligne in range(8):
        for colonne in range(8):
            tuile = plateau[ligne][colonne][1]
            if tuile is not None:
                if tuile[0] == couleur and tuile[1] == sorte:
                    return [ligne, colonne]
    return None

def coups_possibles(plateau, position, sorte):
    """Trouve tous les coups possibles pour une pièce."""
    ligne, colonne = position
    coups = []

    # Direction selon la sorte du joueur
    if sorte == "dark":
        direction = -1  # va vers le haut (ligne 0)
    else:
        direction = 1   # va vers le bas (ligne 7)

    # 3 directions : tout droit, diagonale gauche, diagonale droite
    for deplacement_col in [-1, 0, 1]:
        nouvelle_ligne = ligne + direction
        nouvelle_col   = colonne + deplacement_col

        # On avance case par case jusqu'à un obstacle
        while 0 <= nouvelle_ligne <= 7 and 0 <= nouvelle_col <= 7:
            # Si la case est occupée on s'arrête
            if plateau[nouvelle_ligne][nouvelle_col][1] is not None:
                break
            # Sinon c'est un coup valide
            coups.append([position, [nouvelle_ligne, nouvelle_col]])
            nouvelle_ligne += direction
            nouvelle_col   += deplacement_col

    return coups

def meilleur_coup(coups, sorte):
    """Choisit le coup qui avance le plus vers la ligne adverse."""
    if not coups:
        return None

    if sorte == "dark":
        # On veut la ligne la plus petite (aller vers 0)
        return min(coups, key=lambda coup: coup[1][0])
    else:
        # On veut la ligne la plus grande (aller vers 7)
        return max(coups, key=lambda coup: coup[1][0])

def trouver_piece(plateau, couleur, sorte):
    """Trouve la position de la pièce de la couleur et sorte données."""
    for ligne in range(8):
        for colonne in range(8):
            tuile = plateau[ligne][colonne][1]
            if tuile is not None:
                if tuile[0] == couleur and tuile[1] == sorte:
                    return [ligne, colonne]
    return None

def coups_possibles(plateau, position, sorte):
    """Trouve tous les coups possibles pour une pièce."""
    ligne, colonne = position
    coups = []
    if sorte == "dark":
        direction = -1  # va vers le haut
    else:
        direction = 1   # va vers le bas
    for deplacement_col in [-1, 0, 1]:
        nouvelle_ligne = ligne + direction
        nouvelle_col   = colonne + deplacement_col
        while 0 <= nouvelle_ligne <= 7 and 0 <= nouvelle_col <= 7:
            if plateau[nouvelle_ligne][nouvelle_col][1] is not None:
                break
            coups.append([position, [nouvelle_ligne, nouvelle_col]])
            nouvelle_ligne += direction
            nouvelle_col   += deplacement_col
    return coups

def meilleur_coup(coups, sorte):
    """Choisit le coup qui avance le plus vers la ligne adverse."""
    if not coups:
        return None
    if sorte == "dark":
        return min(coups, key=lambda coup: coup[1][0])
    else:
        return max(coups, key=lambda coup: coup[1][0])
    
def choose_move(state, lives, errors):
    """Choisit le meilleur coup à jouer."""
    plateau = state["board"]
    couleur = state["color"]
    current = state["current"]

    # Déterminer ma sorte (dark ou light)
    if current == 0:
        sorte = "dark"
    else:
        sorte = "light"

    # Premier coup : couleur est null, on commence avec brown
    if couleur is None:
        couleur = "brown"

    # Trouver la pièce à bouger
    position = trouver_piece(plateau, couleur, sorte)
    if position is None:
        return None

    # Calculer les coups possibles
    coups = coups_possibles(plateau, position, sorte)

    # Choisir le meilleur coup
    return meilleur_coup(coups, sorte)

# ─── BOUCLE PRINCIPALE ─────────────────────────────────────────────────────────

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connexion au serveur {SERVER_HOST}:{SERVER_PORT}...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("Connecté !")

        # 1. S'inscrire
        envoyer_message(sock, {
            "request":    "subscribe",
            "port":       MY_PORT,
            "name":       MY_NAME,
            "matricules": MATRICULES
        })

        reponse = recevoir_message(sock)
        print("Réponse inscription :", reponse)

        if reponse.get("response") != "ok":
            print("Erreur :", reponse.get("error"))
            return

        # 2. Boucle d'écoute
        print("En attente des requêtes du serveur...")
        while True:
            requete = recevoir_message(sock)
            type_requete = requete.get("request")
            print(f"\n← Serveur : {requete}")

            if type_requete == "ping":
                envoyer_message(sock, {"response": "pong"})
                print("→ pong")

            elif type_requete == "play":
                vies   = requete.get("lives", 3)
                erreurs = requete.get("errors", [])
                state  = requete.get("state")

                coup = choose_move(state, vies, erreurs)

                if coup is None:
                    envoyer_message(sock, {"response": "giveup"})
                    print("→ giveup")
                else:
                    envoyer_message(sock, {
                        "response": "move",
                        "move":     coup,
                        "message":  "Bonne chance !"
                    })
                    print(f"→ coup joué : {coup}")

            else:
                print(f"Requête inconnue : {type_requete}")

if __name__ == "__main__":
    main()

