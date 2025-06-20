import os
import json
import tkinter as tk
from tkinter import ttk, filedialog
from gui.state import AppState

hashtag_grupos = {}
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
json_path = os.path.join(ROOT_DIR, "data", "hashtags.json")
keywords_path = os.path.join(ROOT_DIR, "data", "keywords.json")
profiles_path = os.path.join(ROOT_DIR, "data", "profiles.json")

with open(json_path, "r", encoding="utf-8") as f:
    hashtag_grupos = json.load(f)

with open(keywords_path, "r", encoding="utf-8") as f:
    keyword_map = json.load(f)

with open(profiles_path, "r", encoding="utf-8") as f:
    perfis = json.load(f)

hashtag_vars = {}

def inferir_keywords():
    sugestoes = set()
    if AppState.selected_mp3s:
        nomes = " ".join(os.path.basename(p).lower() for p in AppState.selected_mp3s)
        for keyword, tags in keyword_map.items():
            if keyword in nomes:
                sugestoes.update(tags)
    return sugestoes

def create_frame(container, controller):
    frame = ttk.Frame(container)

    ttk.Label(frame, text="📝 Preencha os Metadados do Vídeo", font=("Segoe UI", 12, "bold")).pack(pady=10)

    sugestoes = inferir_keywords()
    if not AppState.yt_title:
        AppState.yt_title = "Lofi Beat para Relaxar e Estudar"
    if not AppState.yt_description:
        AppState.yt_description = (
            "🎧 Curta este beat lofi perfeito para estudar, relaxar ou focar.\n"
            "📚 Música instrumental suave com toque nostálgico, ideal para manter a concentração.\n"
            "🌙 Novos beats toda semana! Inscreva-se no canal.\n\n"
            "🔗 https://youtube.com/@radiovitrolabr\n"
            "🎛️ Gerado automaticamente com inteligência artificial.\n"
            "\n#lofimusic #studybeats #relaxing"
        )
    if not AppState.yt_tags:
        base_tags = ["lofi", "study", "focus", "relax", "instrumental", "lofi beats", "study music"]
        AppState.yt_tags = list(set(base_tags + list(sugestoes)))
    if not AppState.yt_privacy:
        AppState.yt_privacy = "public"

    title_var = tk.StringVar(value=AppState.yt_title)
    tags_var = tk.StringVar(value=", ".join(AppState.yt_tags))
    privacy_var = tk.StringVar(value=AppState.yt_privacy)
    thumb_var = tk.StringVar(value=AppState.yt_thumbnail_path)

    label_map = {k: v["label"] for k, v in perfis.items()}
    reverse_map = {v: k for k, v in label_map.items()}
    current_label = label_map.get(AppState.video_perfil, list(label_map.values())[0])
    perfil_var = tk.StringVar(value=current_label)

    ttk.Label(frame, text="🎬 Título:").pack(anchor="w", padx=10)
    ttk.Entry(frame, textvariable=title_var, width=70).pack(padx=10)

    ttk.Label(frame, text="📝 Descrição:").pack(anchor="w", padx=10, pady=(10, 0))
    desc_box = tk.Text(frame, height=5, width=68)
    desc_box.insert("1.0", AppState.yt_description)
    desc_box.pack(padx=10)

    ttk.Label(frame, text="📌 Hashtags sugeridas:").pack(anchor="w", padx=10, pady=(10, 0))
    scroll_wrapper = ttk.Frame(frame)
    scroll_wrapper.pack(padx=10, pady=(0, 5), fill="x")

    scroll_canvas = tk.Canvas(scroll_wrapper, height=200)
    scrollbar = ttk.Scrollbar(scroll_wrapper, orient="vertical", command=scroll_canvas.yview)
    scroll_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    scroll_canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = ttk.Frame(scroll_canvas)
    scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    scroll_frame.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))

    for grupo, tags in hashtag_grupos.items():
        group_frame = ttk.LabelFrame(scroll_frame, text=grupo)
        group_frame.pack(fill="x", padx=5, pady=5)
        for tag in tags:
            var = tk.BooleanVar(value=(tag in AppState.hashtags))
            hashtag_vars[tag] = var
            ttk.Checkbutton(group_frame, text=tag, variable=var).pack(anchor="w", padx=5)

    btn_tags = ttk.Frame(frame)
    btn_tags.pack(pady=4)
    ttk.Button(btn_tags, text="Selecionar todas", command=lambda: [v.set(True) for v in hashtag_vars.values()]).pack(side="left", padx=5)
    ttk.Button(btn_tags, text="Limpar todas", command=lambda: [v.set(False) for v in hashtag_vars.values()]).pack(side="left", padx=5)

    ttk.Label(frame, text="🏷️ Tags (vírgulas):").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Entry(frame, textvariable=tags_var, width=70).pack(padx=10)

    ttk.Label(frame, text="🔐 Privacidade:").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Combobox(frame, textvariable=privacy_var, values=["public", "unlisted", "private"], width=67).pack(padx=10)

    ttk.Label(frame, text="🖼️ Perfil de Exportação:").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Combobox(
        frame,
        textvariable=perfil_var,
        values=list(label_map.values()),
        width=67,
        state="readonly"
    ).pack(padx=10)

    def selecionar_thumbnail():
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png")])
        if caminho:
            thumb_var.set(caminho)

    ttk.Button(frame, text="Selecionar Thumbnail", command=selecionar_thumbnail).pack(pady=5)
    ttk.Label(frame, textvariable=thumb_var, wraplength=680, foreground="gray").pack(padx=10)

    def salvar_dados():
        AppState.yt_title = title_var.get()
        AppState.yt_description = desc_box.get("1.0", "end").strip()
        AppState.yt_tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]
        AppState.yt_privacy = privacy_var.get()
        AppState.yt_thumbnail_path = thumb_var.get()
        AppState.hashtags = {tag for tag, var in hashtag_vars.items() if var.get()}
        AppState.video_perfil = reverse_map.get(perfil_var.get(), "youtube")

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=20)
    ttk.Button(btn_frame, text="◀ Voltar", command=controller.previous_step).pack(side="left", padx=20)
    ttk.Button(btn_frame, text="Próximo ▶", command=lambda: [salvar_dados(), controller.next_step()]).pack(side="right", padx=20)

    return frame
