import pygame
from pathlib import Path
from typing import Optional, List

from .audio_converter import convert_mp4_to_mp3


class MusicManager:
    """Manages background music playback and volume control."""
    
    def __init__(self):
        self.current_music_path: Optional[str] = None
        self.current_music_channel: Optional[pygame.mixer.Channel] = None
        self.music_volume: float = 0.6
        self.music_paused: bool = False

    def _get_default_music_path(self) -> Optional[str]:
        """Get the default music file path from the game assets."""
        base_path = Path(__file__).parent.parent.parent
        possible_paths = [
            base_path / "Jugabilidad" / "Base" / "assets" / "sounds" / "musica_fondo.mp3",
            base_path / "Jugabilidad" / "Base" / "assets" / "sounds" / "musica_fondo.ogg",
            base_path / "Jugabilidad" / "Base" / "assets" / "sounds" / "musica_fondo.wav",
            base_path / "Jugabilidad" / "Base" / "assets" / "sounds" / "musica_fondo.mp4",
        ]
        for path in possible_paths:
            if path.exists():
                print(f"[Música] Encontrado: {path.name}")
                if str(path).lower().endswith('.mp4'):
                    converted = convert_mp4_to_mp3(str(path))
                    if converted:
                        return converted
                return str(path)
        return None

    def play_background_music(self, favorite_music: Optional[List[str]] = None) -> None:
        """Play background music from favorite list or default."""
        music_path = None
        
        if favorite_music and len(favorite_music) > 0:
            for music_file in favorite_music:
                if isinstance(music_file, str) and Path(music_file).exists():
                    music_path = music_file
                    break
        
        if not music_path:
            music_path = self._get_default_music_path()
        
        if not music_path:
            print("[Música] No se encontró archivo de música")
            return
        
        try:
            self.current_music_path = music_path
            
            channel = pygame.mixer.find_channel()
            if channel:
                sound = pygame.mixer.Sound(music_path)
                sound.set_volume(self.music_volume)
                channel.play(sound, loops=-1)
                self.current_music_channel = channel
                print(f"[Música] Reproduciendo: {Path(music_path).name}")
            else:
                print("[Música] No hay canales disponibles")
        except Exception as e:
            print(f"[Música] Error al reproducir: {e}")

    def stop_background_music(self) -> None:
        """Stop background music."""
        if self.current_music_channel:
            self.current_music_channel.stop()
            self.current_music_channel = None
        self.music_paused = False

    def pause_background_music(self) -> None:
        """Pause background music."""
        if self.current_music_channel and not self.music_paused:
            self.current_music_channel.pause()
            self.music_paused = True

    def resume_background_music(self) -> None:
        """Resume background music."""
        if self.current_music_channel and self.music_paused:
            self.current_music_channel.unpause()
            self.music_paused = False

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music_channel:
            self.current_music_channel.set_volume(self.music_volume)
