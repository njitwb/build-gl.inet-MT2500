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
            return 0

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
            run(["git", "checkout", "oringin/"+branch], check=True)
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

def setup_tree():
    if not config.get("wlan_ap"):
        print("copy build scripts to " +openwrt + "/scripts")
        call("cp ./scripts/openwrt/* %s" % (path.join(openwrt,"scripts")), shell=True)

    try:
        print("### Copying files")
        for folder in config.get("files_folders", []):
            file_folder = base_dir / folder
            if not file_folder.is_dir():
                print(f"File folder {file_folder} not found")
                sys.exit(-1)

            print(f"Coping files from {file_folder}")
            call("cp -r %s/* %s" % (base_dir / file_folder, git_clone_dir), shell=True)

        print("### Applying patches")

        patches = []
        patches_openwrt = []

        for folder in config.get("patch_folders", []):
            patch_folder = base_dir / folder
            if not patch_folder.is_dir():
                print(f"Patch folder {patch_folder} not found")
                sys.exit(-1)

            print(f"Adding patches from {patch_folder}")

            if patch_folder / "openwrt":
                patches_openwrt.extend(sorted(list((base_dir / folder / "openwrt").glob("*.patch")), key=os.path.basename))
                patches.extend(sorted(list((base_dir / folder).glob("*.patch")), key=os.path.basename))
            else:
                patches_openwrt.extend(sorted(list((base_dir / folder).glob("*.patch")), key=os.path.basename))

        print(f"Found {len(patches) + len(patches_openwrt)} patches")

        os.chdir(git_clone_dir)

        for patch in patches:
            run(["git", git_am, "-3", str(patch)], check=True)

        os.chdir(base_dir / openwrt)

        for patch in patches_openwrt:
            run(["git", git_am, "-3", str(patch)], check=True)

        if not Path("profiles").exists():
            os.mkdir("profiles")

        os.chdir("profiles")

        for profile in os.listdir(profiles):
            run(["ln", "-fs", path.join(profiles, profile), profile], check=True)

        os.chdir(base_dir / openwrt)

        feeds_dir = str(base_dir) + "/feeds"

        if not Path("feeds_dir").exists():
            run(
                ["ln", "-s", feeds_dir, "feeds_dir"],
                check=True,
            )

        offline_dl_dir = str(base_dir) + "/feeds/dl"

        if os.path.exists(offline_dl_dir):
            if not Path("dl").exists():
                print(f"Install offline dl folder...")
                run(
                    ["ln", "-s", offline_dl_dir, "dl"],
                    check=True,
                )
        print("### Patches done")
    except:
        print("### Setting up the tree failed")
        sys.exit(1)
    finally:
        os.chdir(base_dir)
    if  config.get("wlan_ap"):
        print("copy build scripts to " +openwrt + "/scripts")
        call("cp ./scripts/wlan-ap/* %s" % (path.join(openwrt,"scripts")), shell=True)

TOPDIR = os.getenv('TOPDIR')
BUILD_DIR = os.getenv('BUILD_DIR')

CONFIG = TOPDIR + "/etc/setup_config.yml"
PROFILE = TOPDIR + "/etc/profile_teplate.yml"

if not sys.version_info >= (3, 6):
    print("This script requires Python 3.6 or higher!")
    print("You are using Python {}.{} by default.".format(sys.version_info.major, sys.version_info.minor))
    print("The following versions of Python3 have been installed on your system.")
    print("You can use the command 'cd /usr/bin/ && ln -sf <python3_version> python3' to change it.")
    os.system("ls -l /usr/bin/python3*")
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:p", ["config=", "profile="])
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

for o, a in opts:
    if o in ("-c", "--config"):
        CONFIG = a
    elif o in ("-p", "--profile"):
        PROFILE = a
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
