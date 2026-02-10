import ctypes
import customtkinter as ctk
from gui.app import App

# Fix para que el icono se vea en la barra de tareas de Windows
try:
    myappid = 'antigravity.diagramgenerator.3000.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Configuración de tema de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = App()
    app.mainloop()
