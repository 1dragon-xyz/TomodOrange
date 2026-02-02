
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PySide6.QtCore import QUrl

from src.core.audio_manager import AudioManager

class TestAudioRecovery(unittest.TestCase):
    def setUp(self):
        # Create instance
        # We need to mock the internal objects because __init__ creates them
        with patch('src.core.audio_manager.QSoundEffect') as mock_se, \
             patch('src.core.audio_manager.QMediaPlayer') as mock_mp, \
             patch('src.core.audio_manager.QAudioOutput') as mock_ao, \
             patch('src.core.audio_manager.QMediaDevices') as mock_md:
            
            self.audio_manager = AudioManager()
            self.mock_player = self.audio_manager.player
            self.mock_audio_output = self.audio_manager.audio_output
            self.mock_media_devices = self.audio_manager.media_devices
            self.mock_tick_effect = self.audio_manager.tick_effect

    def test_on_player_error_triggers_recovery(self):
        """Test that a ResourceError triggers recovery."""
        # Mock the recovery method to verify it gets called
        self.audio_manager._recover_audio_state = MagicMock()
        
        from PySide6.QtMultimedia import QMediaPlayer as RealQMediaPlayer
        resource_error = RealQMediaPlayer.ResourceError
        
        self.audio_manager._on_player_error(resource_error, "Device disconnected")
        
        self.audio_manager._recover_audio_state.assert_called_once()

    def test_on_player_error_ignores_other_errors(self):
        """Test that non-critical errors do not trigger recovery."""
        self.audio_manager._recover_audio_state = MagicMock()
        
        from PySide6.QtMultimedia import QMediaPlayer as RealQMediaPlayer
        format_error = RealQMediaPlayer.FormatError
        
        self.audio_manager._on_player_error(format_error, "Bad format")
        
        self.audio_manager._recover_audio_state.assert_not_called()

    def test_on_audio_outputs_changed_triggers_recovery_if_null(self):
        """Test recovery is triggered if device becomes null."""
        self.audio_manager._recover_audio_state = MagicMock()
        
        # Mock device().isNull() to return True
        mock_device = MagicMock()
        mock_device.isNull.return_value = True
        self.mock_audio_output.device.return_value = mock_device
        
        self.audio_manager._on_audio_outputs_changed()
        
        self.audio_manager._recover_audio_state.assert_called_once()

    @patch('src.core.audio_manager.QMediaDevices')
    def test_recover_audio_state_resets_device(self, mock_md_cls):
        """Test that recovery attempts to set the default device."""
        # Setup default device return
        mock_default_device = MagicMock()
        mock_default_device.isNull.return_value = False
        mock_default_device.description.return_value = "Speakers"
        mock_md_cls.defaultAudioOutput.return_value = mock_default_device
        
        self.audio_manager._recover_audio_state()
        
        # Verify device was set on audio output and tick effect
        self.mock_audio_output.setDevice.assert_called_with(mock_default_device)
        self.mock_tick_effect.setAudioDevice.assert_called_with(mock_default_device)

if __name__ == '__main__':
    unittest.main()
