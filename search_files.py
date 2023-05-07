import os
from pathlib import Path
from datetime import datetime
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
from threading import Thread

def count_files(directory, excluded_dirs):
    total_files = 0
    for root, _, files in os.walk(directory):
        if any(excluded_dir.lower() in root.lower() for excluded_dir in excluded_dirs):
            continue
        total_files += len(files)
    return total_files

def search_files(directory, extensions, excluded_dirs, pbar):
    for root, _, files in os.walk(directory):
        if any(excluded_dir.lower() in root.lower() for excluded_dir in excluded_dirs):
            continue
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                yield os.path.abspath(os.path.join(root, file))
            if pbar:
                pbar.update(1)

def save_links_to_files(files, output_file):
    with open(output_file, 'w') as f:
        f.write('<html><head><title>File Links</title></head><body>')
        for file in files:
            f.write(f'<p><a href="file://{file}" target="_blank">{file}</a></p>')
        f.write('</body></html>')

def next_alpha_sequence(s):
    if not s:
        return 'A'
    s = list(s)
    i = len(s) - 1
    while i >= 0:
        if s[i] != 'Z':
            s[i] = chr(ord(s[i]) + 1)
            break
        else:
            s[i] = 'A'
            i -= 1
    if i < 0:
        s.insert(0, 'A')
    return ''.join(s)

def create_output_folder(directory, search_directory, folder_name='file_search_output'):
    search_directory_name = search_directory.rstrip(os.path.sep).split(os.path.sep)[-1]
    invalid_chars = '<>:"/\\|?*'
    search_directory_name = ''.join(c for c in search_directory_name if c not in invalid_chars)

    alpha_sequence = ''
    unique_folder_name = f"{folder_name}_{search_directory_name}_{alpha_sequence}"
    output_folder = os.path.join(directory, unique_folder_name)
    while os.path.exists(output_folder):
        alpha_sequence = next_alpha_sequence(alpha_sequence)
        unique_folder_name = f"{folder_name}_{search_directory_name}_{alpha_sequence}"
        output_folder = os.path.join(directory, unique_folder_name)

    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def update_progress_bar(total_files, current_files):
    progress_bar['maximum'] = total_files
    progress_bar['value'] = current_files
    app.update()

def run_search():
    search_button['state'] = tk.DISABLED
    open_output_button['state'] = tk.DISABLED
    directory = directory_entry.get()
    extensions = tuple(f".{ext.strip()}" for ext in extensions_entry.get().split(','))
    excluded_dirs = [dir_name.strip() for dir_name in excluded_dirs_entry.get().split(',') if dir_name.strip()]
    output_parent_folder = output_parent_folder_entry.get()

    total_files = count_files(directory, excluded_dirs)
    progress = 0

    def search_and_update_progress():
        nonlocal progress
        for file in search_files(directory, extensions, excluded_dirs, None):
            progress += 1
            update_progress_bar(total_files, progress)

    search_thread = Thread(target=search_and_update_progress)
    search_thread.start()

    while search_thread.is_alive():
        app.update()

    found_files = list(search_files(directory, extensions, excluded_dirs, None))

    if found_files:
        output_folder = create_output_folder(output_parent_folder, directory)
        output_file = os.path.join(output_folder, 'links_to_files.html')
        save_links_to_files(found_files, output_file)
        result_label.config(text=f"Found {len(found_files)} file(s)")
        open_output_button['state'] = tk.NORMAL
    else:
        result_label.config(text="No matching files found.")
    search_button['state'] = tk.NORMAL

def open_output_folder():
    directory = output_parent_folder_entry.get()
    os.startfile(directory)

app = tk.Tk()
app.title("File Search")
app.resizable(False, False)

ttk.Label(app, text="Directory to search:").grid(column=0, row=0, sticky=tk.W)
directory_entry = ttk.Entry(app, width=60)
directory_entry.grid(column=1, row=0)

ttk.Label(app, text="File extensions:").grid(column=0, row=1, sticky=tk.W)
extensions_entry = ttk.Entry(app)
extensions_entry.grid(column=1, row=1)

ttk.Label(app, text="Exclude subdirectories:").grid(column=0, row=2, sticky=tk.W)
excluded_dirs_entry = ttk.Entry(app)
excluded_dirs_entry.grid(column=1, row=2)

ttk.Label(app, text="Output parent folder:").grid(column=0, row=3, sticky=tk.W)
output_parent_folder_entry = ttk.Entry(app, width=60)
output_parent_folder_entry.grid(column=1, row=3)

search_button = ttk.Button(app, text="Search", command=run_search)
search_button.grid(column=1, row=4, pady=10)

progress_label = ttk.Label(app, text="Progress:")
progress_label.grid(column=0, row=5, sticky=tk.W)
progress_bar = ttk.Progressbar(app, mode="determinate", length=200)
progress_bar.grid(column=1, row=5)

result_label = ttk.Label(app, text="")
result_label.grid(column=1, row=6)

open_output_button = ttk.Button(app, text="Open Output Folder", command=open_output_folder)
open_output_button.grid(column=1, row=7, pady=10)

app.mainloop()

