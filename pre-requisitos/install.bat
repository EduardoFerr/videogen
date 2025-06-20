@echo off
setlocal

echo 🔽 Baixando FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '%TEMP%\ffmpeg.zip'"

echo 📦 Extraindo para C:\ffmpeg...
powershell -Command "Expand-Archive -Path '%TEMP%\ffmpeg.zip' -DestinationPath 'C:\ffmpeg_temp' -Force"

:: Renomeia a pasta extraída para padronizar
for /d %%i in (C:\ffmpeg_temp\*) do (
    move "%%i" "C:\ffmpeg"
    goto :renamed
)
:renamed
rd /s /q C:\ffmpeg_temp

echo 🛠️ Adicionando ao PATH...
setx PATH "%PATH%;C:\ffmpeg\bin"

echo ✅ FFmpeg instalado em C:\ffmpeg e adicionado ao PATH do usuário.
echo 🔁 Feche e reabra o terminal antes de usar.
pause
