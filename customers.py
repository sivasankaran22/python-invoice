import tkinter as tk
from tkinter import messagebox
import sqlite3
import re  # Import the regular expression module

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

# Function to add a new customer with validation
def add_customer_popup(parent_frame):
    def validate_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    def validate_phone(phone):
        phone_regex = r'^\d{10}$'  # Basic validation for 10-digit phone number
        return re.match(phone_regex, phone)

    def save_customer():
        company_name = entry_company_name.get()
        company_address = entry_company_address.get("1.0", "end").strip()
        company_email = entry_company_email.get()
        company_phone = entry_company_phone.get()
        contact_person_name = entry_contact_person_name.get()
        contact_person_phone = entry_contact_person_phone.get()
        contact_person_email = entry_contact_person_email.get()

        if not all([company_name, company_address, company_email, company_phone,
                    contact_person_name, contact_person_phone, contact_person_email]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not validate_email(company_email) or not validate_email(contact_person_email):
            messagebox.showwarning("Input Error", "Invalid email address.")
            return

        if not validate_phone(company_phone) or not validate_phone(contact_person_phone):
            messagebox.showwarning("Input Error", "Invalid phone number.")
            return

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
        popup.destroy()
        load_customers(parent_frame)  # Refresh the customer list

    popup = tk.Toplevel()
    popup.title("Add Customer")
    popup.geometry("600x600")

    tk.Label(popup, text="Company Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_name.pack(pady=5)

    tk.Label(popup, text="Company Address:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_address = tk.Text(popup, font=("Helvetica", 12), height=5, width=40)
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

"""
# Function to load customers into the table
def load_customers(list_frame):
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
    headers = ["Sr. No.", "Company Name", "Company Email", "Company Phone", "Contact Name", "Contact Phone", "Contact Email", "Actions"]
    
    # Display headers at the top of the list
    for col, header in enumerate(headers):
        tk.Label(list_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")

    # Display each customer's details in the list
    for row, customer in enumerate(customers, start=1):
        # Display the serial number in the first column
        tk.Label(list_frame, text=row, font=("Helvetica", 12)).grid(row=row, column=0, padx=10, pady=5, sticky="w")

        # Display each customer's details in the corresponding columns (except the serial number)
        for col, value in enumerate(customer[1:], start=1):  # Skipping the 'id' (customer[0])
            tk.Label(list_frame, text=value, font=("Helvetica", 12)).grid(row=row, column=col, padx=10, pady=5, sticky="w")

        # Add Edit and Delete buttons in the last column
        tk.Button(list_frame, text="Edit", font=("Helvetica", 10), command=lambda c=customer: edit_customer_popup(list_frame, c)).grid(row=row, column=7, padx=5)
        tk.Button(list_frame, text="Delete", font=("Helvetica", 10), command=lambda c=customer: delete_customer(list_frame, c[0])).grid(row=row, column=8, padx=5)

////////// with paginate //////////////
def load_customers(list_frame, page=1, items_per_page=10):
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

    # Fetch customer data
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    total_pages = (total_customers + items_per_page - 1) // items_per_page

    offset = (page - 1) * items_per_page
    cursor.execute("SELECT * FROM customers LIMIT ? OFFSET ?", (items_per_page, offset))
    customers = cursor.fetchall()
    conn.close()

    # If no customers are found, display a message
    if not customers:
        tk.Label(scrollable_frame, text="No customers found.", font=("Helvetica", 14)).pack(pady=10)
        return

    # Display headers
    headers = ["Sr. No.", "Company Name", "Company Address", "Company Email", "Company Phone", "Contact Name", "Contact Phone", "Contact Email", "Actions"]
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

    # Display customer data
    for row, customer in enumerate(customers, start=1):
        tk.Label(scrollable_frame, text=(offset + row), font=("Helvetica", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        for col, value in enumerate(customer[1:], start=1):
            tk.Label(scrollable_frame, text=value, font=("Helvetica", 12)).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        # Action buttons
        button_frame = tk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=8, padx=5, pady=5)
        tk.Button(button_frame, text="Edit", font=("Helvetica", 10), command=lambda c=customer: edit_customer_popup(list_frame, c)).pack(side="left", padx=2)
        tk.Button(button_frame, text="Delete", font=("Helvetica", 10), command=lambda c=customer: delete_customer(list_frame, c[0])).pack(side="left", padx=2)

    # Update canvas scroll region
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Pagination controls at the bottom center (directly below the table)
    pagination_frame = tk.Frame(scrollable_frame)
    pagination_frame.grid(row=len(customers) + 1, column=0, columnspan=len(headers), pady=10)

    if page > 1:
        tk.Button(pagination_frame, text="Previous", font=("Helvetica", 10),
                  command=lambda: load_customers(list_frame, page - 1, items_per_page)).pack(side="left", padx=10)

    tk.Label(pagination_frame, text=f"Page {page} of {total_pages}", font=("Helvetica", 12)).pack(side="left", padx=10)

    if page < total_pages:
        tk.Button(pagination_frame, text="Next", font=("Helvetica", 10),
                  command=lambda: load_customers(list_frame, page + 1, items_per_page)).pack(side="left", padx=10)
"""

def load_customers(list_frame, page=1, items_per_page=10, search_term=""):
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

    # Fetch customer data with an optional search term
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    if search_term:
        query = """
        SELECT COUNT(*) FROM customers 
        WHERE company_name LIKE ? OR company_address LIKE ? OR company_email LIKE ? 
        OR company_phone LIKE ? OR contact_person_name LIKE ? 
        OR contact_person_phone LIKE ? OR contact_person_email LIKE ?
        """
        cursor.execute(query, 
                       ('%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%'))
    else:
        cursor.execute("SELECT COUNT(*) FROM customers")
    
    total_customers = cursor.fetchone()[0]
    total_pages = (total_customers + items_per_page - 1) // items_per_page

    offset = (page - 1) * items_per_page
    if search_term:
        query = """
        SELECT * FROM customers 
        WHERE company_name LIKE ? OR company_address LIKE ? OR company_email LIKE ? 
        OR company_phone LIKE ? OR contact_person_name LIKE ? 
        OR contact_person_phone LIKE ? OR contact_person_email LIKE ? 
        LIMIT ? OFFSET ?
        """
        cursor.execute(query, 
                       ('%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', '%' + search_term + '%', 
                        '%' + search_term + '%', items_per_page, offset))
    else:
        cursor.execute("SELECT * FROM customers LIMIT ? OFFSET ?", (items_per_page, offset))

    customers = cursor.fetchall()
    conn.close()

    # If no customers are found, display a message
    if not customers:
        tk.Label(scrollable_frame, text="No customers found.", font=("Helvetica", 14)).pack(pady=10)
        return

    # Display headers
    headers = ["Sr. No.", "Company Name", "Company Address", "Company Email", "Company Phone", "Contact Name", "Contact Phone", "Contact Email", "Actions"]
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Helvetica", 12, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

    # Display customer data
    for row, customer in enumerate(customers, start=1):
        tk.Label(scrollable_frame, text=(offset + row), font=("Helvetica", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        for col, value in enumerate(customer[1:], start=1):
            tk.Label(scrollable_frame, text=value, font=("Helvetica", 12)).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        # Action buttons
        button_frame = tk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=8, padx=5, pady=5)
        tk.Button(button_frame, text="Edit", font=("Helvetica", 10), command=lambda c=customer: edit_customer_popup(list_frame, c)).pack(side="left", padx=2)
        tk.Button(button_frame, text="Delete", font=("Helvetica", 10), command=lambda c=customer: delete_customer(list_frame, c[0])).pack(side="left", padx=2)

    # Update canvas scroll region
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Pagination controls at the bottom center (directly below the table)
    pagination_frame = tk.Frame(scrollable_frame)
    pagination_frame.grid(row=len(customers) + 1, column=0, columnspan=len(headers), pady=10)

    if page > 1:
        tk.Button(pagination_frame, text="Previous", font=("Helvetica", 10),
                  command=lambda: load_customers(list_frame, page - 1, items_per_page, search_term)).pack(side="left", padx=10)

    tk.Label(pagination_frame, text=f"Page {page} of {total_pages}", font=("Helvetica", 12)).pack(side="left", padx=10)

    if page < total_pages:
        tk.Button(pagination_frame, text="Next", font=("Helvetica", 10),
                  command=lambda: load_customers(list_frame, page + 1, items_per_page, search_term)).pack(side="left", padx=10)



# Function to edit an existing customer
def edit_customer_popup(parent_frame, customer):
    def validate_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    def validate_phone(phone):
        phone_regex = r'^\d{10}$'  # Basic validation for 10-digit phone number
        return re.match(phone_regex, phone)

    def save_changes():
        company_name = entry_company_name.get()
        company_address = entry_company_address.get("1.0", "end").strip()
        company_email = entry_company_email.get()
        company_phone = entry_company_phone.get()
        contact_person_name = entry_contact_person_name.get()
        contact_person_phone = entry_contact_person_phone.get()
        contact_person_email = entry_contact_person_email.get()

        if not all([company_name, company_address, company_email, company_phone,
                    contact_person_name, contact_person_phone, contact_person_email]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not validate_email(company_email) or not validate_email(contact_person_email):
            messagebox.showwarning("Input Error", "Invalid email address.")
            return

        if not validate_phone(company_phone) or not validate_phone(contact_person_phone):
            messagebox.showwarning("Input Error", "Invalid phone number.")
            return

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
        popup.destroy()
        load_customers(parent_frame)  # Refresh the customer list

    popup = tk.Toplevel()
    popup.title("Edit Customer")
    popup.geometry("600x600")

    tk.Label(popup, text="Company Name:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_name = tk.Entry(popup, font=("Helvetica", 12))
    entry_company_name.insert(0, customer[1])
    entry_company_name.pack(pady=5)

    tk.Label(popup, text="Company Address:", font=("Helvetica", 12)).pack(pady=5)
    entry_company_address = tk.Text(popup, font=("Helvetica", 12), height=5, width=40)
    entry_company_address.insert("1.0", customer[2])  # Insert text at the beginning
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
def delete_customer(parent_frame, customer_id):
    result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?")
    if result:
        conn = sqlite3.connect('invoice.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer deleted successfully!")
        load_customers(parent_frame)  # Refresh the customer list

# Main function to manage customers
def manage_customers(parent_frame):
    create_customer_table()

    # Header Frame
    header_frame = tk.Frame(parent_frame)
    header_frame.pack(fill="x", pady=10)

    # "Add New Customer" Button
    button_add = tk.Button(header_frame, text="Add New Customer", command=lambda: add_customer_popup(parent_frame), font=("Helvetica", 14))
    button_add.pack(side="left", padx=10)

    # Search Bar (Label + Entry + Button) next to the "Add New Customer" Button
    search_label = tk.Label(header_frame, text="Search:", font=("Helvetica", 12))
    search_label.pack(side="left", padx=10)

    search_entry = tk.Entry(header_frame, font=("Helvetica", 12))
    search_entry.pack(side="left", padx=10)

    def search_customers():
        search_term = search_entry.get()
        load_customers(list_frame, page=1, search_term=search_term)

    search_button = tk.Button(header_frame, text="Search", font=("Helvetica", 12), command=search_customers)
    search_button.pack(side="left", padx=10)

    # List Frame for the table
    list_frame = tk.Frame(parent_frame)
    list_frame.pack(fill="both", expand=True)

    load_customers(list_frame, page=1)  # Default to page 1

