#!/bin/python3
# -*- coding: utf-8 -*-

"""
    Ce que l'on peut ecrire sur le terminal depuis le dossier script :
    $ python cut_wav_create_image.py faux_final.tsv
"""

import sys
import regex
from pydub import AudioSegment

def cut_wav(chemin: str, xmin: str, xmax: str):
    """ retourne le fichier wav découpé

    Args:
        chemin (str): chemin vers la transcription du fichier
        xmin (str): début du caractère
        xmax (str): fin du caractère

    Returns:
        AudioSegment: renvoie l'audio découpé
    """
    # transformation en miliseconde
    xmin = (float(xmin) - 0.005) * 1000
    xmax = (float(xmax) + 0.005) * 1000
    
    # on va chercher le fichier audio
    path_audio = regex.sub(r"(../MSLT_Corpus/Data/.+?)/(.+?)\.T2(.+?)\.snt", r"\1/\2.T0\3.wav", chemin)
    audio = AudioSegment.from_wav(path_audio)
    
    # puis on découpe
    return audio[xmin:xmax]

def lecture_tsv(file: list[str]):
    """ cut wav files and create spectogram

    Args:
        file (list[str]): liste des lignes du fichier tsv
    """
    for i, line in enumerate(file):
        # on passe le titre
        if i != 0 :
            # notre ligne
            tok_line = [token for token in line.rstrip().split("\t")]
            
            # label
            label = tok_line[6]
            with open (f"../data/label{i}.txt", "w") as f :
                f.write(label)
                
            # wav zh
            audio_zh = cut_wav(tok_line[15], tok_line[16], tok_line[17])
            audio_zh.export(f"../data/hanzi{i}.wav", format="wav")
            
            # wav jp
            audio_zh = cut_wav(tok_line[10], tok_line[11], tok_line[12]) # pas pu tester
            audio_zh.export(f"../data/kanji{i}.wav", format="wav")

if __name__ == "__main__":
    
    chemin = sys.argv[1]
    
    with open(chemin, "r") as f :
        tsv = f.readlines()
    
    lecture_tsv(tsv)