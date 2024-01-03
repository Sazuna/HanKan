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
			#on = {o.strip() for o in row['On'].split(';') if o.strip() !='–'}
			on = {o.strip() for o in regex.split(r";| ",row['On']) if o.strip() !='–' and len(o.strip()) > 0}
			kun = {k.strip() for k in regex.split(r";| ",row['Kun']) if k.strip() != '–' and len(k.strip()) > 0}
			# On enrichit onyomi avec la première syllabe de chaque onyomi (exemple: nichi -> ni pour nihon 日本)

			"""
			on2 = set()
			for o in on:
				on2.add(cut_syllabes(o)[0])
			on = on.union(on2)
			kun2 = set()
			for k in kun:
				kun2.add(cut_syllabes(k)[0])
			kun = kun.union(kun2)
			"""
			onkun[row['Kanji']] = {'On':on, 'Kun':kun}
			# Ancienne méthode (sans enrichissement du dictionnaire):
			#onkun[row['Kanji']] = {'On':[o.strip() for o in row['On'].split(';')],
			#			'Kun':[k.strip() for k in row['Kun'].split(';')]}
	return onkun

def cut_syllabes(romaji):
	# il faut mettre la string à l'envers pour gérer mieux les cas de ka-ni (et pas kan-i)
	romaji = romaji[::-1]
	print(romaji)
	syllabe_regex = r"(n|(oo|uu|a|e|i|o|u)y?(hc|hs|st|nn|tt|[bcdfghjklmprstwz])?)" # retire le n à la fin des syllabes
	# Le n est considéré comme une syllabe et ne fait plus partie de la liste des consonnes.
	# Le n sera recollé à la syllabe qui convient le mieux en fonction des mots par la suite de l'algorithme.
	#syllabe_regex = r"(n)?(oo|uu|ou|a|e|i|o|u)(y)?(hc|hs|st|[bcdfghjklmnprstwz])?" # ajoute le n à la fin des syllabes
	syllabes = regex.findall(syllabe_regex, romaji)
	syllabes = syllabes[::-1] # on remet à l'endroit l'ordre des syllabes
	#syllabes = [''.join(s) for s in syllabes] # recolle les composants de la syllabe entre eux
	syllabes = [s[0] for s in syllabes] # recolle les composants de la syllabe entre eux (pour la regex où on retire le n)
	syllabes = [s[::-1] for s in syllabes] # on remet à l'endroit les lettres dans la syllabe
	print(romaji, syllabes)
	return syllabes

def get_prononciation_on_kun():
	# récupération de la liste de fichiers
	path_jp = "../MSLT_Corpus/Data/MSLT_Test_JA_20170914/*.jp.snt"
	snt_jp = glob.glob(path_jp)
	converterJp2t = opencc.OpenCC("jp2t.json") # convertisseur de caractères japonais vers chinois traditionnel
	convertert2s = opencc.OpenCC("t2s.json") # convertisseur de caractères traditionnels vers simplifiés

	# Création du dictionnaire des on-kunyomi à partir du fichier tsv
	filename = "../onkunyomi/onkun_modif.tsv"
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
			#stringJp = 'じゃあ今早稲田大学に通ってるんだ。'
			#stringJp = '風邪'
			#stringJp = '丈夫' # attendu : jyoubu (joubu à cause de kakasi)
			#stringJp = '女友達'
			#stringJp = '向日葵'
			#stringJp = '朝風呂'
			#stringJp = '返、うん、返品できないのとかだと困るしね。'
			#stringJp = 'すごい、すごいじゃないけど、喧嘩もしたし。'
			#stringJp = '大体、三四十キロぐらいですかね。'
			#stringJp = 'あのー、カスじゃないけどさ。あの、塵埃 '
			#stringJp = '低い麓の所ではこのお茶の茶葉を栽培します、みたいのが決まっているんですね。'
			#stringJp = 'もう大人になるのにな、みたいな。'
			#stringJp = 'うちの夫は' # otto: problème de la double consonne
			#stringJp = 'あ、松島奈々子。'
			#stringJp = '女の子'
			#stringJp = 'あの、霧の乙女号も乗って <SPN/>'
			#stringJp = '新潟大学の学生'

			converted = kakasi.convert(stringJp)
			for entree in converted:
				# boucle mot par mot 
				# (malheureusement pas de possibilité d'avoir caractère par caractère avec kakasi)
				romaji = entree['hepburn']
				texte = entree['orig']
				syllabes = cut_syllabes(romaji) # on récupère les syllabes du mot
				print(romaji, syllabes)
				kanjis = [] # variable de sortie
				#for c, syllabe in zip(texte, syllabes):
				#texte = texte[::-1]
				#syllabes = syllabes[::-1] # on met à l'envers pour être sûr que les suffixes auront un romaji d'au moins une syllabe
				#(exemple de 風邪 qui ne fonctionne pas car les 2 caractères se prononcent kaze, mais le 1er caractère se prononce aussi kaze)
				#print("texte:",texte,"romaji:", romaji,"syllabes:", syllabes)
				stack = []
				for c in texte:
					# Associe chaque kanji à son romaji (dans le contexte)
					if is_kanji(c):
						# si les syllabes ont toutes été mangées, réutilise la dernière syllabe (exemple de 風邪 qui deviendra kaze+ze au lieu de ka+ze)
						if len(syllabes) == 0 and len(stack) > 0:
							syllabes.append(stack[-1]) # cela peut faire des doublons (réutilisations) du romaji
						c_chinois_trad = converterJp2t.convert(c)
						c_chinois_simpl = convertert2s.convert(c_chinois_trad)
						if onkun[c] == "":
							# Le kanji n'est pas présent dans onkun.
							# Les lignes ne sont pas complètes.
							syllabe = syllabes.pop(0) # une seule syllabe pour compléter (cela peut être source de bugs si le kanji fait en réalité plusieurs syllabes)
							kanjis.append([c, c_chinois_simpl, syllabe, '0', '0', file])
							continue
						on = onkun[c]['On']
						kun = onkun[c]['Kun']
						kuns = [k.split('-')[0] for k in kun]
						i = 4 + 3 # 4 syllabes maximum par mot en japonais; +3 pour les n indépendants
						if i > len(syllabes):
							i = len(syllabes)
						syllabe = ""
						ok = False
						# recherche la correspondance la plus longue possible dans onyomi puis kunyomi en regardant de 4 syllabes à 1 syllabe
						while i > 0: # 3 syllabes maximum par caractère
							syllabe = ''.join(syllabes[0:i])
							if syllabe in on:
								kanjis.append([c, c_chinois_simpl, syllabe, '1', '1', file])
								ok = True
								break
							elif syllabe in kuns:
								kanjis.append([c, c_chinois_simpl, syllabe, '0', '1', file])
								ok = True
								break
							i -= 1
						if not ok:
							# pas dans le on-yomi, ni dans le kun-yomi
							# dans ce cas les colonnes des données on-kun ne sont pas complètes
							# on peut regarder là où il y a des 0 et essayer de compléter le tableau manuellement
							# pour améliorer l'annotation (par défaut on annote à 0 tous les caractères dans ce cas :)
							j = 0
							while j < 3 and j < len(syllabes):
								j += 1 # on va scanner les syllabes plus à droite (problème de sous-syllabisation de la syllabe précédente)
								i = j + 1
								while i < 4 and i <= len(syllabes):
									syllabe = ''.join(syllabes[j:i])
									if syllabe in on:
										if len(kanjis) >= 1:
											kanjis[-1][2] += ''.join(syllabes[0:j])
										kanjis.append([c, c_chinois_simpl, syllabe, '1', '1', file])
										ok = True
										break
									elif syllabe in kuns:
										if len(kanjis) >= 1:
											kanjis[-1][2] += ''.join(syllabes[0:j])
										kanjis.append([c, c_chinois_simpl, syllabe, '0', '1', file])
										ok = True
										break
									i += 1
							i -= 1
							if not ok:
								syllabe = syllabes.pop(0)
								i = 1
								if syllabe == 'n' and len(syllabes) > 0:
									syllabe += syllabes.pop(0)
									i = 2
								kanjis.append([c, c_chinois_simpl, syllabe, '0', '0', file])
								stack.append(syllabe)
								print("syllabe = ", syllabe)
								continue
							# Si on ne fait pas cet ajout artificiel de données dans le tableau des on-kun,
							# il faut verifier qu'en faisant i = 1 ça ne crée pas de décallage sur les prochains kanjis.
							# (ce problème est rare et sera en théorie résolu si toutes les formes de romaji de nos jeux de données sont présentes
							# dans le dictionnaire des on-kun)
						# pop les syllabes qui ont été 'mangées' par le kanji
						for j in range(0, i):
							stack.append(syllabes.pop(0))
					elif is_hirakata(c):
						if c not in "ゃょーェっん" and len(syllabes) > 0: # le N (ん) n'est pas séparé par la fonction cut_syllabes, il est rattaché à une autre syllabe
							print("on enlève ",syllabes[0])
							syllabe = syllabes.pop(0)
							stack.append(syllabe)
							romaji = kakasi.convert(c)[0]['hepburn']
							while romaji != syllabe and len(syllabes) > 0:
							#if syllabe == 'n' and len(syllabes) > 0: # si c'est un hirakata qui commence par n
								syllabe += syllabes.pop(0)
								# verifier que la valeur est bien egale au romaji du hirakata
								stack.pop()
								stack.append(syllabe)
							if len(syllabes) == 0:
								break # si tout a été mangé par le hirakata
						continue
					elif c == '々':
						# diviser par 2 la syllabe précédente
						if len(kanjis) >= 1:
							k = kanjis[-1][2]
							kanjis[-1][2] = k[0:int(len(k)/2)]
				res.extend(kanjis)#[::-1]) # remise à l'endroit des kanjis
			#print(res)
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
