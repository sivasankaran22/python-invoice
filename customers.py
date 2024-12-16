import tkinter as tk
from tkinter import messagebox
import sqlite3

# Function to create the database table for customers
def create_customer_table():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            company_address TEXT NOT NULL,
            company_email TEXT NOT NULL,
            company_phone TEXT NOT NULL,
            contact_person_name TEXT NOT NULL,
            contact_person_phone TEXT NOT NULL,
            contact_person_email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to add a new customer
def add_customer_popup(parent_frame):
    def save_customer():
        company_name = entry_company_name.get()
        company_address = entry_company_address.get()
        company_email = entry_company_email.get()
        company_phone = entry_company_phone.get()
        contact_person_name = entry_contact_person_name.get()
        contact_person_phone = entry_contact_person_phone.get()
        contact_person_email = entry_contact_person_email.get()

        if all([company_name, company_address, company_email, company_phone, 
                contact_person_name, contact_person_phone, contact_person_email]):
            conn = sqlite3.connect('invoice.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (
                    company_name, company_address, company_email, company_phone,
                    contact_person_name, contact_person_phone, contact_person_email
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_name, company_address, company_email, company_phone,
                  contact_person_name, contact_person_phone, contact_person_email))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Customer added successfully!")
            load_customers()  # Refresh the customer list
            popup.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    popup = tk.Toplevel()
    popup.title("Add Customer")
    popup.geometry("600x600")

    tk.Label(popup, text="Company Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_name.pack(pady=5)

    tk.Label(popup, text="Company Address:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_address = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_address.pack(pady=5)

    tk.Label(popup, text="Company Email:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_email = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_email.pack(pady=5)

    tk.Label(popup, text="Company Phone:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_phone = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_phone.pack(pady=5)

    tk.Label(popup, text="Contact Person Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_name.pack(pady=5)

    tk.Label(popup, text="Contact Person Phone:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_phone = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_phone.pack(pady=5)

    tk.Label(popup, text="Contact Person Email:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_email = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_email.pack(pady=5)

    tk.Button(popup, text="Save", command=save_customer, font=("Helvetica", 12)).pack(pady=10)

# Function to load customers into the table
def load_customers():
    # Clear previous widgets in the list frame
    for widget in list_frame.winfo_children():
        widget.destroy()

    # Connect to the database and fetch customer data
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()

    # If no customers are found, display a message
    if not customers:
        tk.Label(list_frame, text="No customers found.", font=("Helvetica", 14)).pack(pady=10)
        return

    # Define headers for the customer list
    headers = ["ID", "Company Name", "Company Email", "Company Phone", "Contact Name", "Contact Phone", "Contact Email", "Actions"]
    
    # Display headers at the top of the list
    for col, header in enumerate(headers):
        tk.Label(list_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")

    # Display each customer's details in the list
    for row, customer in enumerate(customers, start=1):
        for col, value in enumerate(customer[:7]):  # Only display the first 7 fields
            tk.Label(list_frame, text=value, font=("Helvetica", 12)).grid(row=row, column=col, padx=10, pady=5, sticky="w")

        # Add Edit and Delete buttons
        tk.Button(list_frame, text="Edit", font=("Helvetica", 10), command=lambda c=customer: edit_customer_popup(c)).grid(row=row, column=7, padx=5)
        tk.Button(list_frame, text="Delete", font=("Helvetica", 10), command=lambda c=customer: delete_customer(c[0])).grid(row=row, column=8, padx=5)

# Function to edit an existing customer
def edit_customer_popup(customer):
    def save_changes():
        company_name = entry_company_name.get()
        company_address = entry_company_address.get()
        company_email = entry_company_email.get()
        company_phone = entry_company_phone.get()
        contact_person_name = entry_contact_person_name.get()
        contact_person_phone = entry_contact_person_phone.get()
        contact_person_email = entry_contact_person_email.get()

        if all([company_name, company_address, company_email, company_phone, 
                contact_person_name, contact_person_phone, contact_person_email]):
            conn = sqlite3.connect('invoice.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE customers 
                SET company_name = ?, company_address = ?, company_email = ?, company_phone = ?,
                    contact_person_name = ?, contact_person_phone = ?, contact_person_email = ?
                WHERE id = ?
            ''', (company_name, company_address, company_email, company_phone,
                  contact_person_name, contact_person_phone, contact_person_email, customer[0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Customer updated successfully!")
            load_customers()  # Refresh the customer list
            popup.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    popup = tk.Toplevel()
    popup.title("Edit Customer")
    popup.geometry("600x600")

    tk.Label(popup, text="Company Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_name.insert(0, customer[1])
    entry_company_name.pack(pady=5)

    tk.Label(popup, text="Company Address:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_address = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_address.insert(0, customer[2])
    entry_company_address.pack(pady=5)

    tk.Label(popup, text="Company Email:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_email = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_email.insert(0, customer[3])
    entry_company_email.pack(pady=5)

    tk.Label(popup, text="Company Phone:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_phone = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_phone.insert(0, customer[4])
    entry_company_phone.pack(pady=5)

    tk.Label(popup, text="Contact Person Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_name.insert(0, customer[5])
    entry_contact_person_name.pack(pady=5)

    tk.Label(popup, text="Contact Person Phone:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_phone = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_phone.insert(0, customer[6])
    entry_contact_person_phone.pack(pady=5)

    tk.Label(popup, text="Contact Person Email:", font=("Helvetica", 12)).pack(pady=5)
    entry_contact_person_email = tk.Entry(popup, font=("Helvetica", 12))
    entry_contact_person_email.insert(0, customer[7])
    entry_contact_person_email.pack(pady=5)

    tk.Button(popup, text="Save", command=save_changes, font=("Helvetica", 12)).pack(pady=10)

# Function to delete a customer
def delete_customer(customer_id):
    result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?")
    if result:
        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer deleted successfully!")
        load_customers()  # Refresh the customer list

# Main function to manage customers
def manage_customers(parent_frame):
    create_customer_table()

    # Create a sub-frame for the "Add Customer" button (Separate from the customer list)
    header_frame = tk.Frame(parent_frame)
    header_frame.pack(fill="x", pady=10)

    # "Add Customer" button
    button_add = tk.Button(header_frame, text="Add New Customer", command=lambda: add_customer_popup(parent_frame), font=("Helvetica", 14))
    button_add.pack(side="left", padx=10)

    # Create a sub-frame for the customer list (Customer list frame will be updated independently)
    global list_frame
    list_frame = tk.Frame(parent_frame)
    list_frame.pack(fill="both", expand=True)

    # Load customers into the list
    load_customers()
