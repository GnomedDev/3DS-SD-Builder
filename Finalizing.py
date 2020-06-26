import os
import shutil
import requests
from sys import platform
from codecs import encode
from zipfile import ZipFile
from distutils.dir_util import copy_tree

# Input platform on left, output on right
# Allows for easy expandablity for platform compatiblity
platform_translator = {
    "linux": "linux",
    "linux2": "linux",
    "win32": "windows",
    "darwin": "macos",
}

if not platform in platform_translator:
    current_platform = "other"
else:
    current_platform = platform_translator[platform]

# Input platform on left, (how to format the path, prompt for input())
# Again, cleans up for expandablity and probably speeds up code (also looks better).
SD_translator = {
    "windows": ("{}:/", "What drive letter is your SD Card: "),
    "macos": ("/Volumes/{}/", "What is the name of your SD Card: "),
    "linux": ("{}", "Where is your SD Card mounted (if you don't know, leave blank): ")
}

# Gnome: This makes sense to me, if it doesn't open a PR to change this and we can discuss.
SD = SD_translator[current_platform][0].format(input(SD_translator[current_platform][1]))
# Explaination: ^ get the formatting for path | ^ get the answer with the prompt in dict

def gitlatest(repo, file_name, file = 0):
    print(f"Downloading {file_name} from {repo}")

    repo1 = f"https://api.github.com/repos/{repo}/releases/latest"
    url = requests.get(repo1).json()["assets"][int(file)]["browser_download_url"]

    with open(file_name, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
        print (f"Finished downloading {file_name} from {repo}\n")

print("===== Starting download! =====\n")

gitlatest("d0k3/GodMode9", "godmode9.zip")

gitlatest("KunoichiZ/lumaupdate", "lumaupdater.cia", 1)
gitlatest("mariohackandglitch/homebrew_launcher_dummy", "homebrew_launcher.cia")
gitlatest("astronautlevel2/Anemone3DS", "anemone.cia", 1)
gitlatest("FlagBrew/Checkpoint", "checkpoint.cia", 1)
gitlatest("zoogie/DSP1", "dsp1.cia")
gitlatest("Steveice10/FBI", "fbi.cia", 1)

gitlatest("Steveice10/FBI", "fbi.3dsx")
gitlatest("ihaveamac/ctr-no-timeoffset", "ctr-no-timeoffset.3dsx")

print("===== Finished download, extracting files! =====\n")

os.mkdir("temp")

with ZipFile('godmode9.zip', 'r') as zf:
    zf.extractall('temp')
    print("Extracted Godmode9")

print("\n===== Finished extracting, moving everything into place! =====")

os.mkdir("SD Card")
os.mkdir("SD Card/cias")
os.mkdir("SD Card/3ds")
os.mkdir("SD Card/luma")
os.mkdir("SD Card/luma/payloads")

os.rename("temp/GodMode9.firm", "SD Card/luma/payloads/GodMode9.firm")
os.rename("temp/gm9", "SD Card/gm9")

files = os.listdir()
for f in files:
    if f.endswith(".cia"):
        os.rename(f, f"SD Card/cias/{f}")
    elif f.endswith(".3dsx"):
        os.rename(f, f"SD Card/3ds/{f}")

os.remove("godmode9.zip")

if current_platform in ["windows", "macos", "linux"]:
    copy_tree("SD Card", SD)
    print("\n===== Finished, your SD card is setup! =====")
    
else:
    file_paths = list()

    for root, directories, files in os.walk("SD Card"): 
        for filename in files: 
            filepath = os.path.join(root, filename) 
            file_paths.append(filepath) 
    
    with ZipFile('Extract_to_Root_of_SD_Card.zip','w') as zip: 
        for f in file_paths: 
            zip.write(f) 
    print("\n===== Finished, made the zip file! =====")

shutil.rmtree("temp", ignore_errors=True)
shutil.rmtree("SD Card", ignore_errors=True)