import os
import shutil
import requests
from sys import platform
from codecs import encode
from zipfile import ZipFile
from distutils.dir_util import copy_tree

if platform == "win32":
    current_platform = "windows"    
elif platform == "darwin":
    current_platform = "macos"
else:
    current_platform = "other"

if os.path.exists("movable.sed") is False:
    print("===== ERROR: Please download your movable.sed and place it in the same folder as this script =====")
    raise SystemExit 

if current_platform == "windows":
    SD = input("What drive letter is your SD card: ")
    if os.path.exists(f"{SD}:/Nintendo 3DS/"):
        folder = os.listdir(f"{SD}:/Nintendo 3DS/")
        if len(folder) >= 2:
            id0 = input("What is your id0: ")
            if os.path.exists(f"{SD}:/Nintendo 3DS/{id0}") is False:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/{id0} doesn't exist, make sure you put the right SD card drive letter and id0 =====")
                raise SystemExit 
        else:
            try:
                id0 = [id0 for id0 in folder][0]
            except IndexError:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/<id1> doesn't exist =====")
                raise SystemExit 

        folder = os.listdir(f"{SD}:/Nintendo 3DS/{id0}")
        if len(folder) >= 2:
            id1 = input("What is your id1 (folder inside id0): ")
            if os.path.exists(f"{SD}:/Nintendo 3DS/{id0}/{id1}") is False:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/{id0}/{id1} doesn't exist, make sure you put the right id1 =====")
                raise SystemExit 
        else:
            try:
                id1 = [id1 for id1 in folder][0]
            except IndexError:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/{id0}/<id1> doesn't exist =====")
                raise SystemExit 

    else:
        print (f"===== ERROR: {SD}:/Nintendo 3DS/ doesn't exist, make sure you put the right SD card drive letter =====")
        raise SystemExit 
        
elif current_platform == "macos":
    SD_name = input("What is the name of your SD card: ")
    SD = f"/Volumes/{SD_name}"
    if os.path.exists(f"{SD}/Nintendo 3DS/"):
        folder = os.listdir(f"{SD}/Nintendo 3DS/")
        
        # macOS creates a few "hidden" folders, including .DS_Store.
        # The following code is designed to filter such hidden folders out by checking
        # to see if the folder name starts with a "." character, which designates a
        # hidden file or folder.
        
        for hidden_folder in folder:
            if hidden_folder.startswith("."):
                folder.remove(hidden_folder)
        
        if len(folder) >= 2:
            id0 = input("What is your id0: ")
            if os.path.exists(f"{SD}/Nintendo 3DS/{id0}") is False:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/{id0} doesn't exist, make sure you put the right SD card name and id0 =====")
                raise SystemExit 
        else:
            try:
                id0 = [id0 for id0 in folder][0]
            except IndexError:
                print (f"===== ERROR: {SD}:/Nintendo 3DS/<id1> doesn't exist =====")
                raise SystemExit 

        folder = os.listdir(f"{SD}/Nintendo 3DS/{id0}")
        
        # See above for notes on hidden folders, and why this code is used.
        
        for hidden_folder in folder:
            if hidden_folder.startswith("."):
                folder.remove(hidden_folder)
        
        if len(folder) >= 2:
            id1 = input("What is your id1 (folder inside id0): ")
            if os.path.exists(f"{SD}/Nintendo 3DS/{id0}/{id1}") is False:
                print (f"===== ERROR: {SD}/Nintendo 3DS/{id0}/{id1} doesn't exist, make sure you put the right id1 =====")
                raise SystemExit 
        else:
            try:
                id1 = [id1 for id1 in folder][0]
            except IndexError:
                print (f"===== ERROR: {SD}/Nintendo 3DS/{id0}/<id1> doesn't exist =====")
                raise SystemExit 

    else:
        print (f"===== ERROR: {SD}/Nintendo 3DS/ doesn't exist, make sure you put the right SD card name =====")
        raise SystemExit 
    

else:
    id0 = input("What is your id0: ")
    id1 = input("What is your id1: ")

def extract_values(obj, key):
  arr = []
  def extract(obj, arr, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                extract(v, arr, key)
            elif k == key:
                arr.append(v)
    elif isinstance(obj, list):
        for item in obj:
            extract(item, arr, key)
    return arr
  results = extract(obj, arr, key)
  return results

def gitlatest(repo, file_name, file = 0):
    print(f"Downloading {file_name} from {repo}")
    repo1 = f"https://api.github.com/repos/{repo}/releases/latest"
    url = extract_values(requests.get(repo1).json(), 'browser_download_url')[int(file)]
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
    print(f"Finished downloading usm.zip from https://usm.bruteforcemovable.com")

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
os.mkdir(f"SD Card/Nintendo 3DS/{id0}/{id1}/Nintendo DSiware")

os.rename("temp/GodMode9.firm", "SD Card/luma/payloads/GodMode9.firm")
os.rename("temp/gm9", "SD Card/gm9")
os.rename("temp/boot.firm", "SD Card/boot.firm")
os.rename("temp/boot.3dsx", "SD Card/boot.3dsx")
os.rename("temp/usm.bin", "SD Card/usm.bin")
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


if windows:
    copy_tree("SD Card", f"{SD}:/")
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
