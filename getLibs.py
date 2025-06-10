import subprocess
import sys

packages = [
    "minecraft-launcher-lib",
    "requests"
]

for pkg in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])