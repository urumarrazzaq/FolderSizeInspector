import os
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, END, Entry, StringVar

# Constants
DEFAULT_SIZE_LIMIT = 25  # Default size limit in MB
OUTPUT_FILE = "Skipped Files.txt"

def list_large_files(directory, size_limit):
    size_limit_bytes = size_limit * 1024 * 1024  # Convert MB to bytes
    large_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            if file_size > size_limit_bytes:
                large_files.append(file_path)
    return large_files

def save_to_file(file_list):
    with open(OUTPUT_FILE, "w") as f:
        for file in file_list:
            f.write(file + "\n")

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        folder_path.set(directory)
        log_message(f"Selected folder: {directory}", "blue")

def run_script():
    directory = folder_path.get()
    if not directory:
        log_message("Warning: No folder selected. Please browse a directory first.", "yellow")
        return

    try:
        size_limit = float(size_limit_entry.get())
    except ValueError:
        log_message("Error: Invalid size limit. Please enter a valid number.", "red")
        return

    if size_limit <= 0:
        log_message("Error: Size limit must be greater than 0.", "red")
        return

    large_files = list_large_files(directory, size_limit)
    if large_files:
        save_to_file(large_files)
        log_message(f"Success: Found {len(large_files)} files larger than {size_limit}MB.", "green")
        for file in large_files:
            log_message(file, "black")
        log_message(f"Success: List saved to {OUTPUT_FILE}", "green")
        messagebox.showinfo("Success", f"List saved to {OUTPUT_FILE}")
    else:
        log_message(f"Info: No files larger than {size_limit}MB found.", "blue")
        messagebox.showinfo("Info", f"No files larger than {size_limit}MB found.")

def log_message(message, color):
    result_text.config(state="normal")
    result_text.insert(END, message + "\n", color)
    result_text.config(state="disabled")
    result_text.see(END)  # Scroll to the end

# Create the main window
root = Tk()
root.title("File Size Checker")
root.geometry("700x500")

# Variables
folder_path = StringVar()
size_limit = StringVar(value=str(DEFAULT_SIZE_LIMIT))

# UI Elements
Label(root, text="File Size Checker", font=("Arial", 16, "bold")).pack(pady=10)

# Size Limit Input
size_limit_frame = Label(root)
size_limit_frame.pack(pady=5)
Label(size_limit_frame, text="Size Limit (MB):", font=("Arial", 12)).pack(side="left", padx=5)
size_limit_entry = Entry(size_limit_frame, textvariable=size_limit, font=("Arial", 12), width=10)
size_limit_entry.pack(side="left", padx=5)

# Folder Selection
folder_frame = Label(root)
folder_frame.pack(pady=5)
Label(folder_frame, text="Selected Folder:", font=("Arial", 12)).pack(side="left", padx=5)
Label(folder_frame, textvariable=folder_path, font=("Arial", 12), fg="blue").pack(side="left", padx=5)
Button(folder_frame, text="Browse Directory", command=browse_directory, font=("Arial", 12)).pack(side="left", padx=5)

# Run Script Button
Button(root, text="Run Script", command=run_script, font=("Arial", 12), bg="green", fg="white").pack(pady=10)

# Logging Area
result_text = Text(root, wrap="word", font=("Arial", 10), state="disabled", height=15)
result_text.pack(fill="both", expand=True, padx=10, pady=10)

# Add color tags for logging
result_text.tag_config("black", foreground="black")
result_text.tag_config("yellow", foreground="orange")
result_text.tag_config("red", foreground="red")
result_text.tag_config("green", foreground="green")
result_text.tag_config("blue", foreground="blue")

# Scrollbar
scrollbar = Scrollbar(result_text)
scrollbar.pack(side="right", fill="y")
result_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_text.yview)

# Run the application
root.mainloop()