import os
import shutil
import requests
from sys import platform, argv
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

if platform in platform_translator is False:
    current_platform = "other"
else:
    current_platform = platform_translator[platform]

if os.path.exists("movable.sed") is False:
    if len(argv) == 2 and os.path.exists(argv[1]) and argv[1].endswith(".sed"):
        shutil.copy2(argv[1], "movable.sed")
    else:
        print("===== ERROR: Please download your movable.sed and place it in the same folder as this script =====")
        raise SystemExit 

if current_platform in ["macos", "windows", "linux"]:
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

    if current_platform == "linux":
        if SD.endswith("/") is False and SD.endswith("\\") is False:
            SD = SD + "/"

    if len(SD) <= 1:
        current_platform = "other"

    elif os.path.exists(f"{SD}Nintendo 3DS/"):
        folder = os.listdir(f"{SD}Nintendo 3DS/")

        # macOS creates a few "hidden" folders, including .DS_Store.
        # The following code is designed to filter such hidden folders out by checking
        # to see if the folder name starts with a "." character, which designates a
        # hidden file or folder.

        for hidden_folder in folder:
            if hidden_folder.startswith("."):
                folder.remove(hidden_folder)
            elif hidden_folder.lower() == "private":
                folder.remove(hidden_folder)
            #Just in case, remove files.
            elif os.path.isfile(hidden_folder):
                folder.remove(hidden_folder)

        if len(folder) >= 2:
            id0 = input("What is your id0: ")
            if os.path.exists(f"{SD}Nintendo 3DS/{id0}") is False:
                print (f"===== ERROR: {SD}Nintendo 3DS/{id0} doesn't exist, make sure you put the right id0 =====")
                raise SystemExit 
        else:
            try:
                id0 = folder[0]
            except IndexError:
                print (f"===== ERROR: {SD}Nintendo 3DS/<id0> doesn't exist =====")
                raise SystemExit 

        folder = os.listdir(f"{SD}Nintendo 3DS/{id0}")

        # See above for notes on hidden folders, and why this code is used.
        for hidden_folder in folder:
            if hidden_folder.startswith("."):
                folder.remove(hidden_folder)
            #Just in case, remove files.
            elif os.path.isfile(hidden_folder):
                folder.remove(hidden_folder)

        if len(folder) >= 2:
            id1 = input("What is your id1 (folder inside id0): ")
            if os.path.exists(f"{SD}Nintendo 3DS/{id0}/{id1}") is False:
                print (f"===== ERROR: {SD}Nintendo 3DS/{id0}/{id1} doesn't exist, make sure you put the right id1 =====")
                raise SystemExit 
        else:
            try:
                id1 = folder[0]
            except IndexError:
                print (f"===== ERROR: {SD}Nintendo 3DS/{id0}/<id1> doesn't exist =====")
                raise SystemExit 
    else:
        print (f"===== ERROR: {SD}Nintendo 3DS/ doesn't exist, make sure you put the right SD Card drive letter =====")
        raise SystemExit 
        
else:
    id0 = input("What is your id0: ")
    id1 = input("What is your id1: ")

def gitlatest(repo, file_name, file = 0):
    print(f"Downloading {file_name} from {repo}")

    repo1 = f"https://api.github.com/repos/{repo}/releases/latest"
    url = requests.get(repo1).json()["assets"][int(file)]["browser_download_url"]

    with open(file_name, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
        print (f"Finished downloading {file_name} from {repo}\n")

print("===== Starting download! =====\n")

with open("movable.sed", "rb") as f:
    important_section = f.read()[0x110:0x120]
keyY = encode(important_section, "hex").decode("utf-8")

with open("usm.zip", "wb") as f:
    print(f"Downloading usm.zip from https://usm.bruteforcemovable.com")
    r = requests.get(f"https://usm.bruteforcemovable.com/?keyY={keyY}")
    f.write(r.content)
    print(f"Finished downloading usm.zip from https://usm.bruteforcemovable.com \n")

gitlatest("LumaTeam/Luma3DS", "luma.zip")
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

with ZipFile('usm.zip', 'r') as zf:
    zf.extractall('temp')
    print("Extracted unSAFE_MODE-bb3")

with ZipFile('godmode9.zip', 'r') as zf:
    zf.extractall('temp')
    print("Extracted Godmode9")

with ZipFile('luma.zip', 'r') as zf:
    zf.extractall('temp')
    print("Extracted Luma3DS")

print("\n===== Finished extracting, moving everything into place! =====")

os.mkdir("SD Card")
os.mkdir("SD Card/cias")
os.mkdir("SD Card/3ds")
os.mkdir("SD Card/luma")
os.mkdir("SD Card/luma/payloads")
os.mkdir(f"SD Card/Nintendo 3DS")
os.mkdir(f"SD Card/Nintendo 3DS/{id0}")
os.mkdir(f"SD Card/Nintendo 3DS/{id0}/{id1}")
os.mkdir(f"SD Card/Nintendo 3DS/{id0}/{id1}/Nintendo DSiWare")

os.rename("temp/GodMode9.firm", "SD Card/luma/payloads/GodMode9.firm")
os.rename("temp/gm9", "SD Card/gm9")
os.rename("temp/boot.firm", "SD Card/boot.firm")
os.rename("temp/boot.3dsx", "SD Card/boot.3dsx")
os.rename("temp/usm.bin", "SD Card/usm.bin")
print (os.listdir("temp"))
print (os.listdir("SD Card"))
os.rename("temp/F00D43D5.bin", f"SD Card/Nintendo 3DS/{id0}/{id1}/Nintendo DSiWare/F00D43D5.bin")

files = os.listdir()
for f in files:
    if f.endswith(".cia"):
        os.rename(f, f"SD Card/cias/{f}")
    elif f.endswith(".3dsx"):
        os.rename(f, f"SD Card/3ds/{f}")

os.remove("usm.zip")
os.remove("luma.zip")
os.remove("godmode9.zip")


if current_platform in ["windows", "macos", "linux"]:
    copy_tree("SD Card", SD)
    print("\n===== Finished, your SD Card is setup! =====")
    
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