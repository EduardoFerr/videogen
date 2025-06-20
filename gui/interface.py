import tkinter as tk
from tkinter import ttk
from gui.views import config_view, create_view, publish_view, about_view

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎛️ Gerador e Publicador de Vídeos")
        self.root.geometry("1000x720")

        # Estilo flat moderno
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TButton", padding=8, font=("Segoe UI", 10), background="#f0f0f0")
        style.map("TButton", background=[("active", "#e0e0e0")])
        style.configure("ActiveNav.TButton", background="#d0d0d0", font=("Segoe UI", 10, "bold"))

        # Layout principal
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.container = ttk.Frame(self.root)
        self.container.pack(side="right", fill="both", expand=True)

        # Inicializa views
        self.frames = {
            "Configurações": config_view.create_frame(self.container, controller=self),
            "Criar": create_view.create_frame(self.container, controller=self),
            "Publicar": publish_view.create_frame(self.container, controller=self),
            "Sobre": about_view.create_frame(self.container, controller=self)
        }

        # Botões de navegação
        self.nav_buttons = {}
        for name in self.frames:
            btn = ttk.Button(self.sidebar, text=f"▶ {name}", command=lambda n=name: self.show_frame(n))
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[name] = btn

        self.show_frame("Criar")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.config(style="ActiveNav.TButton")
            else:
                btn.config(style="TButton")

        self.frames[name].pack(fill="both", expand=True)

        # Se a view tiver método de atualização, chama
        if hasattr(self.frames[name], "atualizar_lista"):
            self.frames[name].atualizar_lista()

def run_gui():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
