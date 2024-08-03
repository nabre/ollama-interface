import os
import sys
import customtkinter
import subprocess

def find_customtkinter_icon():
    customtkinter_path = os.path.dirname(customtkinter.__file__)
    icon_path = os.path.join(customtkinter_path, "assets", "icons", "CustomTkinter_icon_Windows.ico")
    if not os.path.exists(icon_path):
        print("Icona di customtkinter non trovata.")
        sys.exit(1)
    return icon_path

def main():
    icon_path = find_customtkinter_icon()
    
    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        "--add-data", f"{os.path.dirname(customtkinter.__file__)}:customtkinter",
        "launcher.py"
    ]
    
    print("Esecuzione del comando PyInstaller:")
    print(" ".join(command))
    
    subprocess.run(command, check=True)
    
    print("Compilazione completata. Verifica l'eseguibile nella cartella 'dist'.")

if __name__ == "__main__":
    main()