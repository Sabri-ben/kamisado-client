1.Présentation du projet:

Ce projet a été réalisé par Sabri Ben Yahya (24049) et Abdelouadod Kerrou (24177) dans le cadre du cours de l'UE "Projet Informatique".
L'objectif est de de ce projet créer une IA capable de jouer au jeu "Kamisado" .

Table des matières de ce README: -Qu'est-ce que Kamisado?
                                 -Comment fonctionne l'IA ?
                                 -Présentation de l'élaboration du projet
                                 -La connexion entre l'IA et le serveur
                                 -Bibliothèque utilisées 
                                 -Lancement de l'IA


2.Qu'est ce-que Kamisado?

Kamisado est un jeu de stratégie qui se joue entre 2 joueurs sur un plateau de 8 lignes X 8 colonnes, dont chaque case a une couleur précisé parmi les 8 couleurs posssible: orange,bleu,violet,rose,rouge,jaune,vert et marron.

Chaque joueur contrôle de 8 pièces (une chaque couleur), placées sur la dernière rangée de son côté du plateau au début de la partie.

Le joueur "dark", ses pièces sont noires. Il commence en ligne 7(bas) et doit atteindre la ligne 6 (haut)

Le joueur "light",ses pièces sont blanches. Il commence en ligne 0 (haut) et doit atteindre la ligne 7 (bas).

Une pièce peut avancer dans 3 directions uniquement vers l'avant:
-Tout droit: dans la même colonne
-Diagonale gauche: diagonale vers la gauche
-Diagonale droite: diagonale vers la droite

Une pièce peut avancer autant de cases qu'elle veut dans une direction,tant que le chemin est libre. Elle ne peut pas reculer ni sauter par-dessus une autre pièce.


La régle principale de Kamisado: La couleur de la case sur laquelle tu poses ta pièce détermine quelle pièce ton adversaire doit bouger au prochain tour.



Exemple : si tu poses ta pièce sur une case rouge, ton adversaire devra obligatoirement bouger sa pièce rouge au tour suivant.

Cette règle force les joueurs à penser plusieurs coups à l'avance !


Le premier joueur à atteindre n'importe quelle case de la rangée adverse  gagne la partie.


Si la pièce imposée est complètement bloquée (toutes les cases devant elle sont occupées), le joueur doit jouer un coup spécial : "rester sur place" ,c'est-à-dire envoyer la même position de départ et d'arrivée.



Au début de chaque partie, les 8 pièces de chaque joueur sont placées dans un  ordre aléatoire parmi 36 configurations prédéfinies. Cela rend chaque partie unique !

3.Comment fonctionne l'IA

Cette IA est un programme qui, à chaque tour, reçoit l'état complet du plateau et doit renvoyer le meilleur coup possible en moins de 3 secondes.

Elle suit une logique en 3 étapes :

-Trouver tous les coups possibles pour la pièce imposée
            
-Calculer un score pour chaque coup
            
-Jouer le coup avec le score le plus élevé

Étape 1 — Trouver tous les coups possibles

L'IA identifie la pièce qu'elle doit jouer (imposée par la couleur de la case du coup précédent de l'adversaire). Elle explore ensuite toutes les cases atteignables dans les 3 directions, en s'arrêtant dès qu'une pièce bloque le chemin.

Étape 2 — Évaluer chaque coup avec une fonction de score

C'est le cœur de notre stratégie. Pour chaque coup possible, on calcule un score basé sur 2 critères :

Critère 1 : Avancement vers la victoire 

Plus notre pièce se rapproche de la ligne adverse, mieux c'est.


Pour dark  → score_avancement = 7 - ligne_destination
Pour light → score_avancement = ligne_destination

Critère 2: Pénaliser l'adversaire


Après notre coup, la couleur de notre case d'arrivée impose une pièce à l'adversaire. Notre stratégie consiste à choisir une case dont la couleur force l'adversaire à jouer une pièce déja bien avancée car cette pièce a peu de cases disponibles devant elle.


pénalité   = avancement de la pièce adverse imposée
score_final = score_avancement - pénalité


Étape 3: Cas spécial-le premier coup


Au tout premier tour, aucune couleur n'est imposée. L'IA peut bouger n'importe laquelle de ses 8 pièces. Dans ce cas, elle génère tous les coups possibles pour toutes ses pièces et choisit le meilleur parmi tous.


Si la pièce imposée est bloquée, l'IA renvoie automatiquement [position, position] (rester sur place), conformément aux règles du jeu.



Une IA aléatoire choisit un coup sans réfléchir. Notre IA, elle :
-Avance toujours le plus possible vers la victoire
-Controle l'adversaire en lui imposant des positions difficiles

Ces deux critères combinés donnent un avantage systématique sur une IA aléatoire.

4.Présentation de l'élaboration du projet



projet IA BA2/
│
├── client.py          ← Script principal : toute la logique de l'IA
├── test_client.py     ← Tests automatiques (20 tests, couverture 63%)
└── README.md          ← Ce fichier de documentation


Quelle est la fonction logique du jeu?


ma_sorte(state), Retourne "dark" si current == 0, sinon "light" 

trouver_piece(plateau, couleur, sorte),Parcourt les 64 cases pour trouver la pièce demandée, retourne [ligne, colonne] ou None 

est_bloquee(plateau, position, sorte) , Vérifie si les 3 cases devant la pièce sont toutes occupées 

coups_possibles(plateau, position, sorte) , Explore les 3 directions et collecte toutes les cases vides atteignables 

score_coup(coup, plateau, sorte),Calcule le score d'un coup (avancement - pénalité adversaire) 

meilleur_coup(coups, sorte, plateau),Retourne le coup avec le score maximum 

choose_move(state, lives, errors),Fonction principale : gère premier coup, coups normaux et pièces bloquées 

main(),Ouvre la connexion TCP, s'inscrit au serveur, boucle infinie ping/play 

5.Connexion entre le serveur et l'IA

Qu'est-ce que le TCP ?

TCP est un protocole réseau , comme un tuyau fiable entre deux ordinateurs. Tout ce qu'on envoie d'un côté arrive de l'autre côté, dans l'ordre, sans perte.

Notre IA se connecte au serveur du professeur via TCP et échange des messages au format "JSON" un format texte simple pour représenter des données structurées.

Source : https://www.hostinger.com/fr/tutoriels/protocole-tcp 




```
Notre IA                          Serveur
    |                                |
    |-------- subscribe ------------>|  "Je m'appelle Sabri INDUSTRY"
    |<------- ok --------------------|  "Inscription confirmée"
    |                                |
    |<------- ping ------------------|  "Tu es toujours là ?"
    |-------- pong ---------------->|  "Oui !"
    |                                |
    |<------- play ------------------|  "C'est ton tour !"
    |-------- move ---------------->|  "Je joue [[7,3],[4,3]]"
    |                                |
         ... (jusqu'à la fin)
```

Ps: Le schéma ci-dessus (connexion IA-Serveur) a été entièrement créé par ChatGPT pour avoir une appoche visuel afin de facilité la compréhension de la logique du serveur.

Le serveur donne 3 vies par match. On perd une vie si on envoie un coup invalide. Si on perd toutes nos vies, on perd le match.

Configuration:

```python
SERVER_HOST = "IP_DU_PROF"     # Adresse IP du serveur
SERVER_PORT = 3000              # Port du serveur
MY_PORT     = 8888              # Port d'écoute de notre IA
MY_NAME     = "Kroux" # Nom dans le championnat
MATRICULES  = ["24049"] ["24177"]        # Matricules étudiants
```

Pourquoi faire des tests?

Les tests permettent de vérifier automatiquement que chaque fonction produit le bon résultat. Sans tests, on ne découvre les bugs qu'en jouant contre un vrai adversaire — trop tard !

Comment lancer des tests?

Dans le terminal,
pip install pytest pytest-cov
pytest test_client.py -v --cov=client --cov-report=term-missing


Les résulats de ces test sont

```
20 tests passés ✅  |  Couverture : 63%  |  Durée : 0.19s
```

Ces test vérifient quoi ?

| Groupe | Ce qui est testé | Tests |
|
| TestMaSorte | Joueur 0 = dark, Joueur 1 = light | 2 |
| TestTrouverPiece| Pièce trouvée, absente, mauvaise sorte, mauvaise couleur | 4 |
| TestEstBloquee | Chemin libre, bloqué par adversaires, bord du tableau | 4 |
| TestCoupsPossibles| Plateau vide, pièce bloquante, aucun coup, direction light | 4 |
| TestMeilleurCoup| Liste vide, préférence pour l'avancement | 2 |
| TestChooseMove | Premier coup, coup normal, pièce bloquée, pièce introuvable | 4 |

6.Bibliothèque utilisées


| Bibliothèque | Rôle |

| socket| Ouvre et gère la connexion TCP avec le serveur |
| json | Convertit les dictionnaires Python ↔ texte JSON |
| struct| Encode/décode la taille des messages en 4 octets binaires |

Les externes à installer sont:

| Bibliothèque | Rôle | Installation |

| pytest | Découvre et exécute automatiquement les tests | pip install pytest` |
| pytest-cov| Mesure le pourcentage de code couvert par les tests | pip install pytest-cov` |



7.Comment lancer l'IA
-Python 3.8 ou supérieur
-Être connecté au même réseau que le serveur du professeur

Puis installer:

Dans le terminale,
git clone <url_du_repo>
cd "projet IA BA2"
pip install pytest pytest-cov   # optionnel, pour les tests


Configuration:

Dans client.py, remplace "IP_DU_PROF" par la vraie adresse IP du serveur.

Démarrage:

Dans le terminal, python client.py

Pour lancer les tests:

Dans le terminal, pytest test_client.py -v --cov=client --cov-report=term-missing




