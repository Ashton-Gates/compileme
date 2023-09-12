import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
import csv
import requests
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import ttk  # Import ttk module for the Notebook widget
from chatgpt_suggestions import get_chatgpt_suggestion
from base64 import b64encode, b64decode


LANGUAGES = {
    "C": {
        "compile": ["gcc", "-o", "{output_name}.exe"],
        "run": ["./{output_name}.exe"]
    },
    "C#": {
        "compile": ["csc", "{file_name}.cs"],
        "run": ["mono", "{output_name}.exe"]
    },
    "C++": {
        "compile": ["g++", "-o", "{output_name}.exe"],
        "run": ["./{output_name}.exe"]
    },
    "C++ (clang)": {
        "compile": ["clang++", "-o", "{output_name}.exe", "{console_flag}", "-luser32", "-lgdi32", "-lcomctl32"],
        "run": ["./{output_name}.exe"]
    },
    "C++ (g++)": {
        "compile": ["g++", "-o", "{output_name}.exe", "{console_flag}"],
        "run": ["./{output_name}.exe"]
    },
    "D": {
        "compile": ["dmd", "{file_name}.d"],
        "run": ["./{output_name}.exe"]
    },
    "Fortran": {
        "compile": ["gfortran", "-o", "{output_name}.exe", "{file_name}.f90"],
        "run": ["./{output_name}.exe"]
    },
    "Go": {
        "compile": ["go", "build", "-o", "{output_name}.exe"],
        "run": ["./{output_name}.exe"]
    },
    "Haskell": {
        "compile": ["ghc", "-o", "{output_name}.exe", "{file_name}.hs"],
        "run": ["./{output_name}.exe"]
    },
    "Java": {
        "compile": ["javac", "{file_name}.java"],
        "run": ["java", "{class_name}"]
    },
    "Kotlin": {
        "compile": ["kotlinc", "{file_name}.kt", "-include-runtime", "-d", "{output_name}.jar"],
        "run": ["java", "-jar", "{output_name}.jar"]
    },
    "Objective-C": {
        "compile": ["gcc", "-o", "{output_name}.exe", "{file_name}.m", "-lobjc", "-framework", "Foundation"],
        "run": ["./{output_name}.exe"]
    },
    "Pascal": {
        "compile": ["fpc", "{file_name}.pas"],
        "run": ["./{output_name}.exe"]
    },
    "Python": {
        "Console": ["pyinstaller", "--onefile", "{file_name}.py"],
        "No Console": ["pyinstaller", "--onefile", "--noconsole", "{file_name}.py"],
        "run": ["./dist/{file_name_without_extension}.exe"]
    },
    "Rust": {
        "compile": ["rustc", "{file_name}.rs"],
        "run": ["./{output_name}.exe"]
    },
    "Scala": {
        "compile": ["scalac", "{file_name}.scala"],
        "run": ["scala", "{class_name}"]
    },
    "Swift": {
        "compile": ["swiftc", "{file_name}.swift"],
        "run": ["./{output_name}.exe"]
    },
}



KEY_FILE = 'key.key'
DATA_FILE = 'api_key.enc'

def save_key(key):
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def save_api_key(api_key):
    with open(DATA_FILE, 'w') as file:
        file.write(api_key)

def load_api_key():
    with open(DATA_FILE, 'r') as file:
        api_key = file.read()
    return api_key

def display_api_key():
    api_key = load_api_key()
    display_key = '*' * (len(api_key) - 5) + api_key[-5:]
    return display_key


CHATGPT_API_KEY = None
USE_CHATGPT = False


def general_suggestion(error_msg):
    # A dictionary of common error messages and their general suggestions
    suggestions = {
        "undeclared identifier": "Check if the variable or function is declared before its usage.",
        "expected ';'": "You might be missing a semicolon at the end of a statement.",
        "undefined reference": "There might be a missing library or source file.",
        # ... add more general suggestions as needed ...
    }
    
    # Search for a known error in the error message and return its suggestion
    for error, suggestion in suggestions.items():
        if error in error_msg:
            return suggestion
    return "Please check the error message and consult documentation or online resources."


def log_message(status, message, file_name, compile_type, console_status):
    """Log messages with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs_tree.insert("", "end", values=(status, message, file_name, compile_type, console_status))

def suggest_fix(error_msg):
    if USE_CHATGPT and CHATGPT_API_KEY:
        # Get the suggestion from ChatGPT
        suggestion = get_chatgpt_suggestion(error_msg, CHATGPT_API_KEY)
    else:
        # Use general error suggestions
        suggestion = general_suggestion(error_msg)
    
    return suggestion

def get_chatgpt_suggestion(error_msg):
    # API endpoint
    url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }

    # Data payload
    data = {
        "prompt": f"Suggest a fix for the following C++ compilation error: {error_msg}",
        "max_tokens": 150
    }
    
    # Make the API request
    response = requests.post(url, headers=headers, json=data)
    
    # Extract the suggestion from the response
    suggestion = response.json().get('choices', [{}])[0].get('text', '').strip()
    
    # In the API Settings tab:
def on_api_key_submit():
    global CHATGPT_API_KEY, USE_CHATGPT
    CHATGPT_API_KEY = api_key_input.get()
    USE_CHATGPT = use_chatgpt_var.get()
    
def on_toggle_chatgpt():
    global USE_CHATGPT
    USE_CHATGPT = not USE_CHATGPT
    

def compile_files():
    # Initialize compiler_var at the beginning of the function
    compiler_var = tk.StringVar()

    # Get the selected file paths
    file_paths = files_list.get(1.0, tk.END).strip().split('\n')
    
    # Check if the selected language is in the LANGUAGES dictionary
    selected_language = language_var.get()
    if selected_language in LANGUAGES:
        # Use the commands from the LANGUAGES dictionary
        commands = LANGUAGES[selected_language]
        cmd = commands.get("compile", []) + file_paths
    else:
        # Fallback to the original C++ compilation logic
        compiler = compiler_var.get()
        cmd = [compiler, "-o", output_name_var.get() or "output"]
        if no_console_var.get():
            cmd.append("-mwindows")

# Run the compiler command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Get the selected file paths
    file_paths = files_list.get(1.0, tk.END).strip().split('\n')
    
    commands = LANGUAGES[selected_language]
    
    # Check if the language requires compilation or just running
    if "compile" in commands:
        cmd = commands["compile"] + file_paths
        cmd = [item.format(output_name=output_name_var.get(), console_flag="-mwindows" if no_console_var.get() else "") for item in cmd]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr
            fix_suggestion = suggest_fix(error_msg)
            output_display.insert(tk.END, f"Compilation failed!\n{error_msg}\nSuggestion: {fix_suggestion}")
            return
        else:
            output_display.insert(tk.END, "Compilation succeeded!\n")
    
    # Run the code if a run command is specified
    if "run" in commands:
        cmd = commands["run"] + file_paths
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr
            fix_suggestion = suggest_fix(error_msg)
            output_display.insert(tk.END, f"Execution failed!\n{error_msg}\nSuggestion: {fix_suggestion}")
        else:
            output_display.insert(tk.END, f"Execution succeeded!\n{result.stdout}")

    # If the language is not in the LANGUAGES dictionary, fall back to the original C++ compilation logic
    # Get the selected compiler
    compiler = compiler_var.get()
    # Get the output name
    output_name = output_name_var.get() or "output"
    # Determine if console should be shown
    console_flag = "-mwindows" if no_console_var.get() else ""

    # Run the compiler command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Clear the previous content of the Text widget
    output_display.config(state=tk.NORMAL)  # Enable editing
    output_display.delete(1.0, tk.END)
    
    if result.returncode != 0:
        error_msg = result.stderr
        fix_suggestion = suggest_fix(error_msg)
        output_display.insert(tk.END, f"Compilation failed!\n{error_msg}\nSuggestion: {fix_suggestion}")
    else:
        message = "Compilation succeeded!"
    
    # Insert the message into the Text widget
    output_display.insert(tk.END, message)

    # Adjust the height of the Text widget based on the number of lines in the message
    num_lines = message.count('\n') + 1
    output_display.config(height=min(max(num_lines, 5), 20))  # Set a minimum of 5 lines and a maximum of 20 lines

    # Adjust the window size
    root.update_idletasks()  # Update all pending tasks to get accurate widget dimensions
    root.geometry('')  # Reset the window size to fit its content

    output_display.config(state=tk.DISABLED)  # Disable editing
    
    # Get the file name
    file_name = os.path.basename(file_paths[0]) if file_paths else "Multiple Files"
    
    # Get the compile type
    compile_type = compiler_var.get()
    
    # Get the console status
    console_status = "No Console" if no_console_var.get() else "Console"

    # Get the appropriate compile command for Python based on console status
    compile_command = LANGUAGES["Python"][console_status]

    if result.returncode != 0:
        error_msg = result.stderr
        fix_suggestion = suggest_fix(error_msg)
        output_display.insert(tk.END, f"Compilation failed!\n{error_msg}\nSuggestion: {fix_suggestion}")
        log_message("Error", error_msg, file_name, compile_type, console_status)
    else:
        message = "Compilation succeeded!"
        log_message("Success", message, file_name, compile_type, console_status)
def browse_files():
    file_paths = filedialog.askopenfilenames()
    for path in file_paths:
        _, ext = os.path.splitext(path)
        # Only insert the file path without the file extension description
        files_list.insert(tk.END, f"{path}\n")

def copy_to_clipboard():
    # Get the selected text from the Text widget
    selected_text = output_display.get(tk.SEL_FIRST, tk.SEL_LAST)
    root.clipboard_clear()
    root.clipboard_append(selected_text)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

def export_to_csv():
    """Export logs to a CSV file."""
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if not filename:
        return

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Status", "Message"])
        for item in logs_tree.get_children():
            writer.writerow(logs_tree.item(item)["values"])
            
# Create the main window
root = tk.Tk()
root.title("CompileME")

# Create the Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

# Create the Home tab
home_frame = ttk.Frame(notebook)
notebook.add(home_frame, text="Home")
    
# Add a logo to the Home tab
logo_path = "C:\\Portfolio\\HOPR\\logo.png"  # Replace with the path to your logo
image = Image.open(logo_path)
logo = ImageTk.PhotoImage(image)
logo_label = tk.Label(home_frame, image=logo)
logo_label.pack(pady=20)

title_heading = "CompileME"
title_label = tk.Label(home_frame, text=title_heading, justify=tk.CENTER, font=("default", 22, "bold"))
title_label.pack(pady=20, anchor='center')

about_me = """ 
Version: 1.0
Author: Ashton Kinnell
"""
about_me_label = tk.Label(home_frame, text=about_me, justify=tk.CENTER, font=("default", 12))
about_me_label.pack(pady=20, anchor='center')

about_text = """
Instructions for CompileME:

1. Home Tab:
    - Logo: This displays the logo of the application.
    - About: Provides information about the application version, the author, and these instructions.

2. Compile Tab:
    - Select Files:
        - Click on the "Browse" button to open a file dialog.
        - Select one or more source files that you wish to compile.
        - The selected files will be listed in the box above the "Browse" button.
    - Output Name:
        - Enter the desired name for the output executable file. If left blank, the default name will be "output".
    - Hide Console:
        - Check this option if you do not want a console window to appear when running the compiled application. This is useful for GUI applications.
    - Compile:
        - Click on the "Compile" button to start the compilation process.
        - If the compilation is successful, a message will be displayed confirming the success.
        - If there are any errors or warnings during the compilation, they will be displayed in the box below. Suggestions for resolving common errors will also be provided.
        - You can right-click on the error messages to copy them to the clipboard.
"""
# Set the font for the about_label
font_size = 12  # You can adjust this value as needed
about_label = tk.Label(home_frame, text=about_text, justify=tk.LEFT, font=("default", font_size))
about_label.pack(pady=20, anchor='w')

# Create the Compile tab
compile_frame = ttk.Frame(notebook)
notebook.add(compile_frame, text="Compile")

# Language selection for Compile tab
language_var = tk.StringVar()
default_language = list(LANGUAGES.keys())[0]  # Get the first language from the LANGUAGES dictionary
language_var.set(default_language)  # Set the default value
tk.Label(compile_frame, text="Choose Language:").pack(pady=10)


#Combobox for language selection
language_combobox = ttk.Combobox(compile_frame, textvariable=language_var, values=list(LANGUAGES.keys()))
language_combobox.pack(pady=10)

# File input
tk.Label(compile_frame, text="Select Files:").pack(pady=10)
files_list = tk.Text(compile_frame, height=10, width=50)
files_list.pack(pady=10)
tk.Button(compile_frame, text="Browse", command=browse_files).pack(pady=10)


# Output name input for Compile tab
output_name_var = tk.StringVar()
tk.Label(compile_frame, text="Output Name:").pack(pady=10)
tk.Entry(compile_frame, textvariable=output_name_var, width=40).pack(pady=10)

# No console checkbox for Compile tab
no_console_var = tk.BooleanVar()
tk.Checkbutton(compile_frame, text="Hide Console", variable=no_console_var).pack(pady=10)

# Compile button for Compile tab
tk.Button(compile_frame, text="Compile", command=compile_files).pack(pady=20)

# Output display for Compile tab
output_display = tk.Text(compile_frame, height=5, width=50, wrap=tk.WORD, state=tk.DISABLED)
output_display.pack(pady=10)

# Context menu for the Text widget in Compile tab
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=copy_to_clipboard)
output_display.bind("<Button-3>", show_context_menu)

# Create the Logs tab
logs_frame = ttk.Frame(notebook)
notebook.add(logs_frame, text="Logs")

# Treeview for logs
logs_tree = ttk.Treeview(logs_frame, columns=("Timestamp", "Status", "Message", "File Name", "Compile Type", "Console Status"), show="headings")
logs_tree.heading("Timestamp", text="Timestamp")
logs_tree.heading("Status", text="Status")
logs_tree.heading("Message", text="Message")
logs_tree.heading("File Name", text="File Name")
logs_tree.heading("Compile Type", text="Compile Type")
logs_tree.heading("Console Status", text="Console Status")
logs_tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Scrollbar for the Treeview
scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=logs_tree.yview)
scrollbar.pack(side="right", fill="y")
logs_tree.configure(yscrollcommand=scrollbar.set)

# Export to CSV button
export_button = ttk.Button(logs_frame, text="Export to CSV", command=export_to_csv)
export_button.pack(pady=20)

# Create the API Settings tab
api_frame = ttk.Frame(notebook)
notebook.add(api_frame, text="API Settings")

# Label and Entry for API Key
tk.Label(api_frame, text="Enter ChatGPT API Key:").pack(pady=10)
api_key_input = tk.Entry(api_frame, width=40)
api_key_input.pack(pady=10)

# Checkbox for enabling/disabling ChatGPT
use_chatgpt_var = tk.BooleanVar()
tk.Checkbutton(api_frame, text="Use ChatGPT for Error Suggestions", variable=use_chatgpt_var, command=on_toggle_chatgpt).pack(pady=10)

# Save button for API Settings
tk.Button(api_frame, text="Save Settings", command=on_api_key_submit).pack(pady=20)

root.mainloop()
