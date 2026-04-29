import socket
import json
import struct

# ─── CONFIG ────────────────────────────────────────────────────────────────────
SERVER_HOST = "localhost"   # ← adresse IP du serveur du prof
SERVER_PORT = 3000          # ← port du serveur du prof (à vérifier)
MY_PORT     = 8888          # ← port sur lequel TON client écoute (pour le ping)
MY_NAME     = "MonEquipe"   # ← nom de ton équipe
MATRICULES  = ["12345", "67890"]  # ← vos matricules

# ─── COMMUNICATION ─────────────────────────────────────────────────────────────

def send_message(sock, data: dict):
    """Envoie un message JSON précédé de sa taille en 4 octets (big-endian)."""
    payload = json.dumps(data).encode("utf-8")
    size    = struct.pack(">I", len(payload))   # entier non signé 4 octets
    sock.sendall(size + payload)

def receive_message(sock) -> dict:
    """Reçoit un message JSON précédé de sa taille."""
    # 1. lire les 4 premiers octets = taille du message
    raw_size = _recv_exact(sock, 4)
    if not raw_size:
        raise ConnectionError("Connexion fermée par le serveur")
    size = struct.unpack(">I", raw_size)[0]

    # 2. lire exactement `size` octets
    raw_data = _recv_exact(sock, size)
    return json.loads(raw_data.decode("utf-8"))

def _recv_exact(sock, n: int) -> bytes:
    """Lit exactement n octets depuis le socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return b""
        buf += chunk
    return buf

# ─── LOGIQUE DU JEU ────────────────────────────────────────────────────────────

def choose_move(state, lives, errors):
    """
    C'est ici que tu mets ton IA !
    - state  : état courant du jeu (dépend du jeu)
    - lives  : nombre de vies restantes
    - errors : liste des erreurs précédentes
    Retourne le coup à jouer (format dépend du jeu).
    """
    # TODO : implémenter la logique du jeu
    # Pour l'instant on retourne None → à remplacer
    print("État du jeu :", json.dumps(state, indent=2))
    return None  # ← remplace ça par ton vrai coup

# ─── BOUCLE PRINCIPALE ─────────────────────────────────────────────────────────

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connexion au serveur {SERVER_HOST}:{SERVER_PORT}...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("Connecté !")

        # 1. S'inscrire
        send_message(sock, {
            "request":    "subscribe",
            "port":       MY_PORT,
            "name":       MY_NAME,
            "matricules": MATRICULES
        })

        response = receive_message(sock)
        print("Réponse inscription :", response)

        if response.get("response") != "ok":
            print("Erreur :", response.get("error"))
            return

        # 2. Boucle d'écoute
        print("En attente des requêtes du serveur...")
        while True:
            request = receive_message(sock)
            req_type = request.get("request")
            print(f"\n← Serveur : {request}")

            if req_type == "ping":
                send_message(sock, {"response": "pong"})
                print("→ pong")

            elif req_type == "play":
                lives  = request.get("lives", 3)
                errors = request.get("errors", [])
                state  = request.get("state")

                move = choose_move(state, lives, errors)

                if move is None:
                    # Aucun coup possible → on abandonne
                    send_message(sock, {"response": "giveup"})
                    print("→ giveup")
                else:
                    send_message(sock, {
                        "response": "move",
                        "move":     move,
                        "message":  "Bonne chance !"
                    })
                    print(f"→ move : {move}")

            else:
                print(f"Requête inconnue : {req_type}")

if __name__ == "__main__":
    main()
