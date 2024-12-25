import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

# Function to create the database table for products
def create_products_table():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_description TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_quantity TEXT NOT NULL,
            product_price TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to add a new product with validation
def add_products_popup(parent_frame):
    
    def save_products():
        product_name = entry_product_name.get()
        product_description = entry_product_description.get("1.0", "end").strip()
        product_sku = entry_product_sku.get()
        product_quantity = entry_product_quantity.get()
        product_price = entry_product_price.get()

        if not all([product_name, product_sku, product_quantity, product_price]):
            messagebox.showwarning("Input Error", "Please fill in all required fields.")
            return

        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (
                product_name, product_description, product_sku, product_quantity,
                product_price
            ) VALUES (?, ?, ?, ?, ?)
        ''', (product_name, product_description, product_sku, product_quantity, product_price))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product added successfully!")
        popup.destroy()
        load_products(parent_frame)  # Refresh the product list

    popup = tk.Toplevel()
    popup.title("Add Product")
    popup.geometry("600x600")

    tk.Label(popup, text="Product Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_name.pack(pady=5)

    tk.Label(popup, text="Product Description:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_description = tk.Text(popup, font=("Helvetica", 12), height=5, width=40)
    entry_product_description.pack(pady=5)

    tk.Label(popup, text="Product SKU:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_sku = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_sku.pack(pady=5)

    tk.Label(popup, text="Product Quantity:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_quantity = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_quantity.pack(pady=5)

    tk.Label(popup, text="Product Price:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_price = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_price.pack(pady=5)

    tk.Button(popup, text="Save", command=save_products, font=("Helvetica", 12)).pack(pady=10)

# Function to load and display products with pagination and search
def load_products(list_frame, page=1, items_per_page=10, search_term=""):
    # Clear previous widgets in the list frame
    for widget in list_frame.winfo_children():
        widget.destroy()

    # Create a canvas and scrollbars
    canvas = tk.Canvas(list_frame)
    scroll_y = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scroll_x = tk.Scrollbar(list_frame, orient="horizontal", command=canvas.xview)

    scrollable_frame = tk.Frame(canvas)

    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")

    # Fetch product data with an optional search term
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    if search_term:
        query = """
        SELECT COUNT(*) FROM products 
        WHERE product_name LIKE ? OR product_description LIKE ? OR product_sku LIKE ? 
        OR product_quantity LIKE ? OR product_price LIKE ?
        """
        cursor.execute(query, 
                       ('%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%'))
    else:
        cursor.execute("SELECT COUNT(*) FROM products")
    
    total_products = cursor.fetchone()[0]
    total_pages = (total_products + items_per_page - 1) // items_per_page

    offset = (page - 1) * items_per_page
    if search_term:
        query = """
        SELECT * FROM products 
        WHERE product_name LIKE ? OR product_description LIKE ? OR product_sku LIKE ? 
        OR product_quantity LIKE ? OR product_price LIKE ?
        LIMIT ? OFFSET ?
        """
        cursor.execute(query, 
                       ('%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', items_per_page, offset))
    else:
        cursor.execute("SELECT * FROM products LIMIT ? OFFSET ?", (items_per_page, offset))

    products = cursor.fetchall()
    conn.close()

    # If no products are found, display a message
    if not products:
        tk.Label(scrollable_frame, text="No products found.", font=("Helvetica", 14)).pack(pady=10)
        return

    # Display headers
    headers = ["Sr. No.", "Product Name", "Product Description", "Product SKU", "Product Quantity", "Product Price", "Actions"]
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

    # Display product data
    for row, product in enumerate(products, start=1):
        tk.Label(scrollable_frame, text=(offset + row), font=("Helvetica", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        for col, value in enumerate(product[1:], start=1):
            tk.Label(scrollable_frame, text=value, font=("Helvetica", 12)).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        # Action buttons
        button_frame = tk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=6, padx=5, pady=5)
        tk.Button(button_frame, text="Edit", font=("Helvetica", 10), command=lambda p=product: edit_products_popup(list_frame, p)).pack(side="left", padx=2)
        tk.Button(button_frame, text="Delete", font=("Helvetica", 10), command=lambda p=product: delete_products(list_frame, p[0])).pack(side="left", padx=2)

    # Update canvas scroll region
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Pagination controls at the bottom center (directly below the table)
    pagination_frame = tk.Frame(scrollable_frame)
    pagination_frame.grid(row=len(products) + 1, column=0, columnspan=len(headers), pady=10)

    if page > 1:
        tk.Button(pagination_frame, text="Previous", font=("Helvetica", 10),
                  command=lambda: load_products(list_frame, page - 1, items_per_page, search_term)).pack(side="left", padx=10)

    tk.Label(pagination_frame, text=f"Page {page} of {total_pages}", font=("Helvetica", 12)).pack(side="left", padx=10)

    if page < total_pages:
        tk.Button(pagination_frame, text="Next", font=("Helvetica", 10),
                  command=lambda: load_products(list_frame, page + 1, items_per_page, search_term)).pack(side="left", padx=10)

# Function to edit an existing product
def edit_products_popup(parent_frame, product):
    def save_changes():
        product_name = entry_product_name.get()
        product_description = entry_product_description.get("1.0", "end").strip()
        product_sku = entry_product_sku.get()
        product_quantity = entry_product_quantity.get()
        product_price = entry_product_price.get()

        if not all([product_name, product_sku, product_quantity, product_price]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET product_name = ?, product_description = ?, product_sku = ?, product_quantity = ?, 
                product_price = ?
            WHERE id = ?
        ''', (product_name, product_description, product_sku, product_quantity, product_price, product[0]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product updated successfully!")
        popup.destroy()
        load_products(parent_frame)  # Refresh the product list

    popup = tk.Toplevel()
    popup.title("Edit Product")
    popup.geometry("600x600")

    tk.Label(popup, text="Product Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_name.insert(0, product[1])
    entry_product_name.pack(pady=5)

    tk.Label(popup, text="Product Description:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_description = tk.Text(popup, font=("Helvetica", 12), height=5, width=40)
    entry_product_description.insert("1.0", product[2])
    entry_product_description.pack(pady=5)

    tk.Label(popup, text="Product SKU:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_sku = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_sku.insert(0, product[3])
    entry_product_sku.pack(pady=5)

    tk.Label(popup, text="Product Quantity:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_quantity = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_quantity.insert(0, product[4])
    entry_product_quantity.pack(pady=5)

    tk.Label(popup, text="Product Price:", font=("Helvetica", 12)).pack(pady=5)
    entry_product_price = tk.Entry(popup, font=("Helvetica", 12))
    entry_product_price.insert(0, product[5])
    entry_product_price.pack(pady=5)

    tk.Button(popup, text="Save", command=save_changes, font=("Helvetica", 12)).pack(pady=10)

# Function to delete a product
def delete_products(parent_frame, product_id):
    result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
    if result:
        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product deleted successfully!")
        load_products(parent_frame)  # Refresh the product list

# Main function to manage products
def manage_products(parent_frame):
    create_products_table()

    # Header Frame
    header_frame = tk.Frame(parent_frame)
    header_frame.pack(fill="x", pady=10)

    # "Add New Product" Button
    button_add = tk.Button(header_frame, text="Add New Product", command=lambda: add_products_popup(parent_frame), font=("Helvetica", 14))
    button_add.pack(side="left", padx=10)

    # Search Bar (Label + Entry + Button) next to the "Add New Product" Button
    search_label = tk.Label(header_frame, text="Search:", font=("Helvetica", 12))
    search_label.pack(side="left", padx=10)

    search_entry = tk.Entry(header_frame, font=("Helvetica", 12))
    search_entry.pack(side="left", padx=10)

    def search_products():
        search_term = search_entry.get()
        load_products(list_frame, page=1, search_term=search_term)

    search_button = tk.Button(header_frame, text="Search", font=("Helvetica", 12), command=search_products)
    search_button.pack(side="left", padx=10)

    # List Frame for the table
    list_frame = tk.Frame(parent_frame)
    list_frame.pack(fill="both", expand=True)

    load_products(list_frame, page=1)  # Default to page 1
