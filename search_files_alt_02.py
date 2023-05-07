import os
from tkinter import filedialog
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk

class MultipleDirectoryChooser(tk.Toplevel):
    def __init__(self, master=None, initialdir=None):
        super().__init__(master)

        self.title("Choose Directories")
        self.geometry("300x200")

        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scrollbar.set)

        self.dirs = [d for d in os.listdir(initialdir) if os.path.isdir(os.path.join(initialdir, d))]
        self.dirs.sort()

        for d in self.dirs:
            self.listbox.insert(tk.END, d)

        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(fill=tk.X)

        self.ok_button = ttk.Button(self.buttons_frame, text="OK", command=self.ok)
        self.ok_button.pack(side=tk.RIGHT)

        self.cancel_button = ttk.Button(self.buttons_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.RIGHT)

    def ok(self):
        initialdir = os.getcwd()
        self.result = [os.path.join(initialdir, self.dirs[i]) for i in self.listbox.curselection()]
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

def browse_directory(entry):
    directory = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, directory)

def browse_multiple_directories(entry):
    chooser = MultipleDirectoryChooser(app, initialdir=os.getcwd())
    app.wait_window(chooser)
    if chooser.result:
        entry.delete(0, tk.END)
        entry.insert(0, ','.join(chooser.result))

def count_files(directory, excluded_dirs):
    total_files = 0
    for root, _, files in os.walk(directory):
        if any(excluded_dir.lower() in root.lower() for excluded_dir in excluded_dirs):
            continue
        total_files += len(files)
    return total_files

def search_files(directory, extensions, excluded_dirs, pbar, found_files, files_count):
    for root, _, files in os.walk(directory):
        if any(excluded_dir.lower() in root.lower() for excluded_dir in excluded_dirs):
            continue
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                found_files.append(os.path.abspath(os.path.join(root, file)))
            pbar["value"] += 1
            app.update()
            files_count[0] += 1

def save_links_to_files(files, output_file):
    with open(output_file, 'w') as f:
        f.write('<html><head><title>File Links</title></head><body>')
        for file in files:
            f.write(f'<p><a href="file://{file}" target="_blank">{file}</a></p>')
        f.write('</body></html>')

def run_search():
    search_directory = search_dir_entry.get()
    extensions = ext_entry.get().split(',')
    excluded_dirs = excluded_dirs_entry.get().split(',')
    output_dir = output_dir_entry.get()
    output_file = os.path.join(output_dir, f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    if not search_directory or not extensions or not output_dir:
        return

    search_button.config(state=tk.DISABLED)
    total_files = count_files(search_directory, excluded_dirs)
    files_count = [0]
    found_files = []
    pbar["maximum"] = total_files
    pbar["value"] = 0

    search_thread = threading.Thread(target=search_files, args=(search_directory, extensions, excluded_dirs, pbar, found_files, files_count))
    search_thread.start()

    while search_thread.is_alive():
        app.update_idletasks()
        app.update()

    save_links_to_files(found_files, output_file)
    pbar["value"] = 0
    search_button.config(state=tk.NORMAL)
    files_found_label.config(text=f"Files found: {len(found_files)}")
    open_output_button.config(state=tk.NORMAL)

def open_output_directory():
    output_dir = output_dir_entry.get()
    if output_dir:
        os.startfile(output_dir)

app = tk.Tk()
app.title("File Searcher")
app.geometry("600x300")

search_dir_label = tk.Label(app, text="Search directory:")
search_dir_label.grid(row=0, column=0, sticky=tk.W)
search_dir_entry = tk.Entry(app, width=60)
search_dir_entry.grid(row=0, column=1)
search_dir_button = tk.Button(app, text="Browse", command=lambda: browse_directory(search_dir_entry))
search_dir_button.grid(row=0, column=2)

ext_label = tk.Label(app, text="Extensions (comma separated):")
ext_label.grid(row=1, column=0, sticky=tk.W)
ext_entry = tk.Entry(app, width=60)
ext_entry.grid(row=1, column=1)

excluded_dirs_label = tk.Label(app, text="Excluded directories (comma separated):")
excluded_dirs_label.grid(row=2, column=0, sticky=tk.W)
excluded_dirs_entry = tk.Entry(app, width=60)
excluded_dirs_entry.grid(row=2, column=1)
excluded_dirs_button = tk.Button(app, text="Browse", command=lambda: browse_multiple_directories(excluded_dirs_entry))
excluded_dirs_button.grid(row=2, column=2, padx=5, pady=5)

output_dir_label = tk.Label(app, text="Output directory:")
output_dir_label.grid(row=3, column=0, sticky=tk.W)
output_dir_entry = tk.Entry(app, width=60)
output_dir_entry.grid(row=3, column=1)
output_dir_button = tk.Button(app, text="Browse", command=lambda: browse_directory(output_dir_entry))
output_dir_button.grid(row=3, column=2, padx=5, pady=5)

search_button = tk.Button(app, text="Search", command=run_search)
search_button.grid(row=4, column=1, padx=5, pady=5)

files_found_label = tk.Label(app, text="Files found: 0")
files_found_label.grid(row=5, column=1)

pbar = ttk.Progressbar(app, mode="determinate", length=300)
pbar.grid(row=6, column=1, padx=20, pady=20)

open_output_button = tk.Button(app, text="Open output directory", command=open_output_directory, state=tk.DISABLED)
open_output_button.grid(row=7, column=1, padx=5, pady=5)

app.mainloop()
