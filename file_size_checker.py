import os
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, END

# Constants
SIZE_LIMIT = 25 * 1024 * 1024  # 25MB in bytes
OUTPUT_FILE = "Skipped Files.txt"

def list_large_files(directory):
    large_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            if file_size > SIZE_LIMIT:
                large_files.append(file_path)
    return large_files

def save_to_file(file_list):
    with open(OUTPUT_FILE, "w") as f:
        for file in file_list:
            f.write(file + "\n")

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        large_files = list_large_files(directory)
        if large_files:
            save_to_file(large_files)
            result_text.delete(1.0, END)  # Clear previous content
            result_text.insert(END, f"Found {len(large_files)} files larger than 25MB:\n")
            result_text.insert(END, "\n".join(large_files))
            messagebox.showinfo("Success", f"List saved to {OUTPUT_FILE}")
        else:
            result_text.delete(1.0, END)
            result_text.insert(END, "No files larger than 25MB found.")
            messagebox.showinfo("Info", "No files larger than 25MB found.")

# Create the main window
root = Tk()
root.title("File Size Checker")
root.geometry("600x400")

# Create and place UI elements
label = Label(root, text="Select a directory to check for files larger than 25MB:", font=("Arial", 12))
label.pack(pady=10)

browse_button = Button(root, text="Browse Directory", command=browse_directory, font=("Arial", 12))
browse_button.pack(pady=10)

result_text = Text(root, wrap="word", font=("Arial", 10))
result_text.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = Scrollbar(result_text)
scrollbar.pack(side="right", fill="y")
result_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_text.yview)

# Run the application
root.mainloop()