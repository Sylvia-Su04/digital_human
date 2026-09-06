@echo off
REM ============================================================
REM ComfyUI startup script (TTS / Manhua workflow)
REM Location: D:\digital_human\ComfyUI
REM ============================================================

REM Python env: D drive venv (read-only reuse)
set PYTHON=D:\digital_human\venv\Scripts\python.exe

REM ffmpeg path (bundled with imageio_ffmpeg)
set PATH=D:\digital_human\venv\Lib\site-packages\imageio_ffmpeg\binaries;%PATH%

REM gfpgan / basicsr source path (D drive pylibs, PYTHONPATH)
set PYTHONPATH=D:\digital_human\pylibs\basicsr_src;D:\digital_human\pylibs\gfpgan_src

REM HF mirror fallback (transformers / controlnet_aux auto-download)
set HF_ENDPOINT=https://hf-mirror.com

cd /d "D:\digital_human\ComfyUI"

%PYTHON% main.py --listen 127.0.0.1 --port 8189

pause
