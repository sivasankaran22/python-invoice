import tkinter as tk
from tkinter import messagebox
from auth import check_login
from customers import manage_customers
from products import manage_products
from invoices import manage_invoices

# Function to create the main window
def open_main_app():
    root = tk.Tk()
    root.title("Invoice Generator")
    root.state('zoomed')  # Set to full screen

    # Font configuration
    font = ("Helvetica", 14)

    # Frame management
    frame_customers = tk.Frame(root)
    frame_products = tk.Frame(root)
    frame_invoices = tk.Frame(root)

    def hide_all_frames():
        """Hide all frames to display only the selected one."""
        frame_customers.pack_forget()
        frame_products.pack_forget()
        frame_invoices.pack_forget()

    def clear_frame(frame):
        """Clear the widgets from the frame before displaying new content."""
        for widget in frame.winfo_children():
            widget.destroy()

    def show_customers():
        hide_all_frames()
        clear_frame(frame_customers)  # Clear previous content
        frame_customers.pack(fill="both", expand=True)
        manage_customers(frame_customers)

    def show_products():
        hide_all_frames()
        clear_frame(frame_products)  # Clear previous content
        frame_products.pack(fill="both", expand=True)
        manage_products(frame_products)

    def show_invoices():
        hide_all_frames()
        clear_frame(frame_invoices)  # Clear previous content
        frame_invoices.pack(fill="both", expand=True)
        manage_invoices(frame_invoices)

    # Create the navigation bar
    navbar = tk.Frame(root, bg="gray", height=50)
    navbar.pack(fill="x", side="top")

    button_customers = tk.Button(navbar, text="Customers", command=show_customers, font=font)
    button_customers.pack(side="left", padx=10, pady=5)

    button_products = tk.Button(navbar, text="Products", command=show_products, font=font)
    button_products.pack(side="left", padx=10, pady=5)

    button_invoices = tk.Button(navbar, text="Invoices", command=show_invoices, font=font)
    button_invoices.pack(side="left", padx=10, pady=5)

    # Start with the customers module
    show_customers()

    root.mainloop()

# Run the login window
if __name__ == "__main__":
    check_login(open_main_app)
