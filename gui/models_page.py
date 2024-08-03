import customtkinter as ctk
import threading
from CTkMessagebox import CTkMessagebox

class ModelsPage(ctk.CTkFrame):
    def __init__(self, parent, ollama_api, update_models_callback):
        super().__init__(parent)
        self.ollama_api = ollama_api
        self.update_models_callback = update_models_callback
        self.models = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        self.models_frame = ctk.CTkScrollableFrame(self)
        self.models_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        download_btn = ctk.CTkButton(button_frame, text="Download Model", command=self.download_model)
        download_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(button_frame, text="Delete Model", command=self.delete_model)
        delete_btn.pack(side="left", padx=5)

        # Aggiungi il nuovo pulsante "Aggiorna"
        refresh_btn = ctk.CTkButton(button_frame, text="Aggiorna", command=self.refresh_models)
        refresh_btn.pack(side="left", padx=5)

        self.update_models()

    def refresh_models(self):
        # Mostra un messaggio di caricamento
        loading_label = ctk.CTkLabel(self, text="Aggiornamento in corso...")
        loading_label.grid(row=2, column=0, pady=10)
        self.update()  # Forza l'aggiornamento dell'interfaccia

        def refresh_thread():
            try:
                self.update_models()
                self.update_models_callback()
                CTkMessagebox(title="Success", message="Lista dei modelli aggiornata con successo!", icon="info")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Errore durante l'aggiornamento: {str(e)}", icon="error")
            finally:
                loading_label.destroy()

        threading.Thread(target=refresh_thread).start()

    def update_models(self):
        models = self.ollama_api.get_models()
        
        for widget in self.models_frame.winfo_children():
            widget.destroy()
        
        self.models = []
        for model in models:
            btn = ctk.CTkButton(self.models_frame, text=model, command=lambda m=model: self.select_model(m))
            btn.pack(fill="x", pady=2)
            self.models.append({"name": model, "button": btn})

    def select_model(self, model_name):
        for model in self.models:
            model["button"].configure(fg_color=("gray75", "gray25") if model["name"] == model_name else ("gray70", "gray30"))

    def download_model(self):
        model_name = ctk.CTkInputDialog(text="Enter model name to download:", title="Download Model").get_input()
        if model_name:
            progress_window = ctk.CTkToplevel(self)
            progress_window.title("Downloading Model")
            progress_window.geometry("300x100")

            progress_label = ctk.CTkLabel(progress_window, text=f"Downloading {model_name}...")
            progress_label.pack(pady=20)

            progress_bar = ctk.CTkProgressBar(progress_window)
            progress_bar.pack(pady=10)
            progress_bar.set(0)

            def download_thread():
                try:
                    self.ollama_api.download_model(model_name, progress_callback=lambda p: progress_bar.set(p))
                    self.update_models()  # Aggiorna la lista dei modelli
                    self.update_models_callback()  # Aggiorna altre parti dell'applicazione
                    CTkMessagebox(title="Success", message=f"Model {model_name} downloaded successfully!", icon="info")
                except Exception as e:
                    CTkMessagebox(title="Error", message=f"Failed to download model: {str(e)}", icon="error")
                finally:
                    progress_window.destroy()

            threading.Thread(target=download_thread).start()

    def delete_model(self):
        selected_model = next((model for model in self.models if model["button"].cget("fg_color") == ("gray75", "gray25")), None)
        if selected_model:
            model_name = selected_model["name"]
            confirm = CTkMessagebox(title="Delete Model", 
                                    message=f"Are you sure you want to delete {model_name}?", 
                                    icon="warning", 
                                    option_1="Yes", 
                                    option_2="No")
            if confirm.get() == "Yes":
                try:
                    self.ollama_api.delete_model(model_name)
                    self.update_models()
                    self.update_models_callback()
                    CTkMessagebox(title="Success", message=f"Model {model_name} deleted successfully!", icon="info")
                except Exception as e:
                    CTkMessagebox(title="Error", message=f"Failed to delete model: {str(e)}", icon="error")
        else:
            CTkMessagebox(title="Error", message="Please select a model to delete.", icon="error")