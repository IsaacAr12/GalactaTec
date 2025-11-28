from pathlib import Path
from typing import Optional


def convert_mp4_to_mp3(mp4_path: str) -> Optional[str]:
    """Convert MP4 file to MP3 using ffmpeg."""
    mp3_path = mp4_path.replace('.mp4', '.mp3').replace('.MP4', '.mp3')
    if Path(mp3_path).exists():
        return mp3_path
    
    try:
        import subprocess
        import shutil
        if shutil.which('ffmpeg'):
            result = subprocess.run(
                ['ffmpeg', '-i', mp4_path, '-q:a', '5', '-y', mp3_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0 and Path(mp3_path).exists():
                print(f"✓ Convertido: {Path(mp3_path).name}")
                return mp3_path
    except:
        pass
    
    return None


def convert_mp4_to_ogg(mp4_path: str) -> Optional[str]:
    """Convert MP4 file to OGG using moviepy or ffmpeg."""
    ogg_path = mp4_path.replace('.mp4', '.ogg').replace('.MP4', '.ogg')
    if Path(ogg_path).exists():
        return ogg_path
    
    try:
        from moviepy.editor import VideoFileClip
        print(f"Convirtiendo {mp4_path} a OGG con moviepy...")
        video = VideoFileClip(mp4_path)
        audio = video.audio
        audio.write_audiofile(ogg_path, verbose=False, logger=None)
        video.close()
        print(f"✓ Conversión completada: {ogg_path}")
        return ogg_path
    except Exception as e:
        print(f"moviepy no disponible: {e}")
    
    try:
        import subprocess
        import shutil
        if shutil.which('ffmpeg'):
            print(f"Convirtiendo {mp4_path} a OGG con ffmpeg...")
            result = subprocess.run(
                ['ffmpeg', '-i', mp4_path, '-vn', '-acodec', 'libvorbis', '-q:a', '9', '-y', ogg_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0 and Path(ogg_path).exists():
                print(f"✓ Conversión completada con ffmpeg: {ogg_path}")
                return ogg_path
    except Exception as e:
        print(f"ffmpeg no disponible: {e}")
    
    print(f"⚠ No se pudo convertir {mp4_path}. Instala: pip install moviepy")
    return None
