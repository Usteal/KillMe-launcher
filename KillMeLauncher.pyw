import sys
import subprocess
import os
import subprocess
import shutil
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
game_dir = os.path.join(script_dir, ".minecraft")
instances_dir = os.path.abspath(os.path.join(script_dir, "instances"))
default_path = os.path.abspath(os.path.join(script_dir, "default"))


def read_data_cfg(inst_path):
    cfg_path = os.path.join(inst_path, "data.cfg")
    if not os.path.isfile(cfg_path):
        return None, None
    with open(cfg_path, "r") as f:
        lines = f.readlines()
    hours = None
    username = None
    if len(lines) > 0:
        try:
            hours = float(lines[0].strip()) / 3600
        except ValueError:
            hours = None
    if len(lines) > 2:
        username = lines[2].strip()
    return hours, username

def track_playtime(inst_path, process):
    cfg_path = os.path.join(inst_path, "data.cfg")
    start_time = time.time()
    while process.poll() is None:  # while running
        elapsed = time.time() - start_time
        try:
            with open(cfg_path, "r") as f:
                lines = f.readlines()
            current_playtime = float(lines[0].strip())
        except Exception:
            current_playtime = 0
            lines = ["0\n"] + ["\n"]*5
        total_playtime = current_playtime + elapsed
        lines[0] = f"{total_playtime}\n"
        with open(cfg_path, "w") as f:
            f.writelines(lines)
        time.sleep(1)

def launch_instance(event):
    selection = listbox.curselection()
    if not selection:
        return
    folder = listbox.get(selection[0]).split(" | ")[0]
    inst_path = os.path.join(instances_dir, folder)
    _, username = read_data_cfg(inst_path)
    if not username:
        messagebox.showerror("Error", f"No username found in {folder}/data.cfg line 3")
        return
    launcher_path = os.path.join(inst_path, "launcher.pyw")
    if not os.path.isfile(launcher_path):
        messagebox.showerror("Error", f"launcher.pyw not found in {folder}")
        return
    process = subprocess.Popen([sys.executable, launcher_path, username])
    threading.Thread(target=track_playtime, args=(inst_path, process), daemon=True).start()

def refresh_listbox():
    listbox.delete(0, tk.END)
    if not os.path.isdir(instances_dir):
        return
    folders = [f for f in os.listdir(instances_dir) if os.path.isdir(os.path.join(instances_dir, f))]
    max_len = max((len(f) for f in folders), default=0)
    for folder in folders:
        inst_path = os.path.join(instances_dir, folder)
        hours, _ = read_data_cfg(inst_path)
        hours_str = f"{hours:.2f} hours" if hours is not None else "N/A"
        line = f"{folder.ljust(max_len)} | {hours_str.rjust(10)}"
        listbox.insert(tk.END, line)

def create_instance():
    if not os.path.isdir(default_path):
        messagebox.showerror("Error", "'default' folder not found.")
        return

    popup = tk.Toplevel(root)
    popup.title("Create New Instance")

    tk.Label(popup, text="Instance Name:").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(popup)
    name_entry.grid(row=0, column=1)

    tk.Label(popup, text="Username:").grid(row=1, column=0, sticky="w")
    nick_entry = tk.Entry(popup)
    nick_entry.grid(row=1, column=1)

    versions = minecraft_launcher_lib.utils.get_version_list()
    mc_versions = ["latest-release"] + [v["id"] for v in versions if v["type"] in ("release", "snapshot")]
    if not mc_versions:
        mc_versions = ["latest-release"]

    tk.Label(popup, text="MC Version:").grid(row=2, column=0, sticky="w")
    mc_var = tk.StringVar(value=mc_versions[0])
    mc_dropdown = ttk.Combobox(popup, textvariable=mc_var, values=mc_versions, state="readonly")
    mc_dropdown.grid(row=2, column=1)

    fabric_versions = ["None"]
    tk.Label(popup, text="Fabric Version:").grid(row=3, column=0, sticky="w")
    fabric_var = tk.StringVar(value="None")
    fabric_dropdown = ttk.Combobox(popup, textvariable=fabric_var, values=fabric_versions, state="readonly")
    fabric_dropdown.grid(row=3, column=1)

    keep_var = tk.BooleanVar(value=True)
    tk.Checkbutton(popup, text="Keep files after exit", variable=keep_var).grid(row=4, columnspan=2, sticky="w")

    def confirm():
        name = name_entry.get().strip()
        nick = nick_entry.get().strip()
        if not name or not nick:
            messagebox.showerror("Error", "Instance name and username are required.")
            return

        new_path = os.path.join(instances_dir, name)
        if os.path.exists(new_path):
            messagebox.showerror("Error", "Instance folder already exists.")
            return

        shutil.copytree(default_path, new_path)

        cfg_path = os.path.join(new_path, "data.cfg")
        lines = ["0\n"]  # playtime
        lines.append("y\n" if keep_var.get() else "n\n")
        lines.append("\n")  # unused
        lines.append(nick + "\n")
        lines.append(mc_var.get() + "\n")
        lines.append((fabric_var.get() if fabric_var.get() != "None" else "None") + "\n")

        with open(cfg_path, "w") as f:
            f.writelines(lines)

        popup.destroy()
        refresh_listbox()

    tk.Button(popup, text="Create", command=confirm).grid(row=5, columnspan=2, pady=5)

root = tk.Tk()
root.title("KillMe launcher v0.0.0")

listbox = tk.Listbox(root, width=50, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)
listbox.bind("<Double-1>", launch_instance)

tk.Button(root, text="Create New Instance", command=create_instance).pack(pady=(0, 10))

refresh_listbox()
root.mainloop()
