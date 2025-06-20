import os
from mutagen.mp4 import MP4

def estimate_bitrate(file_path):
    video = MP4(file_path)
    duration = video.info.length  # em segundos
    file_size_bytes = os.path.getsize(file_path)
    bitrate_kbps = (file_size_bytes * 8) / 1000 / duration  # kbps
    return round(bitrate_kbps)

# Uso
file = "./videos/video_final.mp4"
bitrate = estimate_bitrate(file)

print(f"📦 Bitrate estimado: {bitrate} kbps")
if bitrate < 3072:
    print("⚠️ Abaixo do recomendado para 1080p (mínimo: 3072 kbps)")
elif bitrate > 6144:
    print("⚠️ Acima do recomendado para 1080p (máximo: 6144 kbps)")
else:
    print("✅ Bitrate dentro do intervalo ideal")
