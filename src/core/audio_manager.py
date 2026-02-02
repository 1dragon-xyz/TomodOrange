from PySide6.QtCore import QUrl, QObject
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput, QMediaDevices
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
        
        self._setup_connections()

    def _setup_connections(self):
        """Setup signal connections for error handling and device changes."""
        # Listen for media player errors
        self.player.errorOccurred.connect(self._on_player_error)
        
        # Listen for system audio device changes
        self.media_devices = QMediaDevices(self)
        self.media_devices.audioOutputsChanged.connect(self._on_audio_outputs_changed)

    def _on_player_error(self, error, error_string):
        """Handle media player errors."""
        print(f"AudioManager: Player error: {error} - {error_string}")
        # Try to recover if it looks like a resource/device error
        if error == QMediaPlayer.ResourceError:
             self._recover_audio_state()

    def _on_audio_outputs_changed(self):
        """Handle changes in available audio outputs."""
        print("AudioManager: Audio outputs changed. Checking device validity...")
        # If current device is null or invalid, try to reset to default
        if self.audio_output.device().isNull():
             self._recover_audio_state()

    def _recover_audio_state(self):
        """Attempt to recover audio state by resetting to default device."""
        print("AudioManager: Attempting to recover audio state...")
        
        # 1. Reset QAudioOutput to default device
        default_device = QMediaDevices.defaultAudioOutput()
        if not default_device.isNull():
            self.audio_output.setDevice(default_device)
            self.tick_effect.setAudioDevice(default_device)
            print(f"AudioManager: Reset to default device: {default_device.description()}")
            
        # 2. If we were supposed to be playing/looping, ensure we are
        # Validating player state might be tricky if it thinks it's stopped due to error
        # For the break sound (waves), if we are in a state where it SHOULD be playing, restart it.
        # But we don't strictly know if it *should* be playing currently without state from outside.
        # However, if the player has source and is not playing, and we just fixed the device...
        # A safer bet implies we might need the main controller to tell us 'resume'
        # BUT, for now, let's just ensure volume/mute state is re-applied
        
        self.audio_output.setMuted(self.is_muted)


    def toggle_mute(self, is_muted):
        """Toggle mute state."""
        self.is_muted = is_muted
        
        # If we are currently playing the loop and get muted, pause/stop it?
        # OR just rely on logic next time checks happen.
        # Actually, if we are playing break sound and mute is hit, we should silence it immediately.
        # But QSoundEffect/QAudioOutput mute is easiest.
        

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
