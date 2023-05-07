import os
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading

# Not ONE SINGLE bite of this code was generated via any LLM AI ;)
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
            if pbar is not None:
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

def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(tk.END, directory)
        
def browse_directory(entry):
    directory = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, directory)
    
def browse_multiple_directories(entry):
    directories = filedialog.askdirectory(multiple=True)
    entry.delete(0, tk.END)
    entry.insert(0, ','.join)
    

def run_search():
    search_button['state'] = tk.DISABLED
    search_thread = threading.Thread(target=search_files_with_gui, daemon=True)
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

def search_files_with_gui():
    global directory, extensions, excluded_dirs, output_parent_folder
    directory = search_directory_entry.get()
    extensions = extensions_entry.get().split(',')
    excluded_dirs = excluded_dirs_entry.get().split(',')
    output_parent_folder = output_parent_folder_entry.get()

    total_files = count_files(directory, excluded_dirs)
    pbar = ttk.Progressbar(app, maximum=total_files, mode='determinate')
    pbar.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

    for _ in search_files(directory, extensions, excluded_dirs, pbar):
        pass

    pbar.destroy()

def open_output_folder():
    output_folder = create_output_folder(output_parent_folder, directory)
    os.startfile(output_folder)

# GUI stuff
app = tk.Tk()
app.title("File Search")

search_directory_label = tk.Label(app, text="Search Directory:")
search_directory_label.grid(row=0, column=0, sticky='e')
search_directory_entry = tk.Entry(app, width=50)
search_directory_entry.grid(row=0, column=1)
search_directory_button = tk.Button(app, text="Browse", command=lambda: browse_directory(search_directory_entry))
search_directory_button.grid(row=0, column=2)

extensions_label = tk.Label(app, text="File Extensions (comma-separated):")
extensions_label.grid(row=1, column=0, sticky='e')
extensions_entry = tk.Entry(app)
extensions_entry.grid(row=1, column=1)

excluded_dirs_label = tk.Label(app, text="Excluded Directories (comma-separated):")
excluded_dirs_label.grid(row=2, column=0, sticky='e')
excluded_dirs_entry = tk.Entry(app)
excluded_dirs_entry.grid(row=2, column=1)
excluded_dirs_button = tk.Button(app, text="Browse", command=lambda: browse_multiple_directories(excluded_dirs_entry))
excluded_dirs_button.grid(row=2, column=2)

output_parent_folder_label = tk.Label(app, text="Output Parent Folder:")
output_parent_folder_label.grid(row=3, column=0, sticky='e')
output_parent_folder_entry = tk.Entry(app, width=50)
output_parent_folder_entry.grid(row=3, column=1)
output_parent_folder_button = tk.Button(app, text="Browse", command=lambda: browse_directory(output_parent_folder_entry))
output_parent_folder_button.grid(row=3, column=2)

search_button = tk.Button(app, text="Search", command=run_search)
search_button.grid(row=4, column=0, columnspan=2, pady=10)

result_label = tk.Label(app, text="")
result_label.grid(row=6, column=0, columnspan=2)

open_output_button = tk.Button(app, text="Open Output Folder", command=open_output_folder, state=tk.DISABLED)
open_output_button.grid(row=7, column=0, columnspan=2, pady=10)

app.mainloop()

