import random
import string
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import pyperclip
import sqlite3

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")

        self.style = ttk.Style()
        self.style.configure('TButton', font=('calibri', 15, 'bold'), foreground='blue')
        self.style.configure('TLabel', font=('calibri', 12, 'normal'))

        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.length_label = ttk.Label(self.main_frame, text="Password length:")
        self.length_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        self.length_entry = ttk.Entry(self.main_frame)
        self.length_entry.grid(row=0, column=1, pady=(10, 0))
        self.length_entry.bind("<Return>", self.generate_password_on_enter)

        self.title_label = ttk.Label(self.main_frame, text="Title:")
        self.title_label.grid(row=1, column=0, pady=(10, 0), sticky="w")

        self.title_entry = ttk.Entry(self.main_frame)
        self.title_entry.grid(row=1, column=1, pady=(10, 0))

        self.generate_button = ttk.Button(self.main_frame, text="Generate", command=self.generate_password)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.copy_button = ttk.Button(self.main_frame, text="Copy Password", command=self.copy_to_clipboard, state="disabled")
        self.copy_button.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        self.result_text = tk.Text(self.main_frame, wrap=tk.WORD, height=5, width=40)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=10)
        self.result_text.config(state=tk.DISABLED)

        self.scrollbar = ttk.Scrollbar(self.main_frame, command=self.result_text.yview)
        self.scrollbar.grid(row=4, column=2, pady=10, sticky='ns')
        self.result_text['yscrollcommand'] = self.scrollbar.set

        self.save_button = ttk.Button(self.main_frame, text="Save Password", command=self.save_password)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        self.password_tree = ttk.Treeview(self.main_frame, columns=("Title", "Password"), show="headings", height=5)
        self.password_tree.heading("Title", text="Title")
        self.password_tree.heading("Password", text="Password")
        self.password_tree.grid(row=6, column=0, columnspan=2, pady=10)
        self.password_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.generated_password = None
        self.generated_title = ""
        self.selected_id = None

        # Bind Ctrl+C to copy_to_clipboard
        self.root.bind("<Control-c>", self.copy_to_clipboard)

        # Initialize the database
        self.connection = sqlite3.connect("passwords.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, title TEXT, password TEXT)")
        self.connection.commit()

        # Load saved passwords
        self.load_saved_passwords()

    def generate_password(self):
        password_length = int(self.length_entry.get())
        if password_length <= 0:
            self.set_result_text("Enter the correct password length")
            return

        if password_length > 5000:
            self.set_result_text("Password length exceeds limit of 5000 characters")
            return

        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(password_length))
        self.generated_title = self.title_entry.get()
        self.set_result_text("Generated password:\n" + password)
        self.generated_password = password
        self.copy_button.config(state="normal")

    def generate_password_on_enter(self, event):
        self.generate_password()

    def copy_to_clipboard(self, event=None):
        if self.generated_password:
            pyperclip.copy(self.generated_password)
            tkinter.messagebox.showinfo("Success", "Password copied to clipboard")
        else:
            tkinter.messagebox.showwarning("Error", "Generate password first")

    def set_result_text(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def save_password(self):
        if self.generated_password and self.generated_title:
            self.cursor.execute("INSERT INTO passwords (title, password) VALUES (?, ?)",
                                (self.generated_title, self.generated_password))
            self.connection.commit()
            tkinter.messagebox.showinfo("Success", "Password saved to database")
            self.load_saved_passwords()
        else:
            tkinter.messagebox.showwarning("Error", "Generate password first")

    def load_saved_passwords(self):
        self.password_tree.delete(*self.password_tree.get_children())
        self.cursor.execute("SELECT id, title, password FROM passwords")
        rows = self.cursor.fetchall()
        for row in rows:
            self.password_tree.insert("", "end", values=(row[1], row[2]))
    
    def on_tree_select(self, event):
        selected_item = self.password_tree.selection()[0]
        self.selected_id = self.password_tree.item(selected_item, "text")
        self.cursor.execute("SELECT password FROM passwords WHERE id=?", (self.selected_id,))
        password = self.cursor.fetchone()[0]
        self.set_result_text("Selected password:\n" + password)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()