from PySide6.QtCore import QUrl, QObject
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
import os

class AudioManager(QObject):
    def __init__(self):
        super().__init__()
        
        self.assets_dir = os.path.join(os.getcwd(), "assets", "audio")
        
        # --- Work Internal (Water Drop) ---
        # Using QSoundEffect for low latency, low overhead short sounds
        self.tick_effect = QSoundEffect()
        tick_path = os.path.join(self.assets_dir, "water_drop.wav")
        self.tick_effect.setSource(QUrl.fromLocalFile(tick_path))
        self.tick_effect.setVolume(0.5) # Default
        
        # --- Break Interval (Waves) ---
        # Using QMediaPlayer for longer audio/looping
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        waves_path = os.path.join(self.assets_dir, "waves.mp3")
        self.player.setSource(QUrl.fromLocalFile(waves_path))
        self.audio_output.setVolume(0.5) # Default
        self.player.setLoops(QMediaPlayer.Infinite) # Continuous loop
        
        self.is_muted = False

    def toggle_mute(self, is_muted):
        """Toggle mute state."""
        self.is_muted = is_muted
        
        # If we are currently playing the loop and get muted, pause/stop it?
        # OR just rely on logic next time checks happen.
        # Actually, if we are playing break sound and mute is hit, we should silence it immediately.
        # But QSoundEffect/QAudioOutput mute is easiest.
        
        self.tick_effect.setMuted(is_muted)
        self.audio_output.setMuted(is_muted)

    def play_tick(self):
        """Play the work tick sound once."""
        if self.is_muted:
            return
            
        if self.tick_effect.status() == QSoundEffect.Ready:
            self.tick_effect.play()

    def start_break_sound(self):
        """Start the continuous break sound."""
        # Even if muted, we might 'start' it so it's playing but silent?
        # Or just not play. Let's rely on setMuted() above which handles the output silence.
        if self.player.playbackState() != QMediaPlayer.PlayingState:
            self.player.play()

    def stop_break_sound(self):
        """Stop the break sound."""
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.stop()

    def set_work_volume(self, volume_0_100):
        """Set volume for tick (0-100)."""
        # QSoundEffect volume is 0.0 to 1.0
        self.tick_effect.setVolume(volume_0_100 / 100.0)

    def set_break_volume(self, volume_0_100):
        """Set volume for waves (0-100)."""
        # QAudioOutput setVolume is 0.0 to 1.0
        self.audio_output.setVolume(volume_0_100 / 100.0)
