#!/bin/python3

import regex


def get_table_content(fichier):
	entrees = []
	with open(fichier, "r") as f:
		text = f.read()
		lignes = regex.findall(r"<tr>.*?</tr>", text)
		# trouve toutes les lignes de façon non eager (?)
		for ligne in lignes:
			if regex.match(r".*Kanji.*", ligne):
				continue
			ligne = ligne.replace("&nbsp;", "")
			ligne = ligne.replace("<br>", "")
			ligne = ligne.replace("(", "")
			ligne = ligne.replace(")", "")
			col0 = regex.findall(r"(?<=<td.*>).*?(?=</td>)", ligne)[0]
			cols = regex.findall(r"(?<=<td>).*?(?=</td>)", ligne)
			kanji = col0
			onyomi = cols[0].replace("</td>", "").replace("<td>", "")
			if onyomi == "":
				onyomi = "-"
			kunyomi = cols[1].replace(r"</td>", "").replace("<td>", "")
			if kunyomi == "":
				kunyomi = "-"
			
			entrees.append((kanji, onyomi, kunyomi))
	return entrees

if __name__ == "__main__":
	#wget()
	entrees = []
	for i in range (1, 7):
		fichier = "../onkunyomi/" + str(i) + ".html"
		entrees.extend(get_table_content(fichier))

	with open("../onkunyomi/sortie.tsv", "w") as f:
		f.write("Kanji\tOn\tKun\n")
		for entree in entrees:
			f.write("\t".join(entree) + "\n")
