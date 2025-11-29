# FILE: main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk  # Ensure Pillow is installed (pip install pillow)

# Import functionalities from other modules
from config import *
from database import DBManager
from components import ModernButton, SidebarButton
from panels import DashboardPanel, InventoryPanel, SalesPanel, ReportsPanel, SettingsPanel, PurchasePanel

class ClothesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dolmen Clothes Management System")
        self.geometry("1280x800")
        self.state("zoomed")
        self.configure(bg=COLOR_BG)
        
        # Initialize Database
        self.db = DBManager()
        self.user = None
        self.role = None
        
        # Ensure Receipt Directory Exists
        if not os.path.exists(RECEIPT_DIR): os.makedirs(RECEIPT_DIR)
        
        # --- GLOBAL STYLES ---
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview (Table) Styling
        style.configure("Treeview", 
                        background=COLOR_WHITE, 
                        foreground=COLOR_TEXT_MAIN, 
                        rowheight=40,
                        fieldbackground=COLOR_WHITE,
                        font=("Helvetica", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background="#e2e8f0", 
                        foreground=COLOR_TEXT_MAIN, 
                        font=("Helvetica", 10, "bold"),
                        padding=12)
        style.map("Treeview", background=[('selected', COLOR_ACCENT)])

        # Main Container
        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def show_login(self):
        # Clear current screen
        for w in self.container.winfo_children(): w.destroy()
        
        # --- SPLIT SCREEN LOGIN LAYOUT ---
        
        # 1. LEFT SIDE (Brand & Logo) - Dark Theme
        left_frame = tk.Frame(self.container, bg=COLOR_SIDEBAR)
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        # Branding Container (Centered in Left Frame)
        brand_container = tk.Frame(left_frame, bg=COLOR_SIDEBAR)
        brand_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Try Loading Logo
        try:
            load = Image.open(DEFAULT_LOGO)
            load = load.resize((180, 180), Image.Resampling.LANCZOS)
            render = ImageTk.PhotoImage(load)
            img_lbl = tk.Label(brand_container, image=render, bg=COLOR_SIDEBAR)
            img_lbl.image = render # Keep reference
            img_lbl.pack(pady=(0, 20))
        except:
            # Fallback if logo.png is missing
            tk.Label(brand_container, text="👗", font=("Segoe UI", 100), bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack(pady=(0, 20))
            
        tk.Label(brand_container, text="DOLMEN", font=("Helvetica", 40, "bold"), fg=COLOR_WHITE, bg=COLOR_SIDEBAR).pack()
        tk.Label(brand_container, text="CLOTHES POS", font=("Helvetica", 20, "bold"), fg="#94a3b8", bg=COLOR_SIDEBAR).pack(pady=(5, 0))
        tk.Label(brand_container, text="Professional Retail Management", font=("Helvetica", 12), fg="#64748b", bg=COLOR_SIDEBAR).pack(pady=(30, 0))


        # 2. RIGHT SIDE (Login Form) - White Theme
        right_frame = tk.Frame(self.container, bg=COLOR_WHITE)
        right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Login Box (Centered in Right Frame)
        login_box = tk.Frame(right_frame, bg=COLOR_WHITE, padx=50)
        login_box.place(relx=0.5, rely=0.5, anchor="center", width=450)
        
        tk.Label(login_box, text="Hello Again! 👋", font=("Helvetica", 28, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_WHITE).pack(anchor="w")
        tk.Label(login_box, text="Sign in to your account", font=("Helvetica", 11), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(anchor="w", pady=(5, 40))
        
        # Username Field
        tk.Label(login_box, text="USERNAME", font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(anchor="w")
        u_entry = tk.Entry(login_box, font=("Helvetica", 12), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
        u_entry.pack(fill="x", ipady=12, pady=(8, 20))
        
        # Password Field
        tk.Label(login_box, text="PASSWORD", font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(anchor="w")
        p_entry = tk.Entry(login_box, show="•", font=("Helvetica", 12), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
        p_entry.pack(fill="x", ipady=12, pady=(8, 30))
        
        # Login Logic
        def login(event=None):
            conn = sqlite3.connect(DB_NAME)
            res = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (u_entry.get(), p_entry.get())).fetchone()
            conn.close()
            
            if res:
                self.user = u_entry.get()
                self.role = res[0]
                self.load_dashboard()
            else:
                messagebox.showerror("Access Denied", "Invalid Username or Password")
        
        # Bind Enter Key for convenience
        self.bind('<Return>', login)

        # Login Button
        btn = tk.Button(login_box, text="SIGN IN", font=("Helvetica", 11, "bold"), bg=COLOR_SIDEBAR, fg=COLOR_WHITE, 
                        relief="flat", cursor="hand2", command=login, 
                        activebackground=COLOR_SIDEBAR_HOVER, activeforeground=COLOR_WHITE)
        btn.pack(fill="x", ipady=12)
        
        # Footer
        tk.Label(login_box, text="Default: admin/admin123  |  staff/staff123", font=("Helvetica", 9), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(pady=20)

    def load_dashboard(self):
        for w in self.container.winfo_children(): w.destroy()
        
        # --- SIDEBAR (Navigation) ---
        sidebar = tk.Frame(self.container, bg=COLOR_SIDEBAR, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Brand Header
        tk.Label(sidebar, text="Dolmen POS", font=("Helvetica", 20, "bold"), bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack(pady=(40, 10), padx=20, anchor="w")
        tk.Label(sidebar, text=f"Logged as: {self.user.title()}", font=("Helvetica", 9), bg=COLOR_SIDEBAR, fg="#94a3b8").pack(padx=20, anchor="w", pady=(0, 40))
        
        # --- MENU BUTTONS ---
        
        # 1. Dashboard (For Everyone)
        self.create_nav_btn(sidebar, "Dashboard", lambda: self.nav("dash"), "📊")

        # 2. Staff Specific (New Sale)
        if self.role == 'staff':
            self.create_nav_btn(sidebar, "New Sale", lambda: self.nav("sales"), "🛍️")
        
        # 3. Admin Specific (Management Tools)
        if self.role == 'admin':
            self.create_nav_btn(sidebar, "Inventory", lambda: self.nav("inv"), "📦")
            self.create_nav_btn(sidebar, "Stock Entry", lambda: self.nav("buy"), "🚚")
            self.create_nav_btn(sidebar, "Reports", lambda: self.nav("rep"), "📈")
            self.create_nav_btn(sidebar, "Settings", lambda: self.nav("set"), "⚙️")
        
        # Logout Button (Bottom)
        tk.Frame(sidebar, bg=COLOR_SIDEBAR).pack(expand=True)
        self.create_nav_btn(sidebar, "Logout", self.show_login, "🚪")
        
        # --- MAIN CONTENT AREA ---
        self.content = tk.Frame(self.container, bg=COLOR_BG)
        self.content.pack(side="right", fill="both", expand=True)
        
        # Load Dashboard by default
        self.nav("dash")

    def create_nav_btn(self, parent, text, cmd, icon):
        """Helper to create consistent sidebar buttons"""
        btn = tk.Button(parent, text=f"  {icon}   {text}", font=("Helvetica", 11), bg=COLOR_SIDEBAR, fg="#e2e8f0", 
                        anchor="w", padx=20, pady=12, bd=0, cursor="hand2", 
                        activebackground=COLOR_SIDEBAR_HOVER, activeforeground=COLOR_WHITE, command=cmd)
        btn.pack(fill="x", pady=2)

    def nav(self, page):
        """Switch between different panels"""
        for w in self.content.winfo_children(): w.destroy()
        
        # Wrapper for padding/margins
        wrapper = tk.Frame(self.content, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=30, pady=30)
        
        if page == "dash": DashboardPanel(wrapper, self).pack(fill="both", expand=True)
        if page == "sales": SalesPanel(wrapper, self).pack(fill="both", expand=True)
        if page == "inv": InventoryPanel(wrapper, self).pack(fill="both", expand=True)
        if page == "buy": PurchasePanel(wrapper, self).pack(fill="both", expand=True)
        if page == "rep": ReportsPanel(wrapper, self).pack(fill="both", expand=True)
        if page == "set": SettingsPanel(wrapper, self).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ClothesApp()
    app.mainloop()