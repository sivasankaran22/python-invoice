import tkinter as tk
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3

# Function to manage invoices
def manage_invoices(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    invoice_frame = tk.Frame(frame)
    invoice_frame.pack(fill="both", expand=True)

    def generate_invoice():
        selected_customer = askstring("Input", "Enter Customer ID:")
        if selected_customer:
            conn = sqlite3.connect('invoice_app.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (selected_customer,))
            customer = cursor.fetchone()

            if customer:
                total_amount = 0  # Placeholder for total amount calculation
                invoice_file = f"invoice_{selected_customer}.pdf"
                c = canvas.Canvas(invoice_file, pagesize=letter)
                c.setFont("Helvetica", 12)
                c.drawString(100, 750, f"Invoice for Customer ID: {selected_customer}")
                c.drawString(100, 730, "----------------------------------------")
                c.drawString(100, 710, f"Total: ${total_amount}")
                c.save()
                messagebox.showinfo("Invoice Generated", f"Invoice saved as {invoice_file}")
            conn.close()

    invoice_button = tk.Button(invoice_frame, text="Generate Invoice", command=generate_invoice, font=("Helvetica", 14))
    invoice_button.pack(pady=10)
