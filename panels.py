# FILE: panels.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime
import os
from config import *
from components import ModernButton

# --- HELPER: CARD FRAME ---
def create_card_frame(parent, padding=20):
    """Creates a white floating card with shadow border"""
    card = tk.Frame(parent, bg=COLOR_WHITE, padx=padding, pady=padding)
    card.config(highlightbackground="#cbd5e1", highlightthickness=1)
    return card

# --- 1. DASHBOARD PANEL (Clean Version - No Quick Actions) ---
class DashboardPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        
        # Main Layout
        content = tk.Frame(self, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        tk.Label(content, text="Dashboard Overview", font=FONT_HEADER, bg=COLOR_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))
        
        # Stats Grid
        stats_frame = tk.Frame(content, bg=COLOR_BG)
        stats_frame.pack(fill="x", pady=(0, 30))
        
        # Fetch Data
        conn = sqlite3.connect(DB_NAME)
        items = conn.execute("SELECT sum(stock) FROM items").fetchone()[0] or 0
        today = datetime.date.today().strftime("%Y-%m-%d")
        sales = conn.execute("SELECT sum(total) FROM sales WHERE date LIKE ?", (f"{today}%",)).fetchone()[0] or 0.0
        low = conn.execute("SELECT count(*) FROM items WHERE stock <= 5").fetchone()[0]
        conn.close()
        
        # Create 3 Cards
        self.create_stat_card(stats_frame, "📦 Total Inventory", f"{items} Items", COLOR_ACCENT)
        self.create_stat_card(stats_frame, "💰 Today's Revenue", f"Rs. {sales:,.0f}", COLOR_SUCCESS)
        self.create_stat_card(stats_frame, "⚠️ Low Stock Alerts", f"{low} Items", COLOR_DANGER)

    def create_stat_card(self, parent, title, val, color):
        card = create_card_frame(parent, padding=25)
        card.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Accent Strip
        tk.Frame(card, bg=color, width=6).pack(side="left", fill="y", padx=(0, 20))
        
        # Info
        info_frame = tk.Frame(card, bg=COLOR_WHITE)
        info_frame.pack(side="left")
        
        tk.Label(info_frame, text=title, bg=COLOR_WHITE, fg=COLOR_TEXT_SEC, font=("Helvetica", 11)).pack(anchor="w")
        tk.Label(info_frame, text=val, bg=COLOR_WHITE, font=("Helvetica", 22, "bold"), fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(5, 0))


# --- 2. SALES PANEL ---
class SalesPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.cart = []
        self.app = app 
        
        split = tk.Frame(self, bg=COLOR_BG)
        split.pack(fill="both", expand=True)
        
        # === LEFT (Catalog) ===
        left_frame = tk.Frame(split, bg=COLOR_WHITE, padx=20, pady=20)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        left_frame.config(highlightbackground="#cbd5e1", highlightthickness=1)
        
        tk.Label(left_frame, text="Product Catalog", font=("Helvetica", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_WHITE).pack(anchor="w", pady=(0, 15))
        
        # Search
        search_box = tk.Frame(left_frame, bg="#f1f5f9", padx=10, pady=5, bd=0)
        search_box.pack(fill="x", pady=(0, 15))
        tk.Label(search_box, text="🔍", bg="#f1f5f9").pack(side="left")
        self.search = tk.Entry(search_box, font=("Helvetica", 12), bg="#f1f5f9", bd=0)
        self.search.pack(side="left", fill="x", expand=True, padx=10)
        self.search.bind("<KeyRelease>", self.load_items)
        
        # Table
        cols = ("ID", "Product Name", "Stock", "Price")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=18)
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Product Name", width=280, anchor="w")
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Price", width=120, anchor="e")
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.add_to_cart)
        self.tree.tag_configure('odd', background='#f8fafc'); self.tree.tag_configure('even', background='#ffffff')
        
        tk.Label(left_frame, text="Double click item to add to bill", font=("Helvetica", 9), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(pady=5)

        # === RIGHT (Billing) ===
        right_frame = tk.Frame(split, bg=COLOR_WHITE, padx=20, pady=20)
        right_frame.pack(side="right", fill="both", expand=True, ipadx=10)
        right_frame.config(highlightbackground="#cbd5e1", highlightthickness=1)
        
        tk.Label(right_frame, text="Current Order", font=("Helvetica", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_WHITE).pack(anchor="w", pady=(0, 15))
        
        # Cart Buttons (At Bottom)
        btn_grid = tk.Frame(right_frame, bg=COLOR_WHITE)
        btn_grid.pack(side="bottom", fill="x", pady=10)
        
        chk_btn = tk.Button(btn_grid, text="✅  CONFIRM & PRINT", font=("Helvetica", 11, "bold"), 
                            bg=COLOR_ACCENT, fg=COLOR_WHITE, relief="flat", pady=12, cursor="hand2", 
                            activebackground=COLOR_ACCENT_HOVER, command=self.checkout)
        chk_btn.pack(fill="x", side="bottom")
        
        clr_btn = tk.Button(btn_grid, text="🗑  CLEAR CART", font=("Helvetica", 10, "bold"), 
                            bg="#fee2e2", fg="#dc2626", relief="flat", pady=10, cursor="hand2", 
                            activebackground="#fca5a5", command=self.clear_cart)
        clr_btn.pack(fill="x", side="bottom", pady=(0, 10))
        
        # Total Box
        total_box = tk.Frame(right_frame, bg="#f8fafc", padx=15, pady=15)
        total_box.pack(side="bottom", fill="x", pady=(20, 10))
        self.total_lbl = tk.Label(total_box, text="Rs. 0", font=("Helvetica", 24, "bold"), fg=COLOR_SUCCESS, bg="#f8fafc")
        self.total_lbl.pack(anchor="e")
        tk.Label(total_box, text="Grand Total", font=("Helvetica", 10), fg=COLOR_TEXT_SEC, bg="#f8fafc").pack(anchor="e")
        
        # Cart Table (Remaining Space)
        cart_cols = ("Item", "Qty", "Total")
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_cols, show="headings")
        self.cart_tree.column("Item", width=140, anchor="w")
        self.cart_tree.column("Qty", width=50, anchor="center")
        self.cart_tree.column("Total", width=80, anchor="e")
        for c in cart_cols: self.cart_tree.heading(c, text=c)
        self.cart_tree.pack(side="top", fill="both", expand=True)

        self.load_items()

    def load_items(self, e=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        q = f"%{self.search.get()}%"
        conn = sqlite3.connect(DB_NAME)
        rows = conn.execute("SELECT id, name, stock, sale_price FROM items WHERE name LIKE ? AND stock > 0", (q,)).fetchall()
        for i, r in enumerate(rows):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]:,.0f}"), tags=(tag,))
        conn.close()

    def add_to_cart(self, e):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0])['values']
        conn = sqlite3.connect(DB_NAME)
        item = conn.execute("SELECT id, name, stock, sale_price FROM items WHERE id=?", (val[0],)).fetchone()
        conn.close()
        
        qty = simpledialog.askinteger("Qty", f"Add {item[1]} (Stock: {item[2]})", minvalue=1, maxvalue=item[2])
        if qty:
            total = qty * item[3]
            self.cart.append({"id": item[0], "name": item[1], "qty": qty, "price": item[3], "total": total})
            self.update_cart()

    def update_cart(self):
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        gt = 0
        for c in self.cart:
            self.cart_tree.insert("", "end", values=(c['name'], c['qty'], f"{c['total']:,.0f}"))
            gt += c['total']
        self.total_lbl.config(text=f"Rs. {gt:,.0f}")

    def clear_cart(self):
        self.cart = []
        self.update_cart()

    def checkout(self):
        if not self.cart: return messagebox.showwarning("Error", "Cart is empty")
        conn = sqlite3.connect(DB_NAME)
        rid = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            for c in self.cart:
                conn.execute("UPDATE items SET stock=stock-? WHERE id=?", (c['qty'], c['id']))
                conn.execute("INSERT INTO sales (receipt_id, item_id, quantity, sale_price, profit, total, date) VALUES (?,?,?,?,?,?,?)",
                             (rid, c['id'], c['qty'], c['price'], 0, c['total'], dt))
            conn.commit()
            
            if not os.path.exists(RECEIPT_DIR): os.makedirs(RECEIPT_DIR)
            path = os.path.abspath(f"{RECEIPT_DIR}/{rid}.txt")
            with open(path, "w") as f:
                f.write(f"DOLMEN CLOTHES\nReceipt #{rid}\nDate: {dt}\n{'-'*30}\n")
                for c in self.cart: f.write(f"{c['name']} x{c['qty']} = {c['total']:,.0f}\n")
                f.write(f"{'-'*30}\nTOTAL: {self.total_lbl.cget('text')}\nThank you!")
            os.startfile(path)
            self.clear_cart(); self.load_items(); messagebox.showinfo("Success", "Order Processed!")
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: conn.close()


# --- 3. INVENTORY PANEL ---
class InventoryPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        
        main_card = create_card_frame(self)
        main_card.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_card, bg=COLOR_WHITE)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Inventory Management", font=("Helvetica", 18, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_WHITE).pack(side="left")
        ModernButton(header, text="➕ Add New Item", bg=COLOR_SUCCESS, command=self.add_item).pack(side="right")
        
        # Search
        search_box = tk.Frame(main_card, bg="#f1f5f9", padx=10, pady=5)
        search_box.pack(fill="x", pady=(0, 15))
        tk.Label(search_box, text="Search Item:", bg="#f1f5f9", font=("Helvetica", 10, "bold")).pack(side="left", padx=(0,10))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.load_data)
        tk.Entry(search_box, textvariable=self.search_var, font=("Helvetica", 11), bg="white", relief="flat").pack(side="left", fill="x", expand=True)
        
        # Table
        cols = ("ID", "Name", "Category", "Season", "Cost", "Price", "Stock")
        self.tree = ttk.Treeview(main_card, columns=cols, show="headings", height=15)
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("Category", width=100, anchor="center")
        self.tree.column("Season", width=100, anchor="center")
        self.tree.column("Cost", width=100, anchor="e")
        self.tree.column("Price", width=100, anchor="e")
        self.tree.column("Stock", width=80, anchor="center")
        
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure('odd', background='#f8fafc'); self.tree.tag_configure('even', background='#ffffff')
        
        # Actions
        btn_frame = tk.Frame(main_card, bg=COLOR_WHITE)
        btn_frame.pack(fill="x", pady=20)
        ModernButton(btn_frame, text="✏️ Edit Item", command=self.edit_item).pack(side="left", padx=(0, 10))
        ModernButton(btn_frame, text="🗑️ Delete Item", command=self.delete_item, bg=COLOR_DANGER).pack(side="left")
        
        self.load_data()

    def load_data(self, *args):
        for i in self.tree.get_children(): self.tree.delete(i)
        q = f"%{self.search_var.get()}%"
        conn = sqlite3.connect(DB_NAME)
        rows = conn.execute("SELECT * FROM items WHERE name LIKE ? ORDER BY id DESC", (q,)).fetchall()
        for i, r in enumerate(rows):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=r, tags=(tag,))
        conn.close()

    def add_item(self): self.popup("Add Item")
    def edit_item(self):
        sel = self.tree.selection()
        if sel: self.popup("Edit Item", self.tree.item(sel[0])['values'])
    def delete_item(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Confirm", "Delete this item?"):
            iid = self.tree.item(sel[0])['values'][0]
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM items WHERE id=?", (iid,)); conn.commit(); conn.close()
            self.load_data()

    def popup(self, title, data=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x500")
        top.configure(bg=COLOR_WHITE)
        
        tk.Label(top, text=title, font=("Helvetica", 16, "bold"), bg=COLOR_WHITE, fg=COLOR_SIDEBAR).pack(pady=20)
        
        fields = ["Name", "Category", "Season", "Purchase Price", "Sale Price", "Stock"]
        entries = {}
        
        for f in fields:
            frame = tk.Frame(top, bg=COLOR_WHITE); frame.pack(fill="x", padx=30, pady=5)
            tk.Label(frame, text=f, bg=COLOR_WHITE, font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_SEC).pack(anchor="w")
            if f in ["Category", "Season"]:
                vals = ["Men", "Women", "Kids"] if f=="Category" else ["Summer", "Winter", "All"]
                e = ttk.Combobox(frame, values=vals, font=("Helvetica", 10)); e.pack(fill="x", pady=2)
            else:
                e = tk.Entry(frame, font=("Helvetica", 10), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
                e.pack(fill="x", pady=2, ipady=5)
            entries[f] = e
            if data:
                idx = fields.index(f) + 1
                if f in ["Category", "Season"]: e.set(data[idx])
                else: e.insert(0, data[idx])

        def save():
            try:
                v = [entries[f].get() for f in fields]
                v[3], v[4], v[5] = float(v[3]), float(v[4]), int(v[5])
                conn = sqlite3.connect(DB_NAME)
                if data: conn.execute("UPDATE items SET name=?, category=?, season=?, purchase_price=?, sale_price=?, stock=? WHERE id=?", v + [data[0]])
                else: conn.execute("INSERT INTO items (name, category, season, purchase_price, sale_price, stock) VALUES (?,?,?,?,?,?)", v)
                conn.commit(); conn.close(); self.load_data(); top.destroy()
            except: messagebox.showerror("Error", "Invalid inputs")
        
        ModernButton(top, text="SAVE ITEM", command=save).pack(fill="x", padx=30, pady=30)


# --- 4. PURCHASE PANEL (Redesigned Form) ---
class PurchasePanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(expand=True, fill="both")
        
        card = create_card_frame(wrapper, padding=40)
        card.place(relx=0.5, rely=0.5, anchor="center", width=500)
        
        tk.Label(card, text="📦 Stock Entry", font=("Helvetica", 20, "bold"), bg=COLOR_WHITE, fg=COLOR_SIDEBAR).pack(pady=(0, 30))
        
        self.create_label(card, "Select Item")
        self.item_combo = ttk.Combobox(card, font=("Helvetica", 11))
        self.item_combo.pack(fill="x", pady=(0, 15))
        
        self.create_label(card, "Quantity to Add")
        self.qty = tk.Entry(card, font=("Helvetica", 11), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
        self.qty.pack(fill="x", ipady=8, pady=(0, 15))
        
        self.create_label(card, "New Cost Price (Optional Update)")
        self.cost = tk.Entry(card, font=("Helvetica", 11), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
        self.cost.pack(fill="x", ipady=8, pady=(0, 25))
        
        ModernButton(card, text="UPDATE STOCK", command=self.save).pack(fill="x", ipady=5)
        
        self.items_map = {}
        self.load_items()

    def create_label(self, p, t):
        tk.Label(p, text=t, font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(anchor="w", pady=(0, 5))

    def load_items(self):
        conn = sqlite3.connect(DB_NAME)
        for r in conn.execute("SELECT id, name, purchase_price FROM items"):
            self.items_map[f"{r[1]} (Cost: {r[2]})"] = r[0]
        conn.close()
        self.item_combo['values'] = list(self.items_map.keys())

    def save(self):
        try:
            item_id = self.items_map[self.item_combo.get()]
            q = int(self.qty.get())
            c = float(self.cost.get())
            conn = sqlite3.connect(DB_NAME)
            conn.execute("UPDATE items SET stock=stock+?, purchase_price=? WHERE id=?", (q, c, item_id))
            conn.execute("INSERT INTO purchases (item_id, quantity, purchase_price, date) VALUES (?,?,?,?)",
                        (item_id, q, c, datetime.datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Stock Added"); self.load_items()
        except: messagebox.showerror("Error", "Invalid Data")


# --- 5. REPORTS PANEL (Redesigned) ---
class ReportsPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        
        main_card = create_card_frame(self, padding=30)
        main_card.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(main_card, text="Financial Reports", font=("Helvetica", 18, "bold"), bg=COLOR_WHITE, fg=COLOR_TEXT_MAIN).pack(anchor="w")
        
        filter_frame = tk.Frame(main_card, bg=COLOR_WHITE)
        filter_frame.pack(fill="x", pady=20)
        
        ModernButton(filter_frame, text="Today's Report", command=lambda: self.gen('day')).pack(side="left", padx=(0, 10))
        ModernButton(filter_frame, text="Monthly Report", command=lambda: self.gen('month')).pack(side="left", padx=10)
        
        self.text = tk.Text(main_card, font=("Consolas", 11), bg="#f8fafc", relief="flat", padx=20, pady=20)
        self.text.pack(fill="both", expand=True)

    def gen(self, type):
        self.text.delete(1.0, 'end')
        start = datetime.datetime.now().strftime("%Y-%m-%d") if type == 'day' else datetime.datetime.now().strftime("%Y-%m-01")
        conn = sqlite3.connect(DB_NAME)
        res = conn.execute("SELECT count(*), sum(total), sum(profit) FROM sales WHERE date >= ?", (start,)).fetchone()
        conn.close()
        
        rpt = f"""
        ========================================
        FINANCIAL REPORT ({type.upper()})
        Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
        ========================================
        
        Total Transactions : {res[0]}
        Total Revenue      : Rs. {res[1] or 0:,.2f}
        Net Profit         : Rs. {res[2] or 0:,.2f}
        
        ========================================
        """
        self.text.insert('end', rpt)


# --- 6. SETTINGS PANEL (Redesigned Form) ---
class SettingsPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(expand=True, fill="both")
        
        card = create_card_frame(wrapper, padding=40)
        card.place(relx=0.5, rely=0.5, anchor="center", width=500)
        
        tk.Label(card, text="⚙️ Store Settings", font=("Helvetica", 20, "bold"), bg=COLOR_WHITE, fg=COLOR_SIDEBAR).pack(pady=(0, 30))
        
        self.entries = {}
        fields = ["Shop Name", "Address", "Phone", "Terms"]
        vals = app.db.get_shop_info()
        data = [vals[1], vals[2], vals[3], vals[4]]
        
        for i, f in enumerate(fields):
            tk.Label(card, text=f, font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_SEC, bg=COLOR_WHITE).pack(anchor="w", pady=(0, 5))
            e = tk.Entry(card, font=("Helvetica", 11), bg="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
            e.pack(fill="x", ipady=8, pady=(0, 15))
            e.insert(0, data[i])
            self.entries[f] = e
            
        ModernButton(card, text="SAVE CHANGES", command=self.save).pack(fill="x", ipady=5, pady=10)

    def save(self):
        d = [self.entries[f].get() for f in ["Shop Name", "Address", "Phone", "Terms"]]
        conn = sqlite3.connect(DB_NAME)
        conn.execute("UPDATE shop_info SET name=?, address=?, phone=?, terms=? WHERE id=1", d)
        conn.commit(); conn.close()
        messagebox.showinfo("Saved", "Settings Updated")