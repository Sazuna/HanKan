# Données
Les données ont été récupérées sur le site [agreatdream.com](https://agreatdream.com/japanese-ministry-of-education-list-of-kanji-by-school-year-okm/).<br>
Elles sont loin d'être complètes. Cependant, grace au script make_corpus.py, la colonne DansDict permet de déceler les manques (que ce soit au niveau du kanji manquant ou d'un on-yomi ou kun-yomi manquant). Pour compléter efficacement le dictionnaire, on doit se servir de cette colonne et de nos connaissances du japonais. Peut-être qu'il existe une ressource en ligne (un autre dictionnaire) qui permettrait de compléter les lacunes, ou bien un site sur lequel on pourrait les scrapper ?

## Corrections manuelles 
Ces corrections sont à faire après le lancement du script onyomi_kunyomi.py pour la version finale

### Dans la colonne on-yomi:
- 本 : hon (nihon) /!\ très important

### Dans la colonne kun-yomi:
- 美 : o (oishii)
- 味 : i (oishii)
- 事 : goto (shigoto): il n'y a que 'koto', mais quand c'est dans la 2e syllabe, g -> k
- 来 : ki (kimasu), ko (qui existent dans le corpus)
