# sounds.py - Sound effects manager
import pygame
import os

pygame.mixer.init()

class SoundManager:
    """Quản lý tất cả sound effects trong game"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Sound effects dictionary
        self.sounds = {}
        self.music_playing = False
        
        # Volume settings
        self.sfx_volume = 0.7
        self.music_volume = 0.4
        
        # Load all sounds
        self._load_sounds()
    
    def _load_sound(self, name, filename):
        """Load một sound file, return None nếu không tìm thấy"""
        path = os.path.join("sounds", filename)
        if os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
                return True
            except:
                print(f"Warning: Could not load sound {filename}")
        return False
    
    def _load_sounds(self):
        """Load tất cả sound effects"""
        # Tạo folder sounds nếu chưa có
        if not os.path.exists("sounds"):
            os.makedirs("sounds")
            print("Created 'sounds' folder. Add sound files to enable audio!")
        
        # Sound mapping: name -> filename
        sound_files = {
            # Player actions
            'dash': 'dash.wav',
            'footstep': 'footstep.wav',
            
            # Collectibles
            'key_collect': 'key_collect.wav',
            'powerup_collect': 'powerup_collect.wav',
            
            # Combat
            'bullet_fire': 'bullet_fire.wav',
            'bullet_hit': 'bullet_hit.wav',
            'player_hit': 'player_hit.wav',
            
            # UI
            'button_click': 'button_click.wav',
            'button_hover': 'button_hover.wav',
            
            # Game events
            'door_open': 'door_open.wav',
            'level_complete': 'level_complete.wav',
            'game_over': 'game_over.wav',
            
            # Ambient
            'shield_activate': 'shield_activate.wav',
            'speed_boost': 'speed_boost.wav',
            'slow_time': 'slow_time.wav',
        }
        
        loaded_count = 0
        for name, filename in sound_files.items():
            if self._load_sound(name, filename):
                loaded_count += 1
        
        if loaded_count == 0:
            print("No sound files found. Game will run without audio.")
            print("Add .wav files to the 'sounds' folder to enable sound effects.")
        else:
            print(f"Loaded {loaded_count} sound effects.")
    
    def play(self, sound_name):
        """Play một sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_music(self, filename):
        """Play background music (looped)"""
        path = os.path.join("sounds", filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop forever
                self.music_playing = True
            except:
                print(f"Warning: Could not load music {filename}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def set_sfx_volume(self, volume):
        """Set volume cho sound effects (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume):
        """Set volume cho music (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)


# Global sound manager instance
sound_manager = SoundManager()


# Convenience functions
def play_sound(name):
    """Shortcut để play sound"""
    sound_manager.play(name)

def play_music(filename="background_music.wav"):
    """Shortcut để play music"""
    sound_manager.play_music(filename)

def stop_music():
    """Shortcut để stop music"""
    sound_manager.stop_music()
