#!/bin/bash

repertoire_source=$1
repertoire_cible=$2
# code langue = ch ou jp
code_langue=$3

if [ -d $repertoire_source ] && [ -d $repertoire_cible ]; then
    for fichier in $repertoire_source*.T0.$code_langue.wav; do
        cp "$fichier" "$repertoire_cible"
        basename=$(basename $fichier)
        nouveau_nom="${basename//T0./}"
        
        # On se déplace dans le répertoire cible parce que le mv "$repertoire_cible$basename.snt" "$repertoire_cible$basename.txt" ne met pas le fichier .txt dans le $repertoire_cible
        cd $repertoire_cible
        
        # On renomme le fichier pour supprimer le T2 et on transforme le .snt en .txt
        mv "$basename" "$nouveau_nom"
        
        # On retourne au répertoire d'où est exécuté le script
        cd ../..
    done
    for fichier in $repertoire_source*.T2.$code_langue.snt; do
        cp "$fichier" "$repertoire_cible"
        basename=$(basename -s .snt $fichier)
        nouveau_nom="${basename//T2./}"
        
        # On se déplace dans le répertoire cible parce que le mv "$repertoire_cible$basename.snt" "$repertoire_cible$basename.txt" ne met pas le fichier .txt dans le $repertoire_cible
        cd $repertoire_cible
        # On renomme le fichier pour supprimer le T2 et on transforme le .snt en .txt
        mv "$basename.snt" "$nouveau_nom.txt"
        # On est obligé de créer un nouveau fichier, sinon fichier vide
        iconv -f "UTF-16LE" -t "UTF-8" "$nouveau_nom.txt" > "$nouveau_nom-utf8.txt"
        
        # On supprime le fichier en UTF16-LE et on renomme le fichier en utf-8
        rm $nouveau_nom.txt
        mv $nouveau_nom-utf8.txt $nouveau_nom.txt
        
        # On ajoute un espace entre chaque caractère, on remplace tous les caractères d'espacement et de saut à la ligne par un espace, on remplace les espaces multiples par un seul espace puis on supprime le caractère invisible indiquant little-endian, conservé malgé la conversion, ainsi que l'espace qui le suit en début de fichier
        cat $nouveau_nom.txt | perl -C -pe 's/(.)/$1 /g' | perl -C -pe 's/\s/ /g'  | perl -C -pe 's/\s+/ /g' | cut -c 5- > $nouveau_nom-propre.txt

        rm $nouveau_nom.txt
        mv $nouveau_nom-propre.txt $nouveau_nom.txt
        # On retourne au répertoire d'où est exécuté le script
        cd ../..
    done
else
    echo "Les répertoires sources ou cibles spécifiés n'existent pas."
fi

