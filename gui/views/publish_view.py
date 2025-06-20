import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.state import AppState
from uploader import upload_video
from config import OUTPUT_DIR

def create_frame(container, controller=None):
    frame = ttk.Frame(container)

    ttk.Label(frame, text="🚀 Publicar Vídeo Manualmente", font=("Segoe UI", 12, "bold")).pack(pady=10)

    selected_video = tk.StringVar()
    video_combo = ttk.Combobox(frame, textvariable=selected_video, state="readonly", width=70)
    video_combo.pack(padx=10, pady=5)

    def atualizar_lista_videos():
        video_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".mp4")]
        video_combo["values"] = video_files
        if video_files:
            selected_video.set(video_files[0])
            carregar_metadados()

    # Metadados
    metadata_frame = ttk.LabelFrame(frame, text="📄 Metadados")
    metadata_frame.pack(fill="x", padx=10, pady=10)

    title_var = tk.StringVar()
    desc_box = tk.Text(metadata_frame, height=4, width=80)
    tags_var = tk.StringVar()
    privacy_var = tk.StringVar()
    thumb_var = tk.StringVar()
    enviado_label = ttk.Label(metadata_frame, text="")

    def carregar_metadados(event=None):
        nome_video = selected_video.get()
        json_path = os.path.join(OUTPUT_DIR, os.path.splitext(nome_video)[0] + ".json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            title_var.set(data.get("title", ""))
            desc_box.delete("1.0", tk.END)
            desc_box.insert("1.0", data.get("description", ""))
            tags_var.set(", ".join(data.get("tags", [])))
            privacy_var.set(data.get("privacy", "public"))
            thumb_var.set(data.get("thumbnail_path", ""))
            enviado_label.config(text=f"Status: {'✅ Enviado' if data.get('enviado') else '⏳ Pendente'}")
        else:
            title_var.set("")
            desc_box.delete("1.0", tk.END)
            tags_var.set("")
            privacy_var.set("public")
            thumb_var.set("")
            enviado_label.config(text="Status: ❌ Nenhum metadado encontrado")

    video_combo.bind("<<ComboboxSelected>>", carregar_metadados)

    ttk.Label(metadata_frame, text="Título:").pack(anchor="w")
    ttk.Entry(metadata_frame, textvariable=title_var, width=80).pack()

    ttk.Label(metadata_frame, text="Descrição:").pack(anchor="w")
    desc_box.pack()

    ttk.Label(metadata_frame, text="Tags (separadas por vírgula):").pack(anchor="w")
    ttk.Entry(metadata_frame, textvariable=tags_var, width=80).pack()

    ttk.Label(metadata_frame, text="Privacidade:").pack(anchor="w")
    ttk.Combobox(metadata_frame, textvariable=privacy_var, values=["public", "unlisted", "private"], width=78).pack()

    def selecionar_thumbnail():
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png")])
        if caminho:
            thumb_var.set(caminho)

    thumb_frame = ttk.Frame(metadata_frame)
    thumb_frame.pack(fill="x", pady=(5, 0))
    ttk.Button(thumb_frame, text="Selecionar Thumbnail", command=selecionar_thumbnail).pack(side="left", padx=(0, 10))
    ttk.Entry(thumb_frame, textvariable=thumb_var, width=65).pack(side="left")

    enviado_label.pack(pady=5)

    def publicar():
        nome_video = selected_video.get()
        if not nome_video:
            messagebox.showwarning("Atenção", "Selecione um vídeo.")
            return

        video_path = os.path.join(OUTPUT_DIR, nome_video)
        if not os.path.exists(video_path):
            messagebox.showerror("Erro", "Arquivo de vídeo não encontrado.")
            return

        descricao = desc_box.get("1.0", tk.END).strip()
        tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]

        try:
            upload_video(
                file_path=video_path,
                title=title_var.get(),
                description=descricao,
                tags=tags,
                privacy=privacy_var.get(),
                thumbnail_path=thumb_var.get()
            )
        except Exception as e:
            messagebox.showerror("Erro ao publicar", str(e))
            return

        json_path = os.path.join(OUTPUT_DIR, os.path.splitext(nome_video)[0] + ".json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.update({
                "title": title_var.get(),
                "description": descricao,
                "tags": tags,
                "privacy": privacy_var.get(),
                "thumbnail_path": thumb_var.get(),
                "enviado": True
            })
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Publicado", "Vídeo enviado com sucesso para o YouTube!")
        carregar_metadados()

    ttk.Button(frame, text="📤 Publicar", command=publicar).pack(pady=10)

    # Exposto para interface.py chamar dinamicamente
    frame.atualizar_lista = atualizar_lista_videos
    return frame
