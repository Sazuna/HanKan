form generate_spectrogram_as_image_from_sound_file
	sentence sndFilePath /home/flo/Documents/master-TAL/M2/s1/reseau_neuronal_reconnaissance_vocale/HanKan/Corpora.zip-20240112T171417Z-001/Corpora/Processed_Datas/hanzi5219.wav
	comment Set sound file max duration to 0 to autodetect
	real soundFilesMaxDuration_seconds 0
	sentence generatedImagesFolder /home/flo/Documents/master-TAL/M2/s1/reseau_neuronal_reconnaissance_vocale/HanKan/spectrograms/
	# Spectrogram settings, see http://www.fon.hum.uva.nl/praat/manual/Sound__To_Spectrogram___.html for details
	real spectrogramWindowLength_seconds 0.005
	natural spectrogramMaxFrequency_Hz 5000
	real spectrogramTimeStep_seconds 0.002
	natural spectrogramFrequencyStep_Hz 20
	sentence spectrogramWindowShape Gaussian
	# Plotting options, see http://www.fon.hum.uva.nl/praat/manual/Intro_3_2__Configuring_the_spectrogram.html for options specific to spectrograms
	integer plottedSpectrogramMinFrequency_Hz 0
	natural plottedSpectrogramMax_dBbyHz_ratio 100
	boolean plottedSpectrogramAutoScaling 1
	natural plottedSpectrogramDynamicRange_dB 50
	natural plottedSpectrogramPreemphasis_dBbyOctave 6
	real dynamicCompression 0
	# Image size settings
	real imageWidthInches 5
	real imageHeightInches 3
endform

len = length(sndFilePath$)
lindex = index_regex(sndFilePath$, "[^/]*\.wav")
basename$ = right$(sndFilePath$, len - lindex + 1) - ".wav"

# Create target folder if needed
createDirectory: generatedImagesFolder$

# Read the sound file
currentSnd = Read from file: sndFilePath$
# Get its duration
currentSndDuration = Get total duration

# If soundFilesMaxDuration_seconds is 0 (or a negative value), set it to the duration of the provided sound file
if soundFilesMaxDuration_seconds <= 0
	soundFilesMaxDuration_seconds = currentSndDuration
endif

# Convert autoscaling option to string
if plottedSpectrogramAutoScaling=1
	plottedSpectrogramAutoScalingString$ = "yes"
else
	plottedSpectrogramAutoScalingString$ = "no"
endif

# Clean the Praat picture window from any preexisting picture
Erase all

# Get the spectrogram
currentSpectro = To Spectrogram: spectrogramWindowLength_seconds, spectrogramMaxFrequency_Hz, spectrogramTimeStep_seconds, spectrogramFrequencyStep_Hz, spectrogramWindowShape$

# Account for duration differences across sound files by adding silence at the end
zero_padding_factor = imageWidthInches / (soundFilesMaxDuration_seconds / currentSndDuration)

# Plot the spectrogram in the Praat picture window, adapting the viewport width to add final silence when needed
Select outer viewport: 0, zero_padding_factor, 0, imageHeightInches
selectObject: currentSpectro
Paint: 0, 0, plottedSpectrogramMinFrequency_Hz, spectrogramMaxFrequency_Hz, plottedSpectrogramMax_dBbyHz_ratio, plottedSpectrogramAutoScalingString$, plottedSpectrogramDynamicRange_dB, plottedSpectrogramPreemphasis_dBbyOctave, dynamicCompression, "no"

# Get back to the default "full" viewport and save the result as a PNG image
Select outer viewport: 0, imageWidthInches, 0, imageHeightInches
Save as 300-dpi PNG file: generatedImagesFolder$ + basename$ + ".png"

# Clean the Praat picture window and remove temporary objects
Erase all
removeObject: currentSnd, currentSpectro

#writeInfoLine: "Generated spectrogram image for ", basename$
#appendInfoLine: "Max duration of sound files: ", soundFilesMaxDuration_seconds, " seconds"
