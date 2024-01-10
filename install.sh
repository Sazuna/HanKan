#-- le corpus
# wget https://download.microsoft.com/download/3/B/D/3BD46353-D61D-4F02-BE42-FB0E8A565825/MSLT_Corpus.zip

conda create --name hankan python=3.8
conda activate hankan

#-- partie alignement forcé

conda config --add channels conda-forge

conda install pytorch torchvision torchaudio cpuonly -c pytorch
conda install montreal-forced-aligner=2.2.17

mfa model download acoustic japanese_mfa
mfa model download dictionary japanese_mfa
mfa model download acoustic mandarin_mfa
mfa model download dictionary mandarin_mfa

#-- partie fichier tsv de Liza

pip install opencc
pip install pykakasi
pip install pypinyin