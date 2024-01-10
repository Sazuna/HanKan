rm *.T1.ch.snt
rm *.T3.en.snt

for file in *.wav
do
	basename=$(basename -s .T0.ch.wav $file)
	mv $file $basename.wav
done

for file in *.T1.ch.snt
do
	basename=$(basename -s .T2.ch.snt $file)
	iconv -f utf-16 -t utf-8 -o $basename.snt $file 
done

# mfa align --clean --single_speaker ./TEST_ZH mandarin_mfa mandarin_mfa ./TEST_ZH_OUTPUT