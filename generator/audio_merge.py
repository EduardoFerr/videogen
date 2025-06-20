import os
import re
import uuid
import json
import subprocess
from moviepy import AudioFileClip, ImageClip, CompositeAudioClip, concatenate_audioclips
from mutagen.mp3 import MP3
from PIL import Image
from generator.image_overlay import overlay_title_and_watermark
from config import OUTPUT_DIR
from gui.state import AppState


def processar_video(
    audio_concat,
    duration,
    image_path,
    output_filename,
    font_path,
    watermark,
    extra_text,
    rain_audio_path,
    stop_flag,
    log_fn,
    perfil
):
    from moviepy import VideoFileClip

    with open("data/profiles.json", encoding="utf-8") as f:
        perfis = json.load(f)

    conf = perfis[perfil]
    target_size = conf["size"]
    h264_level = conf["level"]
    v_bitrate = conf["v_bitrate"]
    a_bitrate = conf["a_bitrate"]
    crf_value = conf["crf"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_img_path = os.path.join(OUTPUT_DIR, f"temp_img_{uuid.uuid4().hex[:8]}.png")

    if stop_flag and stop_flag.is_set():
        if log_fn: log_fn("🚩 Operação cancelada.")
        return

    if rain_audio_path:
        rain_clip = AudioFileClip(rain_audio_path).with_volume_scaled(0.2)
        loops = int(duration // rain_clip.duration) + 1
        rain_combined = concatenate_audioclips([rain_clip] * loops).subclipped(0, duration)
        audio_concat = audio_concat.subclipped(0, duration)
        audio_concat = CompositeAudioClip([audio_concat, rain_combined])

    ext = os.path.splitext(image_path)[1].lower()

    if ext in [".gif", ".mp4", ".mov", ".webm"]:
        video_clip = VideoFileClip(image_path).resize(target_size)
        if video_clip.duration < duration:
            loops = int(duration // video_clip.duration) + 1
            video_clip = concatenate_audioclips([video_clip] * loops).subclip(0, duration)
        else:
            video_clip = video_clip.subclip(0, duration)
        video_clip.audio = audio_concat
        image_clip = video_clip
    else:
        overlay_title_and_watermark(
            image_path=image_path,
            title="",
            output_path=temp_img_path,
            font_path=font_path,
            watermark=watermark,
            extra_text=extra_text
        )
        Image.open(temp_img_path).convert("RGB").save(temp_img_path)
        image_clip = ImageClip(temp_img_path, duration=duration).resized(target_size)
        image_clip.audio = audio_concat

    intermediate_path = os.path.join(OUTPUT_DIR, f"intermediario_{uuid.uuid4().hex[:8]}.mp4")
    image_clip.write_videofile(
        intermediate_path,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate=a_bitrate,
        bitrate=v_bitrate,
        fps=30,
        preset="ultrafast",
        threads=4,
        ffmpeg_params=["-movflags", "+faststart"],
        logger=None
    )

    safe_name = re.sub(r'[<>:"/\\|?*]', '_', output_filename)
    if not safe_name.endswith(".mp4"):
        safe_name += ".mp4"
    final_path = os.path.join(OUTPUT_DIR, safe_name)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", intermediate_path,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level:v", h264_level,
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", a_bitrate,
        "-movflags", "+faststart"
    ]

    if crf_value:
        ffmpeg_cmd += ["-crf", crf_value]
    else:
        ffmpeg_cmd += [
            "-b:v", v_bitrate,
            "-minrate", v_bitrate,
            "-maxrate", v_bitrate,
            "-bufsize", str(int(v_bitrate.replace("k", "")) * 2) + "k"
        ]

    ffmpeg_cmd.append(final_path)
    subprocess.run(ffmpeg_cmd, check=True)

    os.remove(intermediate_path)
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)

    metadata = {
        "title": AppState.yt_title,
        "description": AppState.yt_description,
        "tags": AppState.yt_tags,
        "privacy": AppState.yt_privacy,
        "thumbnail_path": AppState.yt_thumbnail_path,
        "enviado": False
    }
    json_path = os.path.splitext(final_path)[0] + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    if log_fn:
        log_fn(f"✅ Vídeo gerado ({perfil.upper()}) com qualidade final: {final_path}")

    if image_clip:
        image_clip.close()
    if audio_concat:
        audio_concat.close()


def merge_audio_and_generate_video(
    mp3_paths,
    image_path,
    output_filename,
    font_path,
    watermark="@radiovitrolabr",
    extra_text="Inscreva-se!",
    rain_audio_path=None,
    stop_flag=None,
    log_fn=None,
    perfil="youtube",
    modo="unico"
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        if not mp3_paths:
            raise ValueError("Nenhum arquivo MP3 selecionado.")

        if modo == "unico":
            audio_clips = [AudioFileClip(mp3).with_volume_scaled(0.9) for mp3 in mp3_paths]
            audio_concat = sum(audio_clips[1:], audio_clips[0])
            processar_video(
                audio_concat=audio_concat,
                duration=audio_concat.duration,
                image_path=image_path,
                output_filename=output_filename,
                font_path=font_path,
                watermark=watermark,
                extra_text=extra_text,
                rain_audio_path=rain_audio_path,
                stop_flag=stop_flag,
                log_fn=log_fn,
                perfil=perfil
            )
            for clip in audio_clips:
                clip.close()

        else:  # modo individual
            for i, mp3 in enumerate(mp3_paths):
                if stop_flag and stop_flag.is_set():
                    if log_fn: log_fn("🚩 Operação cancelada.")
                    return
                audio_clip = AudioFileClip(mp3).with_volume_scaled(0.9)
                base_name = os.path.splitext(os.path.basename(mp3))[0]
                output_individual = f"{base_name}.mp4"
                processar_video(
                    audio_concat=audio_clip,
                    duration=audio_clip.duration,
                    image_path=image_path,
                    output_filename=output_individual,
                    font_path=font_path,
                    watermark=watermark,
                    extra_text=extra_text,
                    rain_audio_path=rain_audio_path,
                    stop_flag=stop_flag,
                    log_fn=log_fn,
                    perfil=perfil
                )
                audio_clip.close()

    except subprocess.CalledProcessError as e:
        if log_fn:
            log_fn(f"❌ Erro no FFmpeg: {e}")
        raise
    except Exception as e:
        if log_fn:
            log_fn(f"❌ Erro durante a geração: {e}")
        raise
