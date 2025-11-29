import tkinter as tk
from config import *

class ModernButton(tk.Button):
    """Stylized Button for Main Actions (Login, Add, Save)"""
    def __init__(self, master, **kwargs):
        # Default Background is Accent Color
        bg = kwargs.pop('bg', COLOR_ACCENT)
        fg = kwargs.pop('fg', COLOR_WHITE)
        super().__init__(master, **kwargs)
        
        self.config(bg=bg, fg=fg, relief="flat", font=FONT_BOLD, pady=8, cursor="hand2", 
                    activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_WHITE)
        
        # Hover Effects
        self.bind("<Enter>", lambda e: self.config(bg=COLOR_ACCENT_HOVER))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

class SidebarButton(tk.Button):
    """Stylized Button for Sidebar Navigation"""
    def __init__(self, master, text, command, icon):
        super().__init__(master, text=f"  {icon}   {text}", command=command, anchor="w")
        
        self.config(bg=COLOR_SIDEBAR, fg="#ecf0f1", relief="flat", font=("Helvetica", 11), 
                    padx=20, pady=12, bd=0, cursor="hand2", 
                    activebackground=COLOR_SIDEBAR_HOVER, activeforeground=COLOR_WHITE)
        
        # Hover Effects
        self.bind("<Enter>", lambda e: self.config(bg=COLOR_SIDEBAR_HOVER))
        self.bind("<Leave>", lambda e: self.config(bg=COLOR_SIDEBAR))