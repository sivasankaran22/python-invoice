import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import messagebox
import sqlite3

# Function to manage products
def manage_products(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    product_frame = tk.Frame(frame)
    product_frame.pack(fill="both", expand=True)

    def add_product():
        name = askstring("Input", "Enter Product Name:")
        cost = askstring("Input", "Enter Product Cost:")
        quantity = askstring("Input", "Enter Product Quantity:")

        if name and cost.isdigit() and quantity.isdigit():
            conn = sqlite3.connect('invoice_app.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, cost, quantity) VALUES (?, ?, ?)", (name, float(cost), int(quantity)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product added successfully!")

    add_product_button = tk.Button(product_frame, text="Add Product", command=add_product, font=("Helvetica", 14))
    add_product_button.pack(pady=10)
