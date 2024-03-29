#!/bin/python3
# -*- coding: utf-8 -*-

"""
    Ce que l'on peut ecrire sur le terminal depuis le dossier script :
    $ python create_final_tsv.py hankan_final.tsv
"""

import sys
import regex

def read_textgrid(chemin: str, caracter: str) :
    """ renvoie xmin et xmax

    Args:
        chemin (str): chemin vers la transcription du fichier
    """

    path_textgrid = regex.sub(r"../Corpora/MSLT_Datas/(.+?)\.T2(.+?)\.snt", r"../Corpora/MSLT_TextGrid/\1\2.TextGrid", chemin)
    with open(path_textgrid, "r") as f :
        data = f.readlines()
         
    for i, line in enumerate(data) :
        my_regex = r".+" + regex.escape(caracter) + r".+"
        if regex.match(my_regex, line) :
            
            xmin = regex.sub(r".+xmin\s=\s([0-9\.]+)\s+", r"\1", data[i-2])
            xmax = regex.sub(r".+xmax\s=\s([0-9\.]+)\s+", r"\1", data[i-1])
            
            # on modifie xmin pour prendre un peu avant sans passer dans le negatif
            xmin = round(float(xmin) - 0.005, 3)
            if xmin < 0:
                xmin = 0
                
            # on modifie xmax pour prendre un peu après sans aller au-delà de la durée audio
            xmax = round(float(xmax) + 0.005, 3)
            maxaudio = float(regex.sub(r"^xmax\s=\s([0-9.]+)\s+", r"\1", data[4]))
            if xmax > maxaudio:
                xmax = maxaudio
            
            # enfin, on aggrandit la durée du son si elle est en dessous de 100 millisecondes
            boucle = True
            while boucle:
                duree = xmax - xmin
                if duree >= 0.099:
                    boucle = False
                else :
                    ajout = round((0.100 - duree)/2, 3)
                    if (xmin - ajout) < 0:
                        xmax += ajout * 2
                    elif (xmax + ajout) > maxaudio:
                        xmin -= ajout * 2
                    else:
                        xmin -= ajout
                        xmax += ajout

            break
    
    return str(round(xmin, 3)), str(round(xmax, 3))

def new_tsv(file: list[str]) :
    """ print sur le terminal le nouveau fichier tsv

    Args:
        file (list[str]): liste des lignes du fichier tsv
    """
    for i, line in enumerate(file):
        # on change le titre
        if i == 0 :
            print("Kanji\tHanzi\tSyllabe\tModeSyl\tMode2Syl\tLieuSyl\tLabel\tDansDict\tFichierJap\tDebutJap\tFinJap\tPinyin\tModePin\tMode2Pin\tLieuPin\tFichierCh\tDebutCh\tFinCh")
        else :
            # notre ancienne ligne
            tok_line = [token for token in line.rstrip().split("\t")]
            
            # les nouveaux éléments
            DebutJap, FinJap = read_textgrid(tok_line[8], tok_line[0])
            DebutCh, FinCh = read_textgrid(tok_line[13], tok_line[1])
            
            # on insert les nouveaux éléments dans la liste
            tok_line.insert(9, DebutJap)
            tok_line.insert(10, FinJap)
            tok_line.append(DebutCh)
            tok_line.append(FinCh)

            # on imprime la nouvelle ligne
            print("\t".join(tok_line))
            

if __name__ == "__main__":
    
    chemin = sys.argv[1]
    
    with open(chemin, "r") as f :
        tsv = f.readlines()
    
    new_tsv(tsv)