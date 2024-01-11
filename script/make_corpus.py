#!/bin/python3

import sys
import glob
import csv
from collections import defaultdict
from xmlrpc.client import boolean
import regex
import random

# pip3 install opencc-py
import opencc # chinese converter

# pip3 install mozcpy
#import mozcpy

# pip3 install pykakasi
from pykakasi import kakasi
# module de conversion du japonais en romaji


kakasi = kakasi()
#kakasi.setMode('s', True)

import pypinyin

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
	syllabe_regex = r"(n|(a|e|i|o|u)y?(hct|hc|hs|st|tt|[bcdfghjklmprstwz])?)" # retire le n à la fin des syllabes
	# Le n est considéré comme une syllabe et ne fait plus partie de la liste des consonnes.
	# Le n sera recollé à la syllabe qui convient le mieux en fonction des mots par la suite de l'algorithme.
	#syllabe_regex = r"(n)?(oo|uu|ou|a|e|i|o|u)(y)?(hc|hs|st|[bcdfghjklmnprstwz])?" # ajoute le n à la fin des syllabes
	syllabes = regex.findall(syllabe_regex, romaji)
	syllabes = syllabes[::-1] # on remet à l'endroit l'ordre des syllabes
	#syllabes = [''.join(s) for s in syllabes] # recolle les composants de la syllabe entre eux
	syllabes = [s[0] for s in syllabes] # recolle les composants de la syllabe entre eux (pour la regex où on retire le n)
	syllabes = [s[::-1] for s in syllabes] # on remet à l'endroit les lettres dans la syllabe
	return syllabes

def get_mode_lieu_cons_jp(romaji):
	consonne = get_consonne(romaji, is_pinyin=False)
	if consonne == 'p':
		return 'occlusive', 'sourde', 'bilabiale'
	if consonne == 'b':
		return 'occlusive', 'sonore', 'bilabiale'
	if consonne == 'm':
		return 'nasale', '_', 'bilabiale'
	if consonne == 'f':
		return 'fricative', 'sourde', 'bilabiale'
	if consonne == 'v':
		return 'fricative', 'sonore', 'bilabiale'
	if consonne == 't':
		return 'occlusive', 'sourde', 'alveolaire'
	if consonne == 'd':
		return 'occlusive', 'sonore', 'alveolaire'
	if consonne == 'n':
		return 'nasale', '_', 'alveolaire'
	if consonne == 'r':
		return 'battue', '_', 'alveolaire'
	if consonne == 's':
		return 'fricative', 'sourde', 'alveolaire'
	if consonne == 'ts':
		return 'affriquee', 'sourde', 'alveolaire'
	if consonne == 'z':
		return 'affriquee', 'sonore', 'alveolaire'
	if consonne == 'sh':
		return 'fricative', 'sourde', 'alveolo-palatale' # = post-alveolar je crois
	if consonne == 'ch':
		return 'affriquee', 'sourde', 'alveolo-palatale'
	if consonne == 'j':
		return 'affriquee', 'sonore', 'alveolo-palatale'
	if consonne == 'ny':
		return 'nasal', '_', 'palatal'
	if consonne == 'y':
		return 'spirant', '_', 'palatal'
	if consonne == 'k':
		return 'occlusive', 'sourde', 'velaire'
	if consonne == 'g':
		return 'occlusive', 'sonore', 'velaire'
	if consonne == 'h':
		return 'fricative', '_', 'glottale'
	if consonne == 'hy' or consonne == "hi":
		return 'fricative', '_', 'palatale'
	else:
		return 'voyelle', '_', '_'
	#return '_', '_', '_' # si la consonne

def get_prononciation_on_kun():
	# récupération de la liste de fichiers
	path_jp = "../MSLT_Corpus/Data/MSLT_Test_JA_20170914/*T2.jp.snt"
	snt_jp = glob.glob(path_jp)
	converterJp2t = opencc.OpenCC("jp2t.json") # convertisseur de caractères japonais vers chinois traditionnel
	convertert2s = opencc.OpenCC("t2s.json") # convertisseur de caractères traditionnels vers simplifiés

	# Création du dictionnaire des on-kunyomi à partir du fichier tsv
	filename = "../onkunyomi/onkun_modif.tsv"
	onkun = read_onkun(filename)


	res = []
	for file in snt_jp:
		with open(file, 'r', encoding='UTF-16') as f:
			# TODO essayer kanjiser la string avec l'outil mozcpy avant de faire les manipulations
			# pour essayer d'avoir plus de kanjis dans le corpus

			stringJp = f.read()
			if '今早' in stringJp:
				strin = stringJp.replace('今早','_今早_')
				strin = strin.split('_')
				converted = []
				for s in strin:
					conv = kakasi.convert(s)
					if s == '今早':
						conv[0]['hepburn'] = 'ke'
						conv[1]['hepburn'] = 'sa'
					converted.extend(conv)
				#converted = kakasi.convert(stringJp)
			else:
				converted = kakasi.convert(stringJp)
			for entree in converted:
				# boucle mot par mot 
				# (malheureusement pas de possibilité d'avoir caractère par caractère avec kakasi)
				romaji = entree['hepburn']
				texte = entree['orig']
				syllabes = cut_syllabes(romaji) # on récupère les syllabes du mot
				kanjis = [] # variable de sortie
				#for c, syllabe in zip(texte, syllabes):
				#texte = texte[::-1]
				#syllabes = syllabes[::-1] # on met à l'envers pour être sûr que les suffixes auront un romaji d'au moins une syllabe
				#(exemple de 風邪 qui ne fonctionne pas car les 2 caractères se prononcent kaze, mais le 1er caractère se prononce aussi kaze)
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
						i = 4 + 3 # 4 syllabes maximum par mot en japonais; +3 pour les n indépendants (ex: 寿 a une prononciation à 7 syllabes selon ce découpage)
						if i > len(syllabes):
							i = len(syllabes)
						syllabe = ""
						ok = False
						# recherche la correspondance la plus longue possible dans onyomi puis kunyomi en regardant de 4 syllabes à 1 syllabe
						while i > 0: # 3 syllabes maximum par caractère
							syllabe = ''.join(syllabes[0:i])
							if syllabe in on:
								# TODO ajouter le type de consonne de la syllabe + le lieu d'articulation
								mode_jp, mode2_jp, lieu_jp = get_mode_lieu_cons_jp(syllabe)
								kanjis.append([c, c_chinois_simpl, syllabe, mode_jp, mode2_jp, lieu_jp, '1', '1', file])
								ok = True
								break
							elif syllabe in kuns:
								kanjis.append([c, c_chinois_simpl, syllabe, '_', '_', '_', '0', '1', file])
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
								continue
							# Si on ne fait pas cet ajout artificiel de données dans le tableau des on-kun,
							# il faut verifier qu'en faisant i = 1 ça ne crée pas de décallage sur les prochains kanjis.
							# (ce problème est rare et sera en théorie résolu si toutes les formes de romaji de nos jeux de données sont présentes
							# dans le dictionnaire des on-kun)
						# pop les syllabes qui ont été 'mangées' par le kanji
						for j in range(0, i):
							stack.append(syllabes.pop(0))
					elif is_hirakata(c):
						if c not in "ゃょーェっ" and len(syllabes) > 0: # le N (ん) n'est pas séparé par la fonction cut_syllabes, il est rattaché à une autre syllabe
							syllabe = syllabes[0:1]
							#stack.append(syllabe)
							romaji_c = kakasi.convert(c)[0]['hepburn']
							j = 0
							#i = 2
							while romaji_c != ''.join(syllabe) and j < len(syllabes):
								i = j + 1
								while romaji_c != ''.join(syllabe) and i <= len(syllabes):
								#if syllabe == 'n' and len(syllabes) > 0: # si c'est un hirakata qui commence par n
									syllabe = syllabes[j:i]
									i += 1
								j += 1
							if j == 0:
								j = 1
							syllabe_precedent = syllabes[0:j-1]
							syllabe_hirakata = syllabe
							#for i in range(0, len(syllabe_precedent)):
							#	stack.append(syllabes.pop(0))
							for s in syllabe_precedent:
								stack.append(s)
								syllabes.pop(0)
							if len(kanjis) > 0:
								# ajout des syllabes précédentes au kanji précédent
								kanjis[-1][2] += ''.join(syllabe_precedent)
							for s in syllabe_hirakata:
								stack.append(s)
								syllabes.pop(0)
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
	return res

def get_consonne(pinyin, is_pinyin:boolean=True):
	if is_pinyin:
		consonne = regex.findall(r"^([bcdefghjklmnpqrstwxyz])|(zh|ch|sh)", pinyin[0:2])
	else:
		consonne = regex.findall(r"^((ny|(hy|hi)|ch|sh|ts)|[kgsztdnhbpmyrwjfy])", pinyin[0:2])
	# w, y sont des demi-consonnes. Elles n'apparaissent pas dans le tableau des consonnes
	# du chinois.
	if len(consonne) == 0:
		return ''
	else:
		return consonne[0][0]
	return consonne
	
def get_mode_lieu(pinyin):
	consonne = get_consonne(pinyin)
	if consonne == 'p':
		return 'occlusive', 'aspiree', 'bilabiale'
	if consonne == 'b':
		return 'occlusive', 'non_aspiree', 'bilabiale'
	if consonne == 'm':
		return 'nasale', '_', 'bilabiale'
	if consonne == 'f':
		return 'fricative', 'sourde', 'labio-dentale'
	if consonne == 't':
		return 'occlusive', 'aspiree', 'dentale/alveo-dentale'
	if consonne == 'd':
		return 'occlusive', 'non_aspiree', 'dentale/alveo-dentale'
	if consonne == 'c':
		return 'affriquee', 'aspiree', 'dentale/alveo-dentale'
	if consonne == 'z':
		return 'affriquee', 'non_aspiree', 'dentale/alveo-dentale'
	if consonne == 's':
		return 'fricative', 'sourde', 'dentale/alveo-dentale'
	if consonne == 'l':
		return 'laterale', '_', 'dentale/alveo-dentale'
	if consonne == 'n':
		return 'laterale', '_', 'dentale/alveo-dentale'
	if consonne == 'ch':
		return 'affriquee', 'aspiree', 'retroflexe'
	if consonne == 'zh':
		return 'affriquee', 'non_aspiree', 'retroflexe'
	if consonne == 'sh':
		return 'fricative', 'sourde', 'retroflexe'
	if consonne == 'r':
		return 'fricative', 'sonore', 'retroflexe'
	if consonne == 'q':
		return 'affriquee', 'aspiree', 'palatale'
	if consonne == 'j':
		return 'affriquee', 'non_aspiree', 'palatale'
	if consonne == 'x':
		return 'fricative', 'sourde', 'palatale'
	if consonne == 'k':
		return 'occlusive', 'aspiree', 'velaire'
	if consonne == 'g':
		return 'occlusive', 'non_aspiree', 'velaire'
	if consonne == 'h':
		return 'fricative', 'sourde', 'velaire'
	if consonne == 'ng':
		return 'nasale', '_', 'velaire'
	if consonne == 'w' or consonne == 'y':
		return 'semi_voyelle', '_', '_'
	else:
		return 'voyelle', '_', '_'
	#return '_', '_', '_' # si la consonne n'a pas été trouvée

def get_hanzi(kanjis):
	# Etape 1: constitution d'un dictionnaire de hanzi avec une liste de fichiers pour chaque hanzi
	
	path_ch = "../MSLT_Corpus/Data/MSLT_Test_JA_20170914/*.jp.snt"
	path_ch = "../MSLT_Corpus/Data/MSLT_Test_ZH_20170914/MSLT_Test_CH_*T2.ch.snt"
	snt_ch = glob.glob(path_ch)
	dico_hanzi = {}
	for file in snt_ch:
		with open(file, 'r', encoding='UTF-16') as f:
			stringCh = f.read()
			for hanzi in stringCh:
				if not is_kanji(hanzi):
					continue
				if hanzi in dico_hanzi:
					dico_hanzi[hanzi].append(file)
				else:
					pinyin = pypinyin.pinyin(hanzi)[0][0] # le plus probable, mais il peut exister des hanzi avec plusieurs prononciations dans certains cas rares.
					mode, mode2, lieu = get_mode_lieu(pinyin)
					dico_hanzi[hanzi] = [pinyin, mode, mode2, lieu, file]
			# Ajout de : liens vers fichiers;
			# pinyin;
			# type 1ere consonne du pinyin;

	# Etape 2: ajouter un lien vers un des fichiers chinois aux kanjis
	for i, line in enumerate(kanjis):
		hanzi = line[1]
		if not hanzi in dico_hanzi:
			# Si il n'y a aucune entrée de hanzi, alors on supprime le kanji car on ne peut pas former de couple kanji-hanzi
			#del kanjis[i]
			#line.extend(['_','_','_','_','_'])
			#  cat hanzi_labels.tsv | egrep -v "_$" # enlever les kanji qui n'ont pas de hanzi
			continue
		hanzi_infos = dico_hanzi[hanzi]
		pinyin = hanzi_infos[0]
		mode = hanzi_infos[1]
		mode2 = hanzi_infos[2]
		lieu = hanzi_infos[3]
		files = hanzi_infos[4:]
		# choix au hasard d'un fichier pour ne pas avoir toujours les mêmes entrées
		file = random.choice(files)
		line.extend([pinyin, mode, mode2, lieu, file])
		#return

def write_output(res, file='kanji_label.tsv'):
	with open(file, 'w') as f:
		line0 = "Kanji\tHanzi\tSyllabe\tModeSyl\tMode2Syl\tLieuSyl\tLabel\tDansDict\tFichierJap\tPinyin\tModePin\tMode2Pin\tLieuPin\tFichierCh\n"
		f.write(line0)
		n_champs = len(line0.split('\t'))
		for line in res:
			if len(line) < n_champs:
				continue # ignore les lignes qui ne sont pas de la bonne taille
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
	res = get_prononciation_on_kun()
	get_hanzi(res)
	write_output(res, 'hanzi_labels.tsv')

if __name__ == "__main__":

	main()
