import os
import tkinter as tk
from tkinter import ttk, filedialog
from gui.state import AppState

def create_frame(container, controller):
    frame = ttk.Frame(container)

    ttk.Label(frame, text="🎵 Selecione os arquivos de áudio e imagem", font=("Segoe UI", 12, "bold")).pack(pady=10)

    # Seleção de MP3
    def select_mp3():
        files = filedialog.askopenfilenames(filetypes=[("MP3", "*.mp3")])
        if files:
            AppState.selected_mp3s = list(files)
            mp3_label.config(text=f"{len(files)} MP3s selecionados")
        else:
            mp3_label.config(text="Nenhum MP3 selecionado")

    ttk.Button(frame, text="🎵 Selecionar MP3s", command=select_mp3).pack()
    mp3_label = ttk.Label(frame, text="Nenhum MP3 selecionado", wraplength=600)
    mp3_label.pack(pady=5)

    # Seleção da imagem de fundo
    def select_image():
        file = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png")])
        if file:
            AppState.image_path = file
            img_label.config(text=os.path.basename(file))
        else:
            img_label.config(text="Nenhuma imagem selecionada")

    ttk.Button(frame, text="🖼 Selecionar Imagem de Fundo", command=select_image).pack(pady=5)
    img_label = ttk.Label(frame, text="Nenhuma imagem selecionada", wraplength=600)
    img_label.pack()

    # Seleção do som de chuva
    def select_rain():
        file = filedialog.askopenfilename(filetypes=[("Áudio", "*.mp3 *.wav")])
        if file:
            AppState.rain_path = file
            rain_label.config(text=os.path.basename(file))
        else:
            rain_label.config(text="Nenhum som selecionado")

    ttk.Button(frame, text="🌧️ Selecionar Som de Fundo (opcional)", command=select_rain).pack(pady=5)
    rain_label = ttk.Label(frame, text="Nenhum som selecionado", wraplength=600)
    rain_label.pack()

    # Nome do arquivo de saída
    ttk.Label(frame, text="📁 Nome do arquivo de saída:").pack(pady=(15, 0))
    filename_var = tk.StringVar(value=AppState.output_filename or "video_final.mp4")

    def update_filename(event=None):
        AppState.output_filename = filename_var.get()

    filename_entry = ttk.Entry(frame, textvariable=filename_var, width=50)
    filename_entry.pack()
    filename_entry.bind("<FocusOut>", update_filename)

    # Navegação
    nav = ttk.Frame(frame)
    nav.pack(pady=20)

    ttk.Button(nav, text="◀ Voltar", command=controller.previous_step, state="disabled").pack(side="left", padx=10)
    ttk.Button(nav, text="Próximo ▶", command=lambda: [update_filename(), controller.next_step()]).pack(side="left", padx=10)

    return frame
