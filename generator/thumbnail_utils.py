import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image
from auth import autenticar_youtube
from tempfile import NamedTemporaryFile

def otimizar_thumbnail(input_path, max_size_bytes=2_000_000):
    """
    Reduz o tamanho da imagem de thumbnail para ficar abaixo de 2MB.
    Retorna o caminho para um arquivo JPEG temporário.
    """
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.thumbnail((1280, 720), Image.LANCZOS)

        temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
        quality = 90

        while True:
            img.save(temp_file.name, format="JPEG", optimize=True, quality=quality)
            if os.path.getsize(temp_file.name) <= max_size_bytes or quality <= 40:
                break
            quality -= 5

    return temp_file.name

