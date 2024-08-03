import customtkinter as ctk
from utils.markdown_renderer import MarkdownRenderer
import tkinter as tk
from CTkMessagebox import CTkMessagebox
from PIL import Image

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, message, is_user=True, **kwargs):
        user_color = "#007AFF"  # Blu acceso per l'utente
        ai_color = "#E5E5EA"    # Grigio chiaro per l'AI
        user_text_color = "white"
        ai_text_color = "black"

        super().__init__(master, fg_color=(user_color if is_user else ai_color), corner_radius=15, **kwargs)
        
        self.message = ctk.CTkLabel(
            self, 
            text=message, 
            wraplength=350,  # Ridotto per bolle più compatte
            justify="left",
            text_color=user_text_color if is_user else ai_text_color,
            font=("Helvetica", 12)
        )
        self.message.pack(padx=10, pady=5)
        
        
class ChatPage(ctk.CTkFrame):
    def __init__(self, parent, ollama_api, models):
        super().__init__(parent)
        self.ollama_api = ollama_api
        self.models = models
        self.sessions = []
        self.current_session = None
        self.current_model = models[0] if models else "default"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_chat_area()

        if not self.sessions:
            self.add_session()

    def setup_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(sidebar, text="Ollama Chat", font=ctk.CTkFont(size=20, weight="bold"))
        logo.pack(pady=20)

        add_session_btn = ctk.CTkButton(sidebar, text="New Chat", command=self.add_session,
                                        fg_color="#4CAF50", hover_color="#45a049")
        add_session_btn.pack(pady=10, padx=20, fill="x")

        self.session_frame = ctk.CTkScrollableFrame(sidebar)
        self.session_frame.pack(expand=True, fill="both", padx=10, pady=10)

        model_label = ctk.CTkLabel(sidebar, text="Select Model:")
        model_label.pack(pady=(20, 0), padx=20, anchor="w")

        self.model_dropdown = ctk.CTkOptionMenu(sidebar, values=self.models, command=self.change_model,
                                                fg_color="#2196F3", button_color="#1976D2", button_hover_color="#1565C0")
        self.model_dropdown.pack(pady=5, padx=20, fill="x")

    def setup_chat_area(self):
        chat_frame = ctk.CTkFrame(self)
        chat_frame.grid(row=0, column=1, sticky="nsew")
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        self.chat_display = ctk.CTkScrollableFrame(chat_frame)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        input_frame = ctk.CTkFrame(chat_frame)
        input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkTextbox(input_frame, height=50, wrap="word")
        self.input_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_box.bind("<Return>", self.send_message_event)

        send_btn = ctk.CTkButton(input_frame, text="Send", command=self.send_message,
                                 width=100, fg_color="#4CAF50", hover_color="#45a049")
        send_btn.grid(row=0, column=1)

    def add_session(self):
        session_name = f"Chat {len(self.sessions) + 1}"
        session = {"name": session_name, "messages": [], "model": self.current_model}
        self.sessions.append(session)
        self.add_session_frame(session)
        self.select_session(session)
        self.update_delete_buttons()

    def add_session_frame(self, session):
        frame = ctk.CTkFrame(self.session_frame, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 5), padx=5)
        frame.grid_columnconfigure(0, weight=1)

        session_btn = ctk.CTkButton(frame, text=session["name"], 
                                    command=lambda: self.select_session(session),
                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                    hover_color=("gray70", "gray30"),
                                    anchor="w", height=35)
        session_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        icon_size = 10

        rename_btn = ctk.CTkButton(frame, text="✏️", width=icon_size,
                                   command=lambda: self.rename_session(session),
                                   fg_color="transparent", text_color=("gray10", "gray90"), 
                                   hover_color=("gray70", "gray30"),
                                   corner_radius=5)
        rename_btn.grid(row=0, column=1, padx=(0, 0))

        delete_btn = ctk.CTkButton(frame, text="🗑️", width=icon_size,
                                   command=lambda: self.delete_session(session),
                                   fg_color="transparent", text_color=("gray10", "gray90"), 
                                   hover_color=("gray70", "gray30"),
                                   corner_radius=5)
        delete_btn.grid(row=0, column=2, padx=(0, 0))

        session["frame"] = frame
        session["button"] = session_btn
        session["rename_btn"] = rename_btn
        session["delete_btn"] = delete_btn

        self.update_delete_buttons()
        return frame

    def update_delete_buttons(self):
        for session in self.sessions:
            if len(self.sessions) > 1:
                session["delete_btn"].grid()
            else:
                session["delete_btn"].grid_remove()
        
    def add_session_button(self, session):
        btn = ctk.CTkButton(self.session_frame, text=session["name"], 
                            command=lambda: self.select_session(session),
                            fg_color="transparent", text_color=("gray10", "gray90"),
                            hover_color=("gray70", "gray30"), anchor="w")
        btn.pack(fill="x", pady=2)
        session["button"] = btn

    def select_session(self, session):
        self.current_session = session
        for s in self.sessions:
            s["button"].configure(fg_color="transparent")
        session["button"].configure(fg_color=("gray75", "gray25"))
        self.update_chat_display()
        self.model_dropdown.set(session["model"])

    def rename_session(self, session):
        current_name = session["name"]
        dialog = ctk.CTkInputDialog(text="Enter new session name:", title="Rename Session")
        new_name = dialog.get_input()
        if new_name and new_name.strip() and new_name != current_name:
            session["name"] = new_name
            session["button"].configure(text=new_name)
            CTkMessagebox(title="Success", message=f"Session renamed to '{new_name}'", icon="info")
        elif new_name == current_name:
            CTkMessagebox(title="Info", message="Session name unchanged", icon="info")
        else:
            CTkMessagebox(title="Error", message="Invalid session name", icon="error")

    def update_session_list(self):
        for session in self.sessions:
            session["button"].configure(text=session["name"])
            
    def delete_session(self, session):
        if len(self.sessions) > 1:
            confirm = CTkMessagebox(title="Confirm Deletion", 
                                    message=f"Are you sure you want to delete the session '{session['name']}'?",
                                    icon="warning", option_1="Yes", option_2="No")
            if confirm.get() == "Yes":
                self.sessions.remove(session)
                session["frame"].destroy()
                if self.current_session == session:
                    self.select_session(self.sessions[0])
                self.update_delete_buttons()
                CTkMessagebox(title="Success", message="Session deleted", icon="info")
        else:
            CTkMessagebox(title="Error", message="Cannot delete the last session.", icon="error")

    def change_model(self, model):
        if self.current_session:
            self.current_session["model"] = model
            self.current_model = model

    def send_message_event(self, event):
        if event.state == 0:  # No modifiers
            self.send_message()
            return "break"  # Prevents the newline from being added
        return None  # Allows Shift+Enter for newline

    def send_message(self):
        message = self.input_box.get("1.0", ctk.END).strip()
        if message:
            self.current_session["messages"].append({"role": "user", "content": message})
            self.update_chat_display()
            self.input_box.delete("1.0", ctk.END)

            thinking_bubble = ChatBubble(self.chat_display, "AI is thinking...", is_user=False)
            thinking_bubble.pack(padx=10, pady=5, anchor="w")
            self.chat_display.update()

            response = self.ollama_api.chat(message, model=self.current_session["model"])

            thinking_bubble.destroy()
            self.current_session["messages"].append({"role": "assistant", "content": response})
            self.update_chat_display()

    def update_chat_display(self):
        for widget in self.chat_display.winfo_children():
            widget.destroy()
        
        for message in self.current_session["messages"]:
            is_user = message["role"] == "user"
            bubble = ChatBubble(self.chat_display, message["content"], is_user=is_user)
            bubble.pack(padx=10, pady=5, anchor="e" if is_user else "w")

        self.chat_display.update()
        self.chat_display._parent_canvas.yview_moveto(1.0)
        
    def update_models(self, models):
        self.models = models
        self.model_dropdown.configure(values=self.models)
        if self.current_model not in models:
            self.current_model = models[0] if models else "default"
            self.model_dropdown.set(self.current_model)