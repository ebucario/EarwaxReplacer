import os
import gc
#import glob
import json
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from pydub import AudioSegment
from pathlib import Path
import shutil

# path on your system where custom sounds are located
CUSTOM_SOUNDS_BASE_PATH = Path("./New Sounds")
# can be an absolute path, e.g.
#CUSTOM_SOUNDS_BASE_PATH = Path("C:\Users\<username>\Documents\Earwax Sounds")

# path on your system to the Earwax game
# taking a wild guess for Windows. i haven't tested this, this may not work
EARWAX_BASE_PATH = Path("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Jackbox Games\\The Jackbox Party Pack 2\\games\\Earwax")
# macOS, probably:
#EARWAX_BASE_PATH = Path("~/Library/Application Support/Steam/steamapps/common/The Jackbox Party Pack 2/games/Earwax")
# and Linux:
#EARWAX_BASE_PATH = Path("~/.local/share/Steam/steamapps/common/The Jackbox Party Pack 2/games/Earwax")

# derived from the above Earwax path
AUDIO_JET_PATH = EARWAX_BASE_PATH / "content" / "EarwaxAudio.jet"
SPECTRUM_PATH = EARWAX_BASE_PATH / "content" / "EarwaxAudio" / "Spectrum"
AUDIO_PATH = EARWAX_BASE_PATH / "content" / "EarwaxAudio" / "Audio"

def getChannelScaled(ChannelData):
    # Compute the Short-Time Fourier Transform (STFT)
    frequencies, times, Zxx = stft(ChannelData, fs=fs, nperseg=64)

    # Zxx contains the complex STFT results
    # Convert to magnitude spectrum
    magnitude_spectra = np.abs(Zxx)

    # Downsample to 32 frequency values
    num_bins = 32
    current_bins = magnitude_spectra.shape[0]

    # Trim the magnitude_spectra to a size that is divisible by num_bins
    trimmed_bins = (current_bins // num_bins) * num_bins
    trimmed_magnitude_spectra = magnitude_spectra[:trimmed_bins, :]

    # Calculate bin size after trimming
    bin_size = trimmed_bins // num_bins

    # Average the magnitude spectra in bins
    reduced_magnitude_spectra = np.mean(
        trimmed_magnitude_spectra.reshape((num_bins, bin_size, -1)), axis=1)

    # Convert the reduced magnitude spectra to decibels
    # reduced_magnitude_spectra_db = 20 * np.log10(np.maximum(reduced_magnitude_spectra, 1e-10))  # Adding a small value to avoid log(0)

    max_output_val = 100
    # Scale the reduced magnitude spectra to 0-max_val range
    min_val = np.min(reduced_magnitude_spectra)
    max_val = np.max(reduced_magnitude_spectra)
    scaled_reduced_magnitude_spectra = max_output_val * \
        (reduced_magnitude_spectra - min_val) / (max_val - min_val)

    # Round the scaled values to the nearest integer and convert to integer type
    integer_scaled_reduced_magnitude_spectra = np.round(
        scaled_reduced_magnitude_spectra).astype(int)

    # Print some details
    # print("Sampling Frequency:", fs)
    # print("Original Shape of Magnitude Spectra:", magnitude_spectra.shape)
    # print("Trimmed Shape of Magnitude Spectra:", trimmed_magnitude_spectra.shape)
    # print("Reduced Shape of Magnitude Spectra:", reduced_magnitude_spectra.shape)
    # print("Frequencies Shape:", frequencies.shape)
    # print("Times Shape:", times.shape)
    # print("Reduced Magnitude Spectra in dB Shape:", reduced_magnitude_spectra_db.shape)
    # print("Scaled Reduced Magnitude Spectra Shape:", scaled_reduced_magnitude_spectra.shape)
    # print("Integer Scaled Reduced Magnitude Spectra Shape:", integer_scaled_reduced_magnitude_spectra.shape)

    return integer_scaled_reduced_magnitude_spectra

# glob for custom sounds
# only ogg files -- sorry!
custom_sounds = CUSTOM_SOUNDS_BASE_PATH.glob("*.ogg")
# convert to a list of dicts in the form {"path": Path, "id": int}[]
custom_sounds = [{"path": s, "id": i+30000} for i, s in enumerate(custom_sounds)]
# each sound needs a unique int that acts as its id. the vanilla English game
# seems to have id's starting in the 22000's up to the 25000's. i'm not sure if
# the prompts (in Earwax/content/EarwaxPrompts) use the same id-space, but they
# start in the 411000's to the 433000's. regardless, that isn't a problem until
# you are adding 400k custom sounds.
#
# the original USB3pt0/EarwaxReplacer used the bare filename without the
# extension (the "stem", in pathlib terminology) as the id, but this caused
# freezes in-game for me. maybe because i was using characters like ", ', and
# [space] in my filenames. oops!

# Find any supported non-ogg files and convert them to ogg
extension_list = ('*.mp3', '*.wav')
# create directory to move original audio files
backup_audio_path = CUSTOM_SOUNDS_BASE_PATH / 'Original Audio Files'
backup_audio_path.mkdir(exist_ok=True)
for extension in extension_list:
    for path in CUSTOM_SOUNDS_BASE_PATH.glob(extension):
        # sound: {"path": Path, "id": int}
        print(f"Converting \"{path.stem}\" to ogg")
        # use pydub to create the ogg file
        audio_filename = path.parent / (path.stem + ".ogg")
        AudioSegment.from_file(path).export(
            audio_filename, format='ogg', bitrate="64k")
        # move the original audio file to subdir
        path.rename(backup_audio_path / path.name)

# Generate a spectrum file for each audio file
for sound in custom_sounds:
    # sound: {"path": Path, "id": int}
    path = sound["path"]
    id = sound["id"]
    stem = path.stem
    wav_path = path.parent / (stem + ".wav")
    spectrum_path = SPECTRUM_PATH / (str(id) + ".jet")

    if (spectrum_path.exists()):
        print(f"Spectrum File Already Exists for \"{stem}\"")
        continue

    print(f"Generating Spectrum File for \"{stem}\"")

    # Convert ogg to wav for analysis
    try:
        audio = AudioSegment.from_file(path)
        audio = audio.set_frame_rate(1376)
        audio.export(wav_path, format='wav')

        # Analyze WAV file
        fs, Audiodata = wavfile.read(wav_path)

        # Do this spectrum analysis for each Channel
        # print(len(Audiodata.shape))
        if len(Audiodata.shape) > 1:
            # Stereo
            AudiodataLeft = Audiodata[:, 0]
            AudiodataRight = Audiodata[:, 1]
        else:
            # Copy Channel Data for Mono files
            AudiodataLeft = Audiodata
            AudiodataRight = Audiodata

        LeftData = getChannelScaled(AudiodataLeft)
        RightData = getChannelScaled(AudiodataRight)

        # Create output json for the Spectrum .jet file
        output_data = {'Refresh': 23, 'Frequencies': [], 'Peak': 100}
        for i in range(LeftData.shape[1]):
            thisRow = {'left': [], 'right': []}
            for j in range(len(LeftData)):
                # Convert the arrays to lists of native Python integers
                LeftData_list = LeftData.tolist()
                RightData_list = RightData.tolist()
                thisRow['left'].append(LeftData_list[j][i])
                thisRow['right'].append(RightData_list[j][i])
            output_data['Frequencies'].append(thisRow)

        # Write the Spectrum file
        with open(spectrum_path, 'w') as f:
            json.dump(output_data, f)
    except Exception as e:
        print(e)

    # Cleanup!
    try:
        wav_path.unlink()
    except Exception as e:
        print(e)

# another major deviation from USB3pt0/EarwaxReplacer: as it turns out, the
# EarwaxAudio.jet file is just a JSON file. the original script used a lot of
# string splicing to write out new sounds to this file, but it's a lot easier to
# just use json.load and json.dump.
audio_jet = json.load(open(AUDIO_JET_PATH))
# the type of audio_jet, in Typescript syntax (sorry!)
# audio_jet:{
#               "episodeid": int
#               "content": {
#                   "x": bool
#                   "name": str,
#                   "short": str,
#                   "id": int,
#                   "categories": str[]
#               }[]
#           }

# What these fields mean: if x is true, it will not show up when family friendly filter is on.
# name and short are the names of the sound.  name is what appears on a player's device; short is in-game.
# id is the filename without the extension.
# categories is used for a few achievements and has no bearing on how the sound is chosen by the game.
for sound in custom_sounds:
    path = sound["path"]
    id = sound["id"]
    stem = path.stem
    audio_jet["content"].append({
        "x": False,
        "name": stem,
        "short": stem,
        "id": id,
        "categories": ["household"]
    })

# indent=2 is just here to make the final file more human-readable.
# ensure_ascii is false here because it appears Earwax can read raw UTF-8 JSON
# strings just fine (and has UTF-8 curly quotes in the original anyway).
json.dump(audio_jet, open(AUDIO_JET_PATH, "w"), indent=2, ensure_ascii=False)

# finally, copy the sounds to the actual location
for sound in custom_sounds:
    path = sound["path"]
    id = sound["id"]
    destination = AUDIO_PATH / Path(f"./{id}.ogg")
    if (destination).exists():
        print(f"audio file already exists for \"{path.stem}\"")
    else:
        shutil.copy(path, destination)

print("Complete!")