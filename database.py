# FILE: database.py
import sqlite3
from config import *

class DBManager:
    def __init__(self):
        self.conn = None
        self.init_db()

    def connect(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def init_db(self):
        self.conn = sqlite3.connect(DB_NAME)
        cur = self.conn.cursor()
        
        # 1. Users
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            password TEXT, 
            role TEXT)''')

        # 2. Shop Info
        cur.execute('''CREATE TABLE IF NOT EXISTS shop_info (
            id INTEGER PRIMARY KEY CHECK (id = 1), 
            name TEXT, address TEXT, phone TEXT, terms TEXT)''')

        # 3. Items (Ensure Prices are REAL/FLOAT)
        cur.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, category TEXT, season TEXT, 
            purchase_price REAL, sale_price REAL, stock INTEGER)''')

        # 4. Sales
        cur.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            receipt_id TEXT, item_id INTEGER, quantity INTEGER, 
            sale_price REAL, profit REAL, total REAL, date TEXT)''')

        # 5. Purchases
        cur.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            item_id INTEGER, quantity INTEGER, 
            purchase_price REAL, date TEXT)''')
            
        # Seed Data (Default Users)
        try:
            cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
            cur.execute("INSERT INTO users (username, password, role) VALUES ('staff', 'staff123', 'staff')")
        except: pass
        
        # Default Shop Info
        cur.execute("SELECT count(*) FROM shop_info")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO shop_info VALUES (1, ?, ?, ?, ?)", 
                        (DEFAULT_SHOP_NAME, "123 Market St", "0300-1234567", "No Returns"))
        
        # Default Items for Testing
        cur.execute("SELECT count(*) FROM items")
        if cur.fetchone()[0] == 0:
            items = [
                ("Men Formal Shirt", "Men", "Summer", 800.0, 1500.0, 50),
                ("Women Kurti", "Women", "Summer", 1000.0, 1800.0, 28),
                ("Kids Winter Jacket", "Kids", "Winter", 1200.0, 2500.0, 19)
            ]
            cur.executemany("INSERT INTO items (name, category, season, purchase_price, sale_price, stock) VALUES (?,?,?,?,?,?)", items)

        self.conn.commit()
        self.conn.close()

    def get_shop_info(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM shop_info WHERE id=1")
        data = cur.fetchone()
        conn.close()
        return data