import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.state import AppState
import webbrowser
import threading
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build
from auth import autenticar_youtube
from config import CREDENTIALS_PATH, TOKEN_PATH, FONT_DIR

def verificar_status_api_async(status_label):
    def run():
        try:
            status_label.config(text="⏳ Verificando...", foreground="gray")
            creds = autenticar_youtube()
            service = build("youtube", "v3", credentials=creds)
            response = service.channels().list(part="snippet", mine=True).execute()
            channel_title = response['items'][0]['snippet']['title']
            status_label.config(text=f"✅ Autenticado como: {channel_title}", foreground="green")
            messagebox.showinfo("✅ API Conectada", f"Autenticado como: {channel_title}")
        except FileNotFoundError:
            status_label.config(text="❌ Credenciais não encontradas", foreground="red")
            messagebox.showerror("Erro", "Arquivo de credenciais não encontrado.")
        except DefaultCredentialsError:
            status_label.config(text="❌ Credenciais inválidas", foreground="red")
            messagebox.showerror("Erro", "Credenciais inválidas ou expiradas.")
        except Exception as e:
            status_label.config(text="❌ Erro na API", foreground="red")
            messagebox.showerror("Erro ao verificar API", str(e))
    threading.Thread(target=run, daemon=True).start()

def create_frame(container, controller=None):
    frame = ttk.Frame(container)

    ttk.Label(frame, text="🔧 Configurações Gerais", font=("Segoe UI", 12, "bold")).pack(pady=10)

    cred_label = ttk.Label(frame, text="Arquivo atual: nenhum")
    if os.path.exists(CREDENTIALS_PATH):
        cred_label.config(text=f"Arquivo atual: {os.path.basename(CREDENTIALS_PATH)}")

    def selecionar_credencial():
        caminho = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if caminho:
            with open(caminho, "rb") as src, open(CREDENTIALS_PATH, "wb") as dst:
                dst.write(src.read())
            cred_label.config(text=f"Arquivo atual: {os.path.basename(caminho)}")
            messagebox.showinfo("OK", "Credenciais atualizadas com sucesso!")

    ttk.Button(frame, text="Selecionar client_secrets.json", command=selecionar_credencial).pack(pady=5)
    cred_label.pack(pady=5)

    status_label = ttk.Label(frame, text="")
    ttk.Button(frame, text="🔍 Verificar status da API", command=lambda: verificar_status_api_async(status_label)).pack(pady=(0, 5))
    status_label.pack(pady=(0, 20))

    ttk.Label(
        frame,
        text="🔐 Como obter o arquivo 'client_secrets.json' para publicação no YouTube:",
        font=("Segoe UI", 11, "bold")
    ).pack(pady=(20, 5), anchor="w", padx=20)

    instrucoes = (
        "1. Acesse o Console do Google Cloud: https://console.cloud.google.com\n"
        "2. Crie um novo projeto (ou selecione um existente)\n"
        "3. Vá em 'APIs e serviços' > 'Credenciais'\n"
        "4. Clique em 'Criar credencial' > 'ID do cliente OAuth'\n"
        "5. Selecione o tipo de aplicação como 'Área de trabalho'\n"
        "6. Faça o download do arquivo JSON gerado\n"
        "7. Importe esse arquivo na aba 'Configurações' do aplicativo"
    )
    ttk.Label(frame, text=instrucoes, wraplength=720, justify="left", font=("Segoe UI", 10)).pack(padx=20, pady=5)

    def abrir_console():
        webbrowser.open("https://console.cloud.google.com")

    ttk.Button(frame, text="🌐 Abrir Console do Google Cloud", command=abrir_console).pack(pady=(5, 20))

    ttk.Label(frame, text="Fonte padrão (opcional):").pack(pady=(15, 0))
    fontes = [f for f in os.listdir(FONT_DIR) if f.endswith(".ttf")]
    font_var = tk.StringVar(value=os.path.basename(AppState.font_path) if AppState.font_path else (fontes[0] if fontes else ""))

    combo = ttk.Combobox(frame, values=fontes, textvariable=font_var, state="readonly", width=48)
    combo.pack(pady=2)

    def salvar_font_auto(event=None):
        AppState.font_path = os.path.join(FONT_DIR, font_var.get())

    combo.bind("<<ComboboxSelected>>", salvar_font_auto)
    salvar_font_auto()

    ttk.Label(frame, text="Marca d'água:").pack(pady=(15, 0))
    watermark_entry = ttk.Entry(frame, width=50)
    watermark_entry.insert(0, AppState.watermark)
    watermark_entry.pack()

    ttk.Label(frame, text="Texto adicional:").pack(pady=(15, 0))
    extra_entry = ttk.Entry(frame, width=50)
    extra_entry.insert(0, AppState.extra_text)
    extra_entry.pack()

    def salvar_textos_auto(event=None):
        AppState.watermark = watermark_entry.get()
        AppState.extra_text = extra_entry.get()

    watermark_entry.bind("<FocusOut>", salvar_textos_auto)
    extra_entry.bind("<FocusOut>", salvar_textos_auto)

    return frame
