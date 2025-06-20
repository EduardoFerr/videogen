import os
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from auth import autenticar_youtube
from generator.thumbnail_utils import otimizar_thumbnail




def upload_video(
    file_path,
    title,
    description,
    tags=None,
    category_id="10",
    privacy="public",
    thumbnail_path=None
):
    """
    Faz upload de um vídeo para o YouTube com os metadados especificados.
    """
    print("🔐 Autenticando com o YouTube...")
    try:
        credentials = autenticar_youtube()
        youtube = build("youtube", "v3", credentials=credentials)
    except Exception as e:
        print(f"❌ Falha na autenticação: {e}")
        raise

    print("📤 Enviando vídeo para o YouTube...")

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    try:
        media = MediaFileUpload(file_path, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )
        response = request.execute()
        video_id = response.get("id")
        print(f"✅ Vídeo enviado com sucesso! ID: {video_id}")

        # Enviar thumbnail otimizada, se existir
        if thumbnail_path and os.path.exists(thumbnail_path):
            print("🖼️ Otimizando e enviando thumbnail...")
            thumb_otimizada = otimizar_thumbnail(thumbnail_path)
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumb_otimizada)
            ).execute()
            print("✅ Thumbnail enviada com sucesso.")
            os.remove(thumb_otimizada)

        return video_id

    except HttpError as e:
        print(f"❌ Erro na API do YouTube: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        raise
