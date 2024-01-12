for file in ./MSLT_TextGrid/*.jp.TextGrid
do
	bn=$(basename -s .jp.TextGrid $file)
	mv --target-directory=MSLT_Datas ./MSLT_Datas_notaligned/$bn.T0.jp.wav
	mv --target-directory=MSLT_Datas ./MSLT_Datas_notaligned/$bn.T2.jp.snt
done

for file in ./MSLT_TextGrid/*.ch.TextGrid
do
	bn=$(basename -s .ch.TextGrid $file)
	mv --target-directory=MSLT_Datas ./MSLT_Datas_notaligned/$bn.T0.ch.wav
	mv --target-directory=MSLT_Datas ./MSLT_Datas_notaligned/$bn.T2.ch.snt
done