import customtkinter as ctk
from gui.app import App

if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # Imposta la modalità scura come predefinita
    ctk.set_default_color_theme("green")  # Imposta il tema di colore predefinito a verde
    app = App()
    app.mainloop()