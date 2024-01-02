#!/bin/python3

import sys
import glob
import csv
from collections import defaultdict
import regex

# pip3 install opencc-py
import opencc # chinese converter

# pip3 install mozcpy
#import mozcpy

# pip3 install pykakasi
from pykakasi import kakasi
# module de conversion du japonais en romaji


kakasi = kakasi()
kakasi.setMode('s', True)

def read_onkun(filename):
	onkun = defaultdict(str)
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter='\t')
		for row in reader:
			# découpage et nettoyage des entrées On et Kun
			on = {o.strip() for o in row['On'].split(';') if o.strip() !='–'}
			kun = {k.strip() for k in row['Kun'].split(';') if k.strip() != '–'}
			# On enrichit onyomi avec la première syllabe de chaque onyomi (exemple: nichi -> ni pour nihon 日本)
			on2 = set()
			for o in on:
				on2.add(cut_syllabes(o)[0])
			on = on.union(on2)
			onkun[row['Kanji']] = {'On':on, 'Kun':kun}
			# Ancienne méthode (sans enrichissement du dictionnaire):
			#onkun[row['Kanji']] = {'On':[o.strip() for o in row['On'].split(';')],
			#			'Kun':[k.strip() for k in row['Kun'].split(';')]}
	return onkun

def cut_syllabes(romaji):
	# il faut mettre la string à l'envers pour gérer mieux les cas de ka-ni (et pas kan-i)
	romaji = romaji[::-1]
	#syllabe_regex = r"(n|(oo|uu|a|e|i|o|u)y?(hc|hs|[bcdfghjklmnprstwz])?)" # retire le n à la fin des syllabes
	syllabe_regex = r"(n)?(oo|uu|a|e|i|o|u)(y)?(hc|hs|st|[bcdfghjklmnprstwz])?" # ajoute le n à la fin des syllabes
	syllabes = regex.findall(syllabe_regex, romaji)
	syllabes = syllabes[::-1] # on remet à l'endroit l'ordre des syllabes
	syllabes = [''.join(s) for s in syllabes] # recolle les composants de la syllabe entre eux
	#syllabes = [s[0] for s in syllabes] # recolle les composants de la syllabe entre eux (pour la regex où on retire le n)
	syllabes = [s[::-1] for s in syllabes] # on remet à l'endroit les lettres dans la syllabe
	return syllabes

def get_prononciation_on_kun():
	# récupération de la liste de fichiers
	path_jp = "../MSLT_Corpus/Data/MSLT_Test_JA_20170914/*.jp.snt"
	snt_jp = glob.glob(path_jp)
	converterJp2t = opencc.OpenCC("jp2t.json") # convertisseur de caractères japonais vers chinois traditionnel
	convertert2s = opencc.OpenCC("t2s.json") # convertisseur de caractères traditionnels vers simplifiés

	# Création du dictionnaire des on-kunyomi à partir du fichier tsv
	filename = "../onkunyomi/onkun.tsv"
	onkun = read_onkun(filename)


	res = []
	for file in snt_jp:
		with open(file, 'r', encoding='UTF-16') as f:
			stringJp = f.read()
			# TODO essayer kanjiser la string avec l'outil mozcpy avant de faire les manipulations
			# pour essayer d'avoir plus de kanjis dans le corpus
			# Quelques mots utilisés pour le débug
			#stringJp = '違い'
			#stringJp = '図書館'
			#stringJp = '春天'
			#stringJp = '装郵'
			#stringJp = '中'
			#stringJp = '東京'
			#stringJp = '美味しそう'
			#stringJp = '確かに。'
			#stringJp = 'はなん'
			#stringJp = 'ふーん'
			#stringJp = 'カフェイン'
			#stringJp = '日本'
			#stringJp = '注意'
			#stringJp = '地下鉄'
			#stringJp = ' 一緒に食べる'
			#stringJp = 'きゃ'

			converted = kakasi.convert(stringJp)
			for entree in converted:
				# boucle mot par mot 
				# (malheureusement pas de possibilité d'avoir caractère par caractère avec kakasi)
				romaji = entree['hepburn']
				texte = entree['orig']
				syllabes = cut_syllabes(romaji) # on récupère les syllabes du mot
				kanjis = [] # variable de sortie
				#for c, syllabe in zip(texte, syllabes):
				for c in texte:
					# Associe chaque kanji à son romaji (dans le contexte)
					if is_kanji(c):
						c_chinois_trad = converterJp2t.convert(c)
						c_chinois_simpl = convertert2s.convert(c_chinois_trad)
						if onkun[c] == "":
							# Le kanji n'est pas présent dans onkun.
							# Les lignes ne sont pas complètes.
							kanjis.append((c, c_chinois_simpl, syllabe, '0', '0', file))
							continue
						on = onkun[c]['On']
						kun = onkun[c]['Kun']
						i = 4 # 4 syllabes maximum par mot en japonais
						if i > len(syllabes):
							i = len(syllabes)
						syllabe = ""
						ok = False
						# recherche la correspondance la plus longue possible dans onyomi puis kunyomi en regardant de 4 syllabes à 1 syllabe
						while i > 0: # 3 syllabes maximum par caractère
							syllabe = ''.join(syllabes[0:i])
							if syllabe in on:
								kanjis.append((c, c_chinois_simpl, syllabe, '1', '1', file))
								ok = True
								break
							else:
								kuns = [k.split('-')[0] for k in kun]
								if syllabe in kuns:
									kanjis.append((c, c_chinois_simpl, syllabe, '0', '1', file))
									ok = True
									break
							i -= 1
						if not ok:
							# pas dans le on-yomi, ni dans le kun-yomi
							# dans ce cas les colonnes des données on-kun ne sont pas complètes
							# on peut regarder là où il y a des 0 et essayer de compléter le tableau manuellement
							# pour améliorer l'annotation (par défaut on annote à 0 tous les caractères dans ce cas :)
							kanjis.append((c, c_chinois_simpl, syllabes[0], '0', '0', file))
							i = 1
							# Si on ne fait pas cet ajout artificiel de données dans le tableau des on-kun,
							# il faut verifier qu'en faisant i = 1 ça ne crée pas de décallage sur les prochains kanjis.
							# (ce problème est rare et sera en théorie résolu si toutes les formes de romaji de nos jeux de données sont présentes
							# dans le dictionnaire des on-kun)
						# pop les syllabes qui ont été 'mangées' par le kanji
						for j in range(0, i):
							syllabes.pop(0)
					elif is_hirakata(c):
						if c not in "ーェっん" and len(syllabes) > 0: # le N (ん) n'est pas séparé par la fonction cut_syllabes, il est rattaché à une autre syllabe
							syllabes.pop(0)
						continue
				res.extend(kanjis)
			#return # arrêt à la première boucle pour le débugage

	with open("kanjis_labels.tsv", 'w') as f:
		f.write("Kanji\tHanzi\tSyllabe\tLabel\tDansDict\tFichier\n")
		for line in res:
			f.write('\t'.join(line)+'\n')

def is_kanji(char):
	"""
	Fonction qui vérifie que le caractère fait partie de la plage unicode des caractères chinois / japonais / coréen
	"""
	unicode_value = ord(char)
	return unicode_value >= ord(u"\u3300") and unicode_value <= ord(u"\u9FBF") or unicode_value >= ord(u"\uF900") and unicode_value <= ord(u"\uFAFF")

def is_hirakata(char):
	"""
	Fonction qui vérifie que le caractère fait partie de la plage unicode des hiragana ou des katakana 
	"""
	unicode_value = ord(char)
	return unicode_value >= ord(u"\u3040") and unicode_value <= ord(u"\u309F") or unicode_value >= ord(u"\u30A0") and unicode_value <= ord(u"\u30FF")

def main():
	get_prononciation_on_kun()

if __name__ == "__main__":

	main()
