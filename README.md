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
