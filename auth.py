import tkinter as tk
from tkinter import messagebox
import sqlite3

# Function to check login credentials
def check_login(success_callback):
    login_window = tk.Tk()
    login_window.title("Admin Login")
    login_window.geometry("300x200")

    label_username = tk.Label(login_window, text="Username:", font=("Helvetica", 12))
    label_username.pack(pady=5)
    entry_username = tk.Entry(login_window, font=("Helvetica", 12))
    entry_username.pack(pady=5)

    label_password = tk.Label(login_window, text="Password:", font=("Helvetica", 12))
    label_password.pack(pady=5)
    entry_password = tk.Entry(login_window, show="*", font=("Helvetica", 12))
    entry_password.pack(pady=5)

    def on_login():
        username = entry_username.get()
        password = entry_password.get()

        conn = sqlite3.connect('invoice_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", "Login successful!")
            login_window.destroy()
            success_callback()  # Proceed to main app
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    button_login = tk.Button(login_window, text="Login", command=on_login, font=("Helvetica", 12))
    button_login.pack(pady=10)

    login_window.mainloop()
