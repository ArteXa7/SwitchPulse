import customtkinter as ctk
from ui.app import App
import sys
import ctypes

if sys.platform == "win32":
    myappid = "switchpulse.network.automation.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def main():
    # Set appearance
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
