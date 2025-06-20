from PIL import Image, ImageDraw, ImageFont
from config import IMAGE_EXTENSIONS
import os

def find_background_image(folder):
    for ext in IMAGE_EXTENSIONS:
        candidate = os.path.join(folder, f"background{ext}")
        if os.path.exists(candidate):
            return candidate
    return None

def overlay_title_and_watermark(image_path, title, output_path, font_path, watermark, extra_text=""):
    TARGET_SIZE = (1920, 1080)

    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Fonte não encontrada: {font_path}")

    img = Image.open(image_path).convert("RGBA").resize(TARGET_SIZE)

    # Escurece o fundo para legibilidade
    dark_overlay = Image.new("RGBA", img.size, (0, 0, 0, 100))
    img = Image.alpha_composite(img, dark_overlay)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = ImageFont.truetype(font_path, 100)
    watermark_font = ImageFont.truetype(font_path, 50)
    extra_font = ImageFont.truetype(font_path, 60)

    # Desenha título centralizado com quebra de linha
    if title:
        max_width = 1400
        words = title.split()
        lines, current_line = [], ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_height = title_font.size + 10
        total_height = len(lines) * line_height
        y_start = (img.height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=title_font)
            x = (img.width - (bbox[2] - bbox[0])) // 2
            y = y_start + i * line_height
            draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 160))
            draw.text((x, y), line, font=title_font, fill=(255, 255, 255, 255))

    # Texto extra (geralmente CTA)
    if extra_text:
        bbox = draw.textbbox((0, 0), extra_text, font=extra_font)
        x = (img.width - (bbox[2] - bbox[0])) // 2
        y = img.height - bbox[3] - 50
        draw.text((x + 2, y + 2), extra_text, font=extra_font, fill=(0, 0, 0, 180))
        draw.text((x, y), extra_text, font=extra_font, fill=(255, 255, 255, 255))

    # Marca d'água (inferior direito)
    if watermark:
        bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
        x = img.width - bbox[2] - 40
        y = img.height - bbox[3] - 20
        draw.text((x + 2, y + 2), watermark, font=watermark_font, fill=(0, 0, 0, 180))
        draw.text((x, y), watermark, font=watermark_font, fill=(200, 200, 200, 180))

    final = Image.alpha_composite(img, overlay)
    final.convert("RGB").save(output_path)
