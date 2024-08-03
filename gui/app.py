import customtkinter as ctk
from gui.chat_page import ChatPage
from gui.models_page import ModelsPage
from gui.modelfile_page import ModelfilePage
from utils.ollama_api import OllamaAPI

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")  # Imposta il tema scuro come predefinito
        ctk.set_default_color_theme("green")

        self.title("Ollama Chat")
        self.geometry("1200x800")

        self.ollama_api = OllamaAPI()
        self.models = self.ollama_api.get_models()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.chat_tab = self.tabview.add("Chat")
        self.models_tab = self.tabview.add("Models")
        self.modelfile_tab = self.tabview.add("Modelfile")

        self.chat_page = ChatPage(self.chat_tab, self.ollama_api, self.models)
        self.chat_page.pack(expand=True, fill="both")

        self.models_page = ModelsPage(self.models_tab, self.ollama_api, self.update_models)
        self.models_page.pack(expand=True, fill="both")

        self.modelfile_page = ModelfilePage(self.modelfile_tab, self.ollama_api, self.update_models)
        self.modelfile_page.pack(expand=True, fill="both")

        self.tabview.set("Chat")

    def update_models(self):
        self.models = self.ollama_api.get_models()
        self.chat_page.update_models(self.models)
        self.models_page.update_models()
        # Aggiorna anche altre parti dell'applicazione se necessario