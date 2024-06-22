*Ce fichier peut servir à noter nos questions ou réflexions ainsi que nos avancées d'ici la fin du projet.*  

# Rôles :

## Partie Python
Florine : affichage des bobs des autres joueurs  
Yoann : envoie des infos aux autres  
Julian : Reception  
Célestine : Notion de propriété  

## Partie Reseau
Titouan : python - C & C - python  
Delong : C - C  

# Consignes
Chaque joueur à une copie locale du jeu pour visualiser la simulation et placer ses bobs/sa nourriture  
Les modifications locale des joueurs sont envoyées aux autre joueur pour qu'il mettent a jour leur copie locale  
Il est acceptable qu'un joueur voit les mouvements d'un autre avec un peu de retard  
Un joueur a acces aux caractéristiques des entitées des autres joueurs
Les entitées (bobs et nourriture) ont une propriété metier, les objets du jeu (case, bobs et nourriture) ont une propriété réseau
-Propriété métier : a qui ça appartient
-Propriete réseau : qui y a acces temporairement
Concurence sur les objets : plusieur bob ont acces aux mêmes nourriture mais attention ils ne peuvent pas manger deux fois la même nourriture

# Partie Sécurité
Pour l'IP mettre une fonction de suppression de caractère spéciaux pour pas qu'il puisse y avoir d'attaque ou qui verifie qu'il y a que des chiffre et des "."
Pour les parametres ne pouvoir mettre que des chiffres avec une valeur limitée
Utiliser des connexion sécurisé via TLS pour chiffrer les données (pour pas qu'il puisse y avoir de Man in the Midle pour modifier les valeurs des bobs par exemple.
Signatures numériques pour verifier l'intergirté et l'authenticité des messages / verifier la source des messages
Utilisation de Clé privée / Clé publique afin d'empêcher l'usurpation d'identité.
Déconnexion automatique des clients inactifs afin d'empêcher une attaque SYNC Flood.


# Notes :
## Célestine
Ce que j'ai fais : 
Faire en sorte qu'un joueur ne fasse d'action que sur ses propres bobs.
Faire en sorte que les bobs ne se mange pas dans la même équipe et ne se reproduisent pas avec l'autre équipe.
Gestion d'un set listOtherBobs qui est rempli grâce à la fonction receive de Titouan et qui permet de gerer l'affichage des bobs des autres. 
Avec titouan boucle de remplissage de la liste otherbobs et boucle d'envoie de nos bobs. 
Gestion des nourriture des autres bobs en passant par un dictionnaire entre les deux joueurs (je crois que ça à pas vrm été fait en réseau mais en théorie ça marche dans la logique du jeu)

## Florine 
J'ai créé une fonction `initiateOtherBobs` dans le fichier GameControl.py. Cette fonction servira à afficher les Bobs de l'autre joueur en modifiant l'attribut : `self.isMine`. Cela permet donc de changer la couleur des Bobs : *bleu* quand ils nous appartiennent, *vert* sinon. 

## Julian
Je me suis occupé de réalisé la partie protocol de Trame dans le réseau. La première idée étant un découpage des informations en différents envoie numérotés (saturation de la capacité de transmission d'une trame en tcp). Ces trames contenait différentes actions (Ex:'KillBob', 'MoveBob') qui permettait à chaque client de recréer le comportement des bobs des autres clients en réitérant ces actions. Cependant la mise en place étant trop compliqué, on a décidé d'envoyer directement tous nos bobs (en saturant les Trames [Estimé à 1400octets]) à chaque autre client afin de faciliter le traitement des informations. Cette solution consistait à sérialisé (conversion objets → Bytes) les bobs via le module 'pickle' puis à les désérialisé (Bytes → Objets). Néanmoins la lecture de byte indescriptible lors de l'écoute sur la communication (possiblement dû à la taille de nos buffers en C) ont rendu impossible la désérialisation. Mes collègues se sont alors rabbatus sur une solution plus simple, l'envoi de chaîne de caractère puis leur retranscription en objet.

Mes conceptions : 
Ancienne classe `packet.py`
Implémentation pre-rework de la classe `network.py` et notamment adaptation du premier programme `tcp.py` au contexte du jeu.
Ancienne méthode d'Initialisation du réseau lors du chargement du jeu.

## Yoann
J'ai travaillé en étroite collaboration avec Julian dans la partie encodage, décodage, envoi, réception et remplissage de paquet. Après que la première idée fut abandonné dû à son implémentation compliqué nous avons retenté une deuxième fois, mais de façon à ce que les informations se concaténent les unes après les autres pour les récupérer plus facilement.
De plus, je me suis occupé de tout ce qui est affichage menu 'online', tout ce qui comprend affichage create room et join room.

## Delong
Au début, j'ai réalisé la partie C à C. J'ai conçu un protocole réseau basé sur le partage de la liste IP et le TCP. Chaque joueur avait une partie réseau écrite en C, comprenant un récepteur et un émetteur. Le récepteur était un serveur TCP multithread (un thread pour gérer la liste IP, un thread pour gérer les sockets, un thread permettant de modifier l'intervalle de temps entre les envois), tandis que l'émetteur était un client possédant la liste IP et envoyant des unités de protocole à chaque joueur de la liste (similaire à une diffusion, mais en raison de mes limitations techniques, chaque envoi nécessitait une coupure de la socket).

Le récepteur du premier joueur possédait une liste IP et une fonction de diffusion, et à intervalles réguliers, il envoyait la nouvelle liste IP aux émetteurs des autres joueurs pour s'assurer que les unités de protocole étaient envoyées à tous les joueurs. Tout nouveau joueur devait connecter son émetteur au récepteur du premier joueur pour rejoindre le jeu.

Ensuite, pour aider à tester la logique, j'ai d'abord développé une partie réseau et une lecture interne du jeu entièrement en Python, utilisant des fichiers JSON comme unités de protocole pour réaliser le partage de données. Plus tard, pour éviter les incertitudes, j'ai converti cette partie réseau en C, en utilisant les fichiers JSON comme outil de communication entre le C et le Python.

