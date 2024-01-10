rm *.T1.jp.snt
rm *.T3.en.snt

for file in *.wav
do
	basename=$(basename -s .T0.jp.wav $file)
	mv $file $basename.wav
done

for file in *.T1.ch.snt
do
	basename=$(basename -s .T2.jp.snt $file)
	iconv -f utf-16 -t utf-8 -o $basename.snt $file 
done

# mfa align --clean --single_speaker ./TEST_JAP japanese_mfa japanese_mfa ./TEST_JAP_OUTPUT