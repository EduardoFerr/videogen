from gui.steps import step_select, step_metadata, step_finalize
import tkinter as tk
from tkinter import ttk

class CreateWizard:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)

        # Etapas como barra de progresso superior
        self.progress_label = ttk.Label(self.frame, text="Etapa 1 de 3: Seleção", font=("Segoe UI", 10, "italic"))
        self.progress_label.pack(pady=(10, 0))

        self.container = ttk.Frame(self.frame)
        self.container.pack(fill="both", expand=True)

        self.steps = ["select", "metadata", "finalize"]
        self.frames = {
            "select": step_select.create_frame(self.container, self),
            "metadata": step_metadata.create_frame(self.container, self),
            "finalize": step_finalize.create_frame(self.container, self),
        }
        self.current = 0
        self.show(self.steps[self.current])

    def show(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        self.progress_label.config(text=f"Etapa {self.current+1} de {len(self.steps)}: {name.capitalize()}")

    def next_step(self):
        if self.current < len(self.steps) - 1:
            self.current += 1
            self.show(self.steps[self.current])

    def previous_step(self):
        if self.current > 0:
            self.current -= 1
            self.show(self.steps[self.current])

    def get_frame(self):
        return self.frame

def create_frame(container, controller=None):
    return CreateWizard(container).get_frame()
