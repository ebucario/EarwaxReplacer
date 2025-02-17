# note from ebu

this is a fork of [USB3pt0/EarwaxReplacer](https://github.com/USB3pt0/EarwaxReplacer) that (subjectively) felt like a strong enough deviation from the original that submitting a PR didn't make much sense, but i still wanted to release my changes in case anyone else ran into the same issues i did.

### this version:

- uses `pathlib.Path` whenever possible instead of methods on `os` and `os.path`
- uses assigned numeric IDs for the sounds instead of sound file names
- uses `json` to parse `EarwaxAudio.jet` instead of manual string slicing

to use:

1. \[Optional\] setup a virtual environment.
   - `python -m venv .venv`
   - `. ./.venv/bin/activate` (or `./.venv/bin/activate.bat` on Windows)
1. `pip install -r requirements.txt`
1. edit `CUSTOM_SOUNDS_BASE_PATH` and `EARWAX_BASE_PATH` in `EarwaxReplacer.py` to point to appropriate folders.
1. `python EarwaxReplacer.py`

---

# EarwaxReplacer

A Python script to replace the default sounds in The Jackbox Party Pack 2's game Earwax.

This script is designed to take a folder of sounds in .ogg, .wav, or .mp3 format and create an associated spectrum waveform script file, and a new sounds script file for Earwax to load the sounds.
This was hastily made by me, for me, so it won't trim files, or change their volume, and has some caveats to follow:

1. The game will not work without spectrum files for each file, so make sure one exists for each.
2. The ThreeTwoOne.jet file in the default Spectrum folder is integral; the game WILL NOT START without it!
3. You must have the folders "New Sounds" and "Spectrum" in the directory where you have the python script.
4. There must be at least 6 sounds for every player or the game will fail to continue.
5. The script takes the filename and strips the extension from it; whatever the filename is, will be what the sound is named in-game.

# Prerequisites:

- You must have Python 3 installed and the ability to run commands through a command-line interface. Windows Python installers will ask if you want to add it to your PATH variable; choose yes.
- You must have the following modules installed: [numpy](https://numpy.org/install/), [scipy](https://scipy.org/install/), and [pydub](https://pypi.org/project/pydub/).
  Not having them installed will simply close it if run from Windows, or crash and tell you which of the three you need to install when run through command line.
- You must also have ffmpeg installed. On Windows, run the following commands after installing Python 3:
  ```
  pip install ffmpeg-downloader
  ffdl install --add-path
  ```

# How To Use:

1. Create the folders New Sounds and Spectrum wherever you have the .py script.
2. Open New Sounds and put ONLY sounds in .ogg, .wav, or .mp3 format in the folder. Trying to use any other file format than ogg with the game will softlock it, and the script will convert your .wav and .mp3 files. Give your files a reasonably descriptive filename, as the filename is what it will show up as in-game.
3. Run Earwax Replacer.py. I do it from command line, but it works fine just double clicking.
4. Copy resultant sounds, spectrum files, and EarwaxAudio.jet to the proper locations (back up the originals, leaving ThreeTwoOne.jet in the Spectrum folder intact). You will find them in The Jackbox Party Pack 2\games\Earwax\content if you downloaded from Steam.
5. Run Earwax and enjoy your modded game!

# To-Do:

1. GUI interface.
2. Allow user to select directories.
3. Allow user to rename sounds rather than use filenames.

# Possible future features:

1. Custom prompts. With an empty .ogg file for M.O.T.H.E.R.'s voice, anything can be set as a prompt. That said, I will probably make a separate script with input fields for that rather than try to wrap them both up in one script. I did have the idea of using lines from video games as prompts, and those could easily be imported as oggs...
2. Keeping some sounds from stock Earwax. That will require a full app and maybe even hardcoding their lines in, so they can be appended to the EarwaxAudio.jet. You can hack it now by opening the stock EarwaxAudio.jet and copying the lines you need. Use a code beautifier though because it is a mess only organized by id number/filename. You could also just copy the associated ogg and rename it and use this script, I guess...
