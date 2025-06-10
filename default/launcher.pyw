import subprocess
import sys
import minecraft_launcher_lib
import shutil
import sys
import os
import json
import requests
import time

# Check args
if len(sys.argv) < 2:
    print("Args needed: python launcher.py <nick> [o (online) or - (offline)] [version] [loader]")
    exit(1)

nick = sys.argv[1]

# Game dir = script folder/.minecraft
script_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(script_dir, ".minecraft")

# Version handling
if len(sys.argv) > 3:
    version_base = sys.argv[3]
else:
    version_info = minecraft_launcher_lib.utils.get_latest_version()
    version_base = version_info['release']  # Your stable non-crashing choice

if len(sys.argv) > 4:
    loader = sys.argv[4]
    version = version_base
    # version = f"{version_base}-{loader}"
else:
    version = version_base

if len(sys.argv) > 2:
    mode = sys.argv[2]
    if mode == "o":
        print("online mode not implemented")
        mode = "offline"
    else:
        mode = "offline"
else:
    mode = "offline"

if mode == "offline":
    import uuid
    fake_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, nick))
    options = {
        "username": nick,
        "uuid": fake_uuid,
        "token": "access-token",
        "jvmArguments": [],
        "launcherName": "CustomLauncher",
        "launcherVersion": "1.0",
        "gameDirectory": game_dir
    }

# install minecraft
minecraft_launcher_lib.install.install_minecraft_version(version, game_dir)

# mods
mods_src = os.path.join(script_dir, "mods")
mods_dst = os.path.join(game_dir, "mods")
os.makedirs(mods_dst, exist_ok=True)

if os.path.isdir(mods_src):
    for mod_file in os.listdir(mods_src):
        if mod_file.endswith(".jar"):
            shutil.copy2(os.path.join(mods_src, mod_file), mods_dst)

# resourcepacks
mods_src = os.path.join(script_dir, "resourcepacks")
mods_dst = os.path.join(game_dir, "resourcepacks")
os.makedirs(mods_dst, exist_ok=True)

if os.path.isdir(mods_src):
    for mod_file in os.listdir(mods_src):
        if mod_file.endswith(".zip"):
            shutil.copy2(os.path.join(mods_src, mod_file), mods_dst)

# shaders
mods_src = os.path.join(script_dir, "shaderpacks")
mods_dst = os.path.join(game_dir, "shaderpacks")
os.makedirs(mods_dst, exist_ok=True)

if os.path.isdir(mods_src):
    for mod_file in os.listdir(mods_src):
        if mod_file.endswith(".zip"):
            shutil.copy2(os.path.join(mods_src, mod_file), mods_dst)

# worlds
mods_src = os.path.join(script_dir, "saves")
mods_dst = os.path.join(game_dir, "saves")
os.makedirs(mods_dst, exist_ok=True)

if os.path.isdir(mods_src):
    for save_folder in os.listdir(mods_src):
        src_path = os.path.join(mods_src, save_folder)
        dst_path = os.path.join(mods_dst, save_folder)
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)

cmd = minecraft_launcher_lib.command.get_minecraft_command(version, game_dir, options)
subprocess.run(cmd)

# Read data.cfg second line
keep_data = False
cfg_path = os.path.join(script_dir, "data.cfg")
if os.path.isfile(cfg_path):
    with open(cfg_path, "r") as f:
        lines = f.readlines()
        if len(lines) > 1 and lines[1].strip().lower() == "y":
            keep_data = True

# At the end, decide whether to delete .minecraft
if not keep_data:
    shutil.rmtree(game_dir)