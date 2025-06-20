import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from gui.state import AppState
from uploader import upload_video
from generator.audio_merge import merge_audio_and_generate_video
from generator.image_overlay import overlay_title_and_watermark
from config import FONT_DIR, OUTPUT_DIR

def get_valid_font_path():
    font_path = AppState.font_path
    if isinstance(font_path, str) and os.path.isfile(font_path):
        return font_path

    fallback = os.path.join(FONT_DIR, "Anton-Regular.ttf")
    if os.path.isfile(fallback):
        return fallback

    raise FileNotFoundError(f"Nenhuma fonte válida encontrada.\nTentado: {repr(font_path)} e fallback: {fallback}")

def create_frame(container, controller):
    frame = ttk.Frame(container)

    # Carrega perfis e labels
    with open(os.path.join("data", "profiles.json"), encoding="utf-8") as f:
        perfis = json.load(f)
    label_map = {k: v["label"] for k, v in perfis.items()}

    ttk.Label(frame, text="📦 Finalizar e Publicar").pack(pady=10)
    ttk.Label(frame, text="📄 Verifique os dados antes de gerar o vídeo:").pack(anchor="w", padx=20)
    ttk.Label(frame, text="✔️ Arquivos selecionados, metadados preenchidos e imagem definida.").pack(anchor="w", padx=40, pady=10)

    # PREVIEW
    preview_frame = ttk.LabelFrame(frame, text="📺 Preview do Vídeo")
    preview_frame.pack(fill="x", padx=20, pady=10)

    from PIL import Image, ImageTk
    temp_preview_path = os.path.join(OUTPUT_DIR, "preview_temp.png")
    preview_gerado = False

    try:
        if AppState.image_path and os.path.isfile(AppState.image_path):
            font_path = get_valid_font_path()
            overlay_title_and_watermark(
                image_path=AppState.image_path,
                title=AppState.yt_title or "",
                output_path=temp_preview_path,
                font_path=font_path,
                watermark=AppState.watermark or "",
                extra_text=AppState.extra_text or ""
            )
            preview_gerado = True
    except Exception as e:
        print(f"Erro ao gerar preview: {e}")
        temp_preview_path = None

    if preview_gerado and os.path.exists(temp_preview_path):
        try:
            img = Image.open(temp_preview_path).resize((160, 90))
            img_tk = ImageTk.PhotoImage(img)
            label_img = ttk.Label(preview_frame, image=img_tk)
            label_img.image = img_tk
            label_img.pack(pady=5)
        except Exception as e:
            ttk.Label(preview_frame, text=f"Erro ao carregar imagem: {e}").pack()
    else:
        ttk.Label(preview_frame, text="Imagem de preview não disponível.").pack()

    ttk.Label(preview_frame, text=f"Título: {AppState.yt_title or '—'}").pack(anchor="w")
    ttk.Label(preview_frame, text=f"Áudios selecionados: {len(AppState.selected_mp3s)}").pack(anchor="w")
    ttk.Label(preview_frame, text=f"Imagem de fundo: {os.path.basename(AppState.image_path) if AppState.image_path else '—'}").pack(anchor="w")
    perfil_legivel = label_map.get(AppState.video_perfil, AppState.video_perfil)
    ttk.Label(preview_frame, text=f"Perfil de exportação: {perfil_legivel}").pack(anchor="w")

    # Escolha do modo (único ou individual)
    modo_var = tk.StringVar(value="unico")

    modo_frame = ttk.LabelFrame(frame, text="🎞️ Modo de Geração do Vídeo")
    modo_frame.pack(fill="x", padx=20, pady=10)

    ttk.Radiobutton(modo_frame, text="🔗 Vídeo único com todos os áudios", variable=modo_var, value="unico").pack(anchor="w", padx=10, pady=2)
    ttk.Radiobutton(modo_frame, text="🎬 Um vídeo para cada áudio", variable=modo_var, value="individual").pack(anchor="w", padx=10, pady=2)

    # STATUS
    status_var = tk.StringVar(value="⏳ Aguardando...")
    status_label = ttk.Label(frame, textvariable=status_var, foreground="gray")
    status_label.pack(pady=(5, 10))

    def gerar_video():
        def run():
            status_var.set("⏳ Gerando vídeo...")
            try:
                font_path = get_valid_font_path()
                hashtags = " ".join(AppState.hashtags)
                descricao = AppState.yt_description + "\n" + hashtags

                if AppState.video_perfil not in perfis:
                    raise ValueError(f"Perfil inválido: {AppState.video_perfil}")

                merge_audio_and_generate_video(
                    mp3_paths=AppState.selected_mp3s,
                    image_path=AppState.image_path,
                    output_filename=AppState.output_filename,
                    font_path=font_path,
                    watermark=AppState.watermark,
                    extra_text=AppState.extra_text,
                    rain_audio_path=AppState.rain_path,
                    stop_flag=None,
                    log_fn=lambda msg: print("▶", msg),
                    perfil=AppState.video_perfil,
                    modo=modo_var.get()
                )

                metadata = {
                    "title": AppState.yt_title,
                    "description": AppState.yt_description,
                    "tags": AppState.yt_tags,
                    "privacy": AppState.yt_privacy,
                    "thumbnail_path": AppState.yt_thumbnail_path,
                    "enviado": False
                }
                json_path = os.path.join(OUTPUT_DIR, os.path.splitext(AppState.output_filename)[0] + ".json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                status_var.set("✅ Vídeo e metadados gerados com sucesso!")
                messagebox.showinfo("🎬", "Vídeo e metadados gerados com sucesso!")
            except Exception as e:
                status_var.set("❌ Erro ao gerar vídeo.")
                messagebox.showerror("Erro", f"Erro ao gerar vídeo:\n{e}")

        threading.Thread(target=run).start()

    def publicar_youtube():
        def run():
            status_var.set("⏳ Publicando no YouTube...")
            try:
                video_path = os.path.join(OUTPUT_DIR, AppState.output_filename)
                hashtags = " ".join(AppState.hashtags)
                descricao = AppState.yt_description + "\n" + hashtags

                upload_video(
                    file_path=video_path,
                    title=AppState.yt_title,
                    description=descricao,
                    tags=AppState.yt_tags,
                    privacy=AppState.yt_privacy,
                    thumbnail_path=AppState.yt_thumbnail_path
                )

                json_path = os.path.join(OUTPUT_DIR, os.path.splitext(AppState.output_filename)[0] + ".json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    metadata["enviado"] = True
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)

                status_var.set("✅ Vídeo publicado com sucesso!")
                messagebox.showinfo("🚀", "Vídeo enviado para o YouTube com sucesso!")
            except Exception as e:
                status_var.set("❌ Erro ao publicar vídeo.")
                messagebox.showerror("Erro", f"Erro ao publicar vídeo:\n{e}")

        threading.Thread(target=run).start()

    # Botões
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=30)

    ttk.Button(btn_frame, text="◀ Voltar", command=controller.previous_step).pack(side="left", padx=20)
    ttk.Button(btn_frame, text="🎬 Somente Gerar Vídeo", command=gerar_video).pack(side="left", padx=20)
    ttk.Button(btn_frame, text="🚀 Gerar e Publicar no YouTube", command=publicar_youtube).pack(side="left", padx=20)

    return frame
