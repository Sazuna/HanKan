# Mon ordi n'est pas assez puissant pour traiter tous
# les fichier sons en même temps avec praat, les images
# étaient tronquées.
# J'ai donc fait un fichier à la fois
repocible=../spectro_processed_datas_5000Hz/
for file in ../Corpora/Processed_Datas/*.wav
do
    bn=$(basename -s .wav $file)
    imagename="$bn.png"
    if test -f "$repocible$imagename"; then
        continue
    else
        praat generate_spectrograms_as_images_from_sound_file.praat $file 0 $repocible 0.005 5000 0.002 20 Gaussian 0 100 1 50 6 0 5 3
    fi
done

