import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import uuid

# Function to create the database table for invoices
def create_invoices_table():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,  -- Use UUID as invoice ID
            customer_id INTEGER,
            customer_name TEXT,
            customer_address TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            shipping_address TEXT,
            invoice_date TEXT,
            total_amount REAL,
            payment_status TEXT,
            payment_received_type TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    conn.commit()
    conn.close()


# Function to create the invoice_items table
def create_invoice_items_table():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            product_name TEXT,
            product_quantity INTEGER,
            product_unit_price REAL,
            product_total REAL,
            product_sku TEXT,
            product_id INTEGER,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid

# Function to create the invoice entry popup
def create_invoice_popup(parent_frame):
    def save_invoice():
        customer_id = customer_var.get()
        if customer_id == "0":
            customer_name = entry_customer_name.get()
            customer_address = entry_customer_address.get()
            customer_phone = entry_customer_phone.get()
            customer_email = entry_customer_email.get()
            shipping_address = entry_shipping_address.get()
        else:
            conn = sqlite3.connect('invoice.db')
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, company_address, company_phone, company_email FROM customers WHERE id=?", (customer_id,))
            customer_data = cursor.fetchone()
            conn.close()

            if customer_data:
                customer_name, customer_address, customer_phone, customer_email = customer_data
                shipping_address = entry_shipping_address.get()
            else:
                messagebox.showerror("Error", "Customer not found.")
                return

        invoice_date = entry_invoice_date.get()
        total_amount = sum(item['total'] for item in products_selected)

        if not products_selected:
            messagebox.showwarning("Input Error", "Please select at least one product.")
            return

        invoice_id = str(uuid.uuid4())
        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO invoices (id, customer_id, customer_name, customer_address, customer_phone, customer_email,
                                  shipping_address, invoice_date, total_amount, payment_status, payment_received_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        ''', (invoice_id, customer_id if customer_id != "0" else None, customer_name, customer_address, customer_phone,
              customer_email, shipping_address, invoice_date, total_amount, "Pending", "Cash"))
        conn.commit()

        for product in products_selected:
            cursor.execute(''' 
                INSERT INTO invoice_items (invoice_id, product_name, product_quantity, product_unit_price, product_total,
                                          product_sku, product_id)
                VALUES (?, ?, ?, ?, ?, ?, ?) 
            ''', (invoice_id, product['name'], product['quantity'], product['unit_price'], product['total'], product['sku'], product['id']))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Invoice created successfully!")
        popup.destroy()
        load_invoices(parent_frame)

    def on_customer_select(event):
        selected_company_name = customer_dropdown.get()
        if selected_company_name == "Enter Manually":
            customer_var.set("0")
            # Clear all fields for manual input
            entry_customer_name.delete(0, tk.END)
            entry_customer_address.delete(0, tk.END)
            entry_customer_phone.delete(0, tk.END)
            entry_customer_email.delete(0, tk.END)
            return

        customer_id = customer_map.get(selected_company_name, "0")
        customer_var.set(customer_id)

        if customer_id != "0":
            # Fetch and populate customer details
            conn = sqlite3.connect('invoice.db')
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, company_address, company_phone, company_email FROM customers WHERE id=?", (customer_id,))
            customer_data = cursor.fetchone()
            conn.close()

            if customer_data:
                # Auto-fill the customer details
                entry_customer_name.delete(0, tk.END)
                entry_customer_name.insert(0, customer_data[0])
                entry_customer_address.delete(0, tk.END)
                entry_customer_address.insert(0, customer_data[1])
                entry_customer_phone.delete(0, tk.END)
                entry_customer_phone.insert(0, customer_data[2])
                entry_customer_email.delete(0, tk.END)
                entry_customer_email.insert(0, customer_data[3])
            else:
                messagebox.showerror("Error", "Customer details not found.")

    def add_product_popup():
        def search_product(event=None):
            search_term = search_var.get().lower()
            product_listbox.delete(0, tk.END)
            for product in product_data:
                if search_term in product[1].lower() or search_term in product[3].lower():
                    product_listbox.insert(tk.END, f"{product[1]} (SKU: {product[3]})")

        def calculate_total():
            try:
                quantity = int(quantity_var.get())
                unit_price = float(unit_price_var.get())
                total = quantity * unit_price
                total_label.config(text=f"Total: {total:.2f}")
            except ValueError:
                total_label.config(text="Total: 0.00")

        def add_selected_product():
            selected_index = product_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Selection Error", "Please select a product to add.")
                return

            index = selected_index[0]
            product = product_data[index]

            quantity = quantity_var.get()
            if not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showwarning("Input Error", "Please enter a valid quantity.")
                return

            quantity = int(quantity)
            unit_price = float(unit_price_var.get())
            total = quantity * unit_price

            # Append the product with unit price, quantity, and total to the selected products
            products_selected.append({
                'id': product[0],
                'name': product[1],
                'unit_price': unit_price,
                'quantity': quantity,
                'total': total,
                'sku': product[3]
            })

            update_product_table()
            product_popup.destroy()

        product_popup = tk.Toplevel()
        product_popup.title("Add Product")
        product_popup.geometry("500x500")  # Increased height to fit the Add button

        tk.Label(product_popup, text="Search Product:", font=("Helvetica", 12)).pack(pady=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(product_popup, textvariable=search_var, font=("Helvetica", 12))
        search_entry.pack(pady=5)
        search_entry.bind("<KeyRelease>", search_product)  # Bind the key release event to search function

        product_listbox = tk.Listbox(product_popup, font=("Helvetica", 12), height=10)
        product_listbox.pack(pady=5, fill="both", expand=True)

        # Fill product listbox initially with all products
        for product in product_data:
            product_listbox.insert(tk.END, f"{product[1]} (SKU: {product[3]})")

        tk.Label(product_popup, text="Quantity:", font=("Helvetica", 12)).pack(pady=5)
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(product_popup, textvariable=quantity_var, font=("Helvetica", 12))
        quantity_entry.pack(pady=5)

        tk.Label(product_popup, text="Unit Price:", font=("Helvetica", 12)).pack(pady=5)
        unit_price_var = tk.StringVar()
        unit_price_entry = tk.Entry(product_popup, textvariable=unit_price_var, font=("Helvetica", 12))
        unit_price_entry.pack(pady=5)

        total_label = tk.Label(product_popup, text="Total: 0.00", font=("Helvetica", 12))
        total_label.pack(pady=5)

        # Update total when quantity or unit price changes
        quantity_entry.bind("<KeyRelease>", lambda event: calculate_total())
        unit_price_entry.bind("<KeyRelease>", lambda event: calculate_total())

        tk.Button(product_popup, text="Add", command=add_selected_product, font=("Helvetica", 12)).pack(pady=10)

    def update_product_table():
        for widget in product_table_frame.winfo_children():
            widget.destroy()

        for index, product in enumerate(products_selected):
            tk.Label(product_table_frame, text=product['name'], font=("Helvetica", 12)).grid(row=index, column=0, padx=5, pady=5)
            tk.Label(product_table_frame, text=product['quantity'], font=("Helvetica", 12)).grid(row=index, column=1, padx=5, pady=5)
            tk.Label(product_table_frame, text=product['total'], font=("Helvetica", 12)).grid(row=index, column=2, padx=5, pady=5)

            # Remove the edit option; only keep the delete option
            tk.Button(product_table_frame, text="Delete", font=("Helvetica", 12), command=lambda i=index: delete_product(i)).grid(row=index, column=3, padx=5, pady=5)

    def delete_product(index):
        products_selected.pop(index)
        update_product_table()



    popup = tk.Toplevel()
    popup.title("Create Invoice")
    popup.geometry("800x600")

    tk.Label(popup, text="Invoice Date:", font=("Helvetica", 12)).pack(pady=5)
    entry_invoice_date = tk.Entry(popup, font=("Helvetica", 12))
    entry_invoice_date.pack(pady=5)

    customer_var = tk.StringVar(value="0")
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name FROM customers")
    customers = cursor.fetchall()
    conn.close()

    customer_dropdown = ttk.Combobox(popup, textvariable=customer_var, values=["Enter Manually"] + [c[1] for c in customers], state="readonly", font=("Helvetica", 12))
    customer_dropdown.set("Select Customer")
    customer_dropdown.pack(pady=5)

    customer_map = {customer[1]: customer[0] for customer in customers}

    customer_dropdown.bind("<<ComboboxSelected>>", on_customer_select)

    entry_customer_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_customer_name.pack(pady=5)
    entry_customer_name.insert(0, "Customer Name")

    entry_customer_address = tk.Entry(popup, font=("Helvetica", 12))
    entry_customer_address.pack(pady=5)
    entry_customer_address.insert(0, "Customer Address")

    entry_customer_phone = tk.Entry(popup, font=("Helvetica", 12))
    entry_customer_phone.pack(pady=5)
    entry_customer_phone.insert(0, "Customer Phone")

    entry_customer_email = tk.Entry(popup, font=("Helvetica", 12))
    entry_customer_email.pack(pady=5)
    entry_customer_email.insert(0, "Customer Email")

    entry_shipping_address = tk.Entry(popup, font=("Helvetica", 12))
    entry_shipping_address.pack(pady=5)
    entry_shipping_address.insert(0, "Shipping Address")

    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, product_price, product_sku FROM products")
    product_data = cursor.fetchall()
    conn.close()

    tk.Button(popup, text="Add Product", command=add_product_popup, font=("Helvetica", 12)).pack(pady=10)

    product_table_frame = tk.Frame(popup)
    product_table_frame.pack(fill="both", expand=True)

    products_selected = []

    tk.Button(popup, text="Save Invoice", command=save_invoice, font=("Helvetica", 12)).pack(pady=10)



# Function to load and display the list of invoices
def load_invoices(list_frame):
    for widget in list_frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(list_frame)
    scroll_y = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scroll_x = tk.Scrollbar(list_frame, orient="horizontal", command=canvas.xview)

    scrollable_frame = tk.Frame(canvas)

    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")

    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT invoices.* 
        FROM invoices
    ''')
    invoices = cursor.fetchall()
    conn.close()

    if not invoices:
        tk.Label(scrollable_frame, text="No invoices found.", font=("Helvetica", 14)).pack(pady=10)
    else:
        headers = ["Invoice ID", "Customer", "Invoice Date", "Total Amount", "Actions"]
        for col, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        for row, invoice in enumerate(invoices, start=1):
            tk.Label(scrollable_frame, text=invoice[0], font=("Helvetica", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            tk.Label(scrollable_frame, text=invoice[1], font=("Helvetica", 12)).grid(row=row, column=1, padx=5, pady=5, sticky="w")
            tk.Label(scrollable_frame, text=invoice[2], font=("Helvetica", 12)).grid(row=row, column=2, padx=5, pady=5, sticky="w")
            tk.Label(scrollable_frame, text=invoice[3], font=("Helvetica", 12)).grid(row=row, column=3, padx=5, pady=5, sticky="w")

            button_frame = tk.Frame(scrollable_frame)
            button_frame.grid(row=row, column=4, padx=5, pady=5)
            tk.Button(button_frame, text="View", font=("Helvetica", 10), command=lambda i=invoice[0]: view_invoice_details(i)).pack(side="left", padx=2)

    # Add Create Invoice Button directly in this function (Ensure button is always visible)
    tk.Button(list_frame, text="Create New Invoice", command=lambda: create_invoice_popup(list_frame), font=("Helvetica", 14)).pack(pady=10)

# Function to view an invoice's details (optional)
def view_invoice_details(invoice_id):
    print(f"Viewing details of Invoice ID: {invoice_id}")
    # Logic for viewing detailed invoice (for example, display invoice items, etc.)

def manage_invoices(parent_frame):
    # Create required tables
    create_invoices_table()
    create_invoice_items_table()
    
    # Header Frame (Optional, could be used for navigation or title)
    header_frame = tk.Frame(parent_frame)
    header_frame.pack(fill="x", pady=10)

    # List Frame for displaying the invoices list
    list_frame = tk.Frame(parent_frame)
    list_frame.pack(fill="both", expand=True)

    # Load and display the list of invoices (including the "Create New Invoice" button)
    load_invoices(list_frame)
