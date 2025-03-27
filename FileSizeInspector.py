import os
import threading
import logging
from datetime import datetime
from tkinter import ttk, Tk, StringVar, filedialog, messagebox, END
from tkinter.scrolledtext import ScrolledText
from queue import Queue

# Constants
DEFAULT_SIZE_LIMIT = 25  # Default size limit in MB
OUTPUT_FILE = "FileSizeInspector Logs.log"  # Changed to .log extension

class FileSizeChecker:
    def __init__(self, root):
        self.root = root
        self.queue = Queue()
        self.scanning = False
        self.setup_logging()  # Initialize logging
        self.setup_ui()
        self.root.after(100, self.process_queue)
        
    def setup_logging(self):
        """Configure the logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=OUTPUT_FILE,
            filemode='w'  # Overwrite existing log file
        )
        self.logger = logging.getLogger('FileSizeChecker')
        
    def setup_ui(self):
        # Configure main window
        self.root.title("File Size Checker")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.configure(bg="#f0f0f0")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')  # More modern theme
        
        # Configure colors
        self.style.configure('.', background="#f0f0f0")
        self.style.configure('TFrame', background="#f0f0f0")
        self.style.configure('TLabel', background="#f0f0f0", font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        
        # Button styles with readable text
        self.style.map('Success.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#218838'), ('!disabled', '#28a745')])
        self.style.map('Primary.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#0069d9'), ('!disabled', '#007bff')])
        self.style.map('Danger.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#c82333'), ('!disabled', '#dc3545')])
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill='both', expand=True)
        
        # Header
        self.header = ttk.Label(self.main_frame, text="File Size Checker", style='Header.TLabel')
        self.header.pack(pady=(0, 20))
        
        # Settings frame
        self.settings_frame = ttk.Frame(self.main_frame)
        self.settings_frame.pack(fill='x', pady=(0, 20))
        
        # Size limit setting
        self.size_limit_frame = ttk.Frame(self.settings_frame)
        self.size_limit_frame.pack(side='left', padx=10, fill='x', expand=True)
        ttk.Label(self.size_limit_frame, text="Size Limit (MB):").pack(anchor='w')
        self.size_limit = StringVar(value=str(DEFAULT_SIZE_LIMIT))
        self.size_limit_entry = ttk.Entry(self.size_limit_frame, textvariable=self.size_limit, width=10)
        self.size_limit_entry.pack(anchor='w', pady=(5, 0))
        
        # Folder selection
        self.folder_frame = ttk.Frame(self.settings_frame)
        self.folder_frame.pack(side='left', padx=10, fill='x', expand=True)
        ttk.Label(self.folder_frame, text="Folder to Scan:").pack(anchor='w')
        self.folder_path = StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_path, state='readonly')
        self.folder_entry.pack(side='left', fill='x', expand=True, pady=(5, 0))
        self.browse_btn = ttk.Button(self.folder_frame, text="Browse", command=self.browse_directory, style='Primary.TButton')
        self.browse_btn.pack(side='left', padx=(5, 0), pady=(5, 0))
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill='x', pady=(0, 20))
        
        self.run_btn = ttk.Button(self.button_frame, text="Scan Files", command=self.start_scan_thread, style='Success.TButton')
        self.run_btn.pack(side='left', padx=(0, 10))
        
        self.clear_btn = ttk.Button(self.button_frame, text="Clear Logs", command=self.clear_logs, style='Danger.TButton')
        self.clear_btn.pack(side='left')
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        
        # Results frame
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.pack(fill='both', expand=True)
        
        ttk.Label(self.results_frame, text="Scan Results:").pack(anchor='w')
        
        # Logging area with scrollbar
        self.result_text = ScrolledText(self.results_frame, wrap="word", font=('Segoe UI', 10), state="disabled")
        self.result_text.pack(fill='both', expand=True, pady=(5, 0))
        
        # Add color tags for logging
        self.result_text.tag_config("black", foreground="black")
        self.result_text.tag_config("warning", foreground="#ffc107")
        self.result_text.tag_config("error", foreground="#dc3545")
        self.result_text.tag_config("success", foreground="#28a745")
        self.result_text.tag_config("info", foreground="#17a2b8")
    
    def start_scan_thread(self):
        if self.scanning:
            return
            
        directory = self.folder_path.get()
        if not directory:
            self.log_message("⚠️ Warning: No folder selected. Please browse a directory first.", "warning")
            return

        try:
            size_limit = float(self.size_limit.get())
        except ValueError:
            self.log_message("❌ Error: Invalid size limit. Please enter a valid number.", "error")
            return

        if size_limit <= 0:
            self.log_message("❌ Error: Size limit must be greater than 0.", "error")
            return
            
        self.scanning = True
        self.run_btn.config(state="disabled")
        self.progress.pack(fill='x', pady=(0, 10))
        self.progress.start()
        
        # Start scan in separate thread
        scan_thread = threading.Thread(
            target=self.run_script,
            args=(directory, size_limit),
            daemon=True
        )
        scan_thread.start()
    
    def list_large_files(self, directory, size_limit):
        size_limit_bytes = size_limit * 1024 * 1024  # Convert MB to bytes
        large_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if not self.scanning:  # Allow cancellation
                    break
                    
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > size_limit_bytes:
                        large_files.append(file_path)
                        self.queue.put(("file", file_path))
                        # Log to file
                        self.logger.info(f"Large file found: {file_path} ({file_size/1024/1024:.2f} MB)")
                except (OSError, PermissionError) as e:
                    self.queue.put(("warning", f"⚠️ Warning: Could not access file {file_path}"))
                    self.logger.warning(f"Access denied to file: {file_path} - {str(e)}")
        return large_files
    
    def save_to_file(self, file_list):
        """This is now handled by the logging system, but we keep it for backward compatibility"""
        with open(OUTPUT_FILE, "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n\n=== Scan completed at {timestamp} ===\n")
            f.write(f"Found {len(file_list)} files exceeding size limit:\n")
            for file in file_list:
                f.write(f"{file}\n")
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.folder_path.set(directory)
            self.log_message(f"ℹ️ Selected folder: {directory}", "info")
            self.logger.info(f"Selected folder: {directory}")
    
    def run_script(self, directory, size_limit):
        self.queue.put(("info", "⏳ Scanning folder..."))
        self.logger.info(f"Starting scan in directory: {directory} with size limit: {size_limit}MB")
        
        large_files = self.list_large_files(directory, size_limit)
        
        if not self.scanning:  # Scan was cancelled
            self.queue.put(("info", "ℹ️ Scan cancelled by user."))
            self.logger.info("Scan cancelled by user")
        elif large_files:
            # The logging system already captured individual files, now log summary
            self.logger.info(f"Found {len(large_files)} files larger than {size_limit}MB")
            self.save_to_file(large_files)  # Additional summary file
            self.queue.put(("success", f"✅ Success: Found {len(large_files)} files larger than {size_limit}MB."))
            self.queue.put(("success", f"✅ Success: List saved to {OUTPUT_FILE}"))
            self.queue.put(("messagebox", ("Success", f"List saved to {OUTPUT_FILE}")))
        else:
            self.logger.info(f"No files larger than {size_limit}MB found")
            self.queue.put(("info", f"ℹ️ Info: No files larger than {size_limit}MB found."))
            self.queue.put(("messagebox", ("Info", f"No files larger than {size_limit}MB found.")))
        
        self.queue.put(("complete", None))
    
    def process_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == "file":
                    self.log_message(f"  • {message[1]}", "black")
                elif message[0] == "messagebox":
                    messagebox.showinfo(message[1][0], message[1][1])
                elif message[0] == "complete":
                    self.scanning = False
                    self.run_btn.config(state="normal")
                    self.progress.stop()
                    self.progress.pack_forget()
                else:
                    self.log_message(message[1], message[0])
        except:
            pass
        
        self.root.after(100, self.process_queue)
    
    def log_message(self, message, tag):
        self.result_text.config(state="normal")
        # Split the symbol and the message
        symbol = message[:2]  # Extract the symbol (first 2 characters)
        text = message[2:]    # Extract the rest of the message
        # Insert the symbol with color
        self.result_text.insert(END, symbol, tag)
        # Insert the text with appropriate tag
        self.result_text.insert(END, text + "\n", tag)
        self.result_text.config(state="disabled")
        self.result_text.see(END)  # Scroll to the end
    
    def clear_logs(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, END)  # Clear all content in the logging area
        self.result_text.config(state="disabled")
        self.log_message("ℹ️ Logs cleared.", "info")  # Notify user that logs have been cleared
        self.logger.info("UI logs cleared by user")

if __name__ == "__main__":
    root = Tk()
    app = FileSizeChecker(root)
    root.mainloop()