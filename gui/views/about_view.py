import tkinter as tk
from tkinter import ttk
import webbrowser

def create_frame(container, controller=None):
    frame = ttk.Frame(container)

    ttk.Label(frame, text="ℹ️ Sobre o Projeto", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))

    descricao = (
        "Este aplicativo foi desenvolvido para simplificar a criação e publicação de vídeos musicais no YouTube, "
        "com foco em automação, praticidade e organização."
    )
    ttk.Label(frame, text=descricao, wraplength=720, justify="left", font=("Segoe UI", 11)).pack(padx=20, pady=10)

    recursos = (
        "💡 Funcionalidades principais:\n"
        "• Criação de vídeos a partir de múltiplos MP3s com imagem de fundo\n"
        "• Inserção automática de marca d'água e texto adicional\n"
        "• Salvamento e carregamento automático de configurações\n"
        "• Exportação de metadados no formato JSON\n"
        "• Visualização e edição de metadados antes da publicação\n"
        "• Upload automatizado com título, descrição, tags, thumbnail e privacidade\n"
        "• Marcação de vídeos publicados com status 'enviado'\n"
    )
    ttk.Label(frame, text=recursos, wraplength=720, justify="left", font=("Segoe UI", 10)).pack(padx=20, pady=5)

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

    ttk.Button(frame, text="🌐 Abrir Console do Google Cloud", command=abrir_console).pack(pady=(5, 15))

    ttk.Label(
        frame,
        text="Versão 1.0.0  |  Criado por Du Moraes",
        font=("Segoe UI", 10, "italic"),
        foreground="gray"
    ).pack(pady=5)

    return frame
