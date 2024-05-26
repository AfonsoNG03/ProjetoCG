import os
import pygame.mixer

class Music:
    def __init__(self):
        pygame.mixer.init()
        self.music_file = 'music/FF2.mp3'
        self.play_music()
    
    def play_music(self):
        if not os.path.isfile(self.music_file):
            print(f"Music file not found: {self.music_file}")
        else:
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                print(f"Playing music: {self.music_file}")
            except pygame.error as e:
                print(f"Failed to load music file: {self.music_file}, error: {e}")
                pygame.mixer.quit()
