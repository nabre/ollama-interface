import customtkinter as ctk
import tkinter.filedialog as filedialog
import threading
from CTkMessagebox import CTkMessagebox

class ModelfilePage(ctk.CTkFrame):
    def __init__(self, parent, ollama_api, update_models_callback):
        super().__init__(parent)
        self.ollama_api = ollama_api
        self.update_models_callback = update_models_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        self.modelfile_text = ctk.CTkTextbox(self, wrap="none")
        self.modelfile_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        load_btn = ctk.CTkButton(button_frame, text="Load Modelfile", command=self.load_modelfile)
        load_btn.pack(side="left", padx=5)

        create_btn = ctk.CTkButton(button_frame, text="Create Model", command=self.create_model)
        create_btn.pack(side="left", padx=5)

    def load_modelfile(self):
        file_path = filedialog.askopenfilename(filetypes=[("Modelfile", "*.modelfile"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.modelfile_text.delete("1.0", ctk.END)
                self.modelfile_text.insert("1.0", content)

    def create_model(self):
        modelfile_content = self.modelfile_text.get("1.0", ctk.END).strip()
        if modelfile_content:
            model_name = ctk.CTkInputDialog(text="Enter name for the new model:", title="Create Model").get_input()
            if model_name:
                progress_window = ctk.CTkToplevel(self)
                progress_window.title("Creating Model")
                progress_window.geometry("300x100")

                progress_label = ctk.CTkLabel(progress_window, text=f"Creating model {model_name}...")
                progress_label.pack(pady=20)

                progress_bar = ctk.CTkProgressBar(progress_window)
                progress_bar.pack(pady=10)
                progress_bar.set(0)

                def create_model_thread():
                    try:
                        self.ollama_api.create_model(model_name, modelfile_content, progress_callback=lambda p: progress_bar.set(p))
                        self.update_models_callback()  # Aggiorna la lista dei modelli in altre parti dell'applicazione
                        CTkMessagebox(title="Success", message=f"Model {model_name} created successfully!", icon="info")
                    except Exception as e:
                        CTkMessagebox(title="Error", message=f"Failed to create model: {str(e)}", icon="error")
                    finally:
                        progress_window.destroy()

                threading.Thread(target=create_model_thread).start()
        else:
            CTkMessagebox(title="Error", message="Modelfile content is empty!", icon="error")