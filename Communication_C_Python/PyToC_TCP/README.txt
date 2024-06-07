Communication TCP bidirectionnelle entre un programme C et un programme Py.
Fonctionnel et plutôt fiable je pense (aucun problème observé jusqu à maintenant).

Pour le faire fonctionner il faut que le programme C soit compilé (nommé tcpclient) et dans le même répertoire que le pyton. Ensuite on lance le pyton et tout fonctionne. Le C ne produit pas d'affichage graphique ou de printf dans la console, mais on peut vérifier qu'il fonctionne car retourne vers le Python chaque message que le Python lui envoie.
