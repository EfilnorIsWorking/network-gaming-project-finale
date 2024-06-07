Communication UDP bidirectionnelle entre un programme C et un programme Py.
Fonctionnelle mais pas très fiable (si vous le testez vous allez voir qu'il y a quelques messages envoyés qui n'ont pas de retour).

Pour le faire fonctionner il faut que le programme C soit compilé (nommé udpclient) et dans le même répertoire que le pyton. Ensuite on lance le pyton et tout fonctionne. Le C ne produit pas d'affichage graphique ou de printf dans la console, mais on peut vérifier qu'il fonctionne car retourne vers le Python chaque message que le Python lui envoie.
