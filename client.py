import socket
import json
import struct

SERVER_HOST = "IP_DU_PROF"
SERVER_PORT = 3000
MY_PORT     = 8888
MY_NAME     = "Sabri INDUSTRY"
MATRICULES  = ["24049"]

def envoyer_message(sock, data: dict):
    
    payload = json.dumps(data).encode("utf-8")
    taille  = struct.pack(">I", len(payload))
    sock.sendall(taille + payload)

def recevoir_message(sock) -> dict:
    
    taille_brute = recevoir_exact(sock, 4)
    if not taille_brute:
        raise ConnectionError("Connexion fermée par le serveur")
    taille  = struct.unpack(">I", taille_brute)[0]
    donnees = recevoir_exact(sock, taille)
    return json.loads(donnees.decode("utf-8"))

def recevoir_exact(sock, n: int) -> bytes:
    
    buf = b""
    while len(buf) < n:
        morceau = sock.recv(n - len(buf))
        if not morceau:
            return b""
        buf += morceau
    return buf

def ma_sorte(state) -> str:
    
    return "dark" if state["current"] == 0 else "light"

def trouver_piece(plateau, couleur: str, sorte: str):
    
    for ligne in range(8):
        for colonne in range(8):
            tuile = plateau[ligne][colonne][1]
            if tuile is not None and tuile[0] == couleur and tuile[1] == sorte:
                return [ligne, colonne]
    return None

def est_bloquee(plateau, position, sorte: str) -> bool:
    
    ligne, colonne = position
    ligne_devant = ligne - 1 if sorte == "dark" else ligne + 1
    if ligne_devant < 0 or ligne_devant > 7:
        return True
    for col in range(max(colonne - 1, 0), min(colonne + 2, 8)):
        if plateau[ligne_devant][col][1] is None:
            return False
    return True

def coups_possibles(plateau, position, sorte: str) -> list:
   
    ligne, colonne = position
    direction = -1 if sorte == "dark" else 1
    coups = []
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

def score_coup(coup, plateau, sorte: str) -> int:
    
    _, destination = coup
    ligne_dest, col_dest = destination
    sorte_adverse = "light" if sorte == "dark" else "dark"
    avancement = (7 - ligne_dest) if sorte == "dark" else ligne_dest
    couleur_imposee = plateau[ligne_dest][col_dest][0]
    piece_adverse   = trouver_piece(plateau, couleur_imposee, sorte_adverse)
    penalite = 0
    if piece_adverse is not None:
        ligne_adverse = piece_adverse[0]
        penalite = (7 - ligne_adverse) if sorte_adverse == "dark" else ligne_adverse
    return avancement - penalite

def meilleur_coup(coups: list, sorte: str, plateau) -> list:
    
    if not coups:
        return None
    return max(coups, key=lambda coup: score_coup(coup, plateau, sorte))

def choose_move(state, lives: int, errors: list):
   
   
    plateau = state["board"]
    couleur = state["color"]
    sorte   = ma_sorte(state)
    if couleur is None:
        tous_les_coups = []
        for ligne in range(8):
            for colonne in range(8):
                tuile = plateau[ligne][colonne][1]
                if tuile is not None and tuile[1] == sorte:
                    position = [ligne, colonne]
                    if not est_bloquee(plateau, position, sorte):
                        coups = coups_possibles(plateau, position, sorte)
                        tous_les_coups.extend(coups)
        return meilleur_coup(tous_les_coups, sorte, plateau)
    position = trouver_piece(plateau, couleur, sorte)
    if position is None:
        return None
    if est_bloquee(plateau, position, sorte):
        return [position, position]
    coups = coups_possibles(plateau, position, sorte)
    return meilleur_coup(coups, sorte, plateau)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connexion au serveur {SERVER_HOST}:{SERVER_PORT}...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("Connecté !")
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
        print("En attente des requêtes du serveur...")
        while True:
            requete      = recevoir_message(sock)
            type_requete = requete.get("request")
            print(f"\n← Serveur : {requete}")
            if type_requete == "ping":
                envoyer_message(sock, {"response": "pong"})
                print("→ pong")
            elif type_requete == "play":
                vies    = requete.get("lives", 3)
                erreurs = requete.get("errors", [])
                state   = requete.get("state")
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


