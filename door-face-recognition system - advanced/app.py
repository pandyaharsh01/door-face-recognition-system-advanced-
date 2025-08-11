import customtkinter as ctk
import os
from utils.gui_utils import create_login_frame, create_dashboard_frame

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Face Recognition Door Access")
        self.root.geometry("600x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = create_login_frame(self.root, self.show_dashboard)

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = create_dashboard_frame(self.root)

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()