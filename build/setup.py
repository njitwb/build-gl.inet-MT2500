#!/usr/bin/python3.7

from os import path
from pathlib import Path
from subprocess import run
from subprocess import call
import os
import sys
import yaml
import getopt

git_am = "am"

def copy_local_file(src,dest):
    try:
        call("cp  -r %s %s" % (src,dest), shell=True)
        return 0
    except:
        print("### copy "+src+" to "+ dest +" failed")
        return 1

def clone_tree(url,clone_dir,branch,revision):
    try:
        git_config = clone_dir + "/.git/config"
        if Path(git_config).is_file():
            print("### %s checkout is already present." %clone_dir)
        else:
            print("### Cloning or copy tree")
            Path(clone_dir).mkdir(exist_ok=True, parents=True)

            if not  url.startswith("https:") and not  url.startswith("git@"):
                print("### copy local tree")
                return copy_local_file(url+"/.",clone_dir)

            run(["git", "clone", "--recursive", url, clone_dir], check=True)
            print("### Clone done")

        if branch != "":
            print("### Checkout branch: %s"%branch)
            os.chdir(clone_dir)
            run(["git", "checkout", "origin/"+branch], check=True)
            print("### Checkout done")

        if revision != "":
            print("### Reset to Revision: %s"%revision)
            os.chdir(clone_dir)
            run(["git", "reset", "--hard", revision], check=True)
            print("### Reset done")

        return 0
    except:
        print("### Cloning the tree failed")
        return 1

def setup_tree(config, openwrt_dir):
        print("### Applying patches")

        patches_openwrt = []

        for folder in config.get("patch_folders", []):
            patch_folder = Path(TOP_DIR) / folder
            if not patch_folder.is_dir():
                print(f"Patch folder {patch_folder} not found")
                sys.exit(-1)

            print(f"Adding patches from {patch_folder}")
            patches_openwrt.extend(sorted(list(patch_folder.glob("*.patch")), key=os.path.basename))

        print(f"Found {len(patches_openwrt)} patches")

        os.chdir(openwrt_dir)
        for patch in patches_openwrt:
            try:
                run(["git", git_am, "-3", str(patch)], check=True)
            except:
                run(["git", git_am, "--abort"], check=True)
                sys.exit(-1)

        print("### Patches done")

        print("### Copying files")
        for folder in config.get("files_folders", []):
            file_folder = Path(TOP_DIR) / folder
            if not file_folder.is_dir():
                print(f"File folder {file_folder} not found")
                sys.exit(-1)

            print(f"Coping files from {file_folder}")
            call("cp -r %s/* %s" % (TOP_DIR / file_folder, openwrt_dir), shell=True)


TOP_DIR = os.getenv('TOP_DIR')
BUILD_DIR = os.getenv('BUILD_DIR')

CONFIG = TOP_DIR + "/devices/mt2500/setup_config.yml"
PROFILES = os.getenv('PROFILES')

if not sys.version_info >= (3, 6):
    print("This script requires Python 3.6 or higher!")
    print("You are using Python {}.{} by default.".format(sys.version_info.major, sys.version_info.minor))
    print("The following versions of Python3 have been installed on your system.")
    print("You can use the command 'cd /usr/bin/ && ln -sf <python3_version> python3' to change it.")
    os.system("ls -l /usr/bin/python3*")
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:", ["config="])
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

for o, a in opts:
    if o in ("-c", "--config"):
        CONFIG = a
    else:
        assert False, "unhandled option"

if not Path(CONFIG).is_file():
    print(f"Missing {CONFIG}")
    sys.exit(1)
CONFIG = yaml.safe_load(open(CONFIG))

source = CONFIG['source']
for n in source:
    if n.__contains__("name") and n.__contains__("url"):
        if n.__contains__("revision"):
            revision = n["revision"]
        else:
            revision = ""

        if n.__contains__("branch"):
            branch = n["branch"]
        else:
            branch = ""
       
        ret = clone_tree(n["url"], BUILD_DIR + "/" + n["name"], branch, revision)
        if ret != 0:
            print("### failed to clone %s"%n["name"])
            sys.exit(1)

setup_tree(CONFIG,BUILD_DIR + "/openwrt")

config_script=TOP_DIR + "/build/gen_config.py"
cmd=PROFILES.split()
cmd.insert(0, config_script)
run(cmd, check=True, cwd=BUILD_DIR+"/openwrt")
