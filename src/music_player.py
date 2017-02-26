"""
Definition of MusicPlayer, which is a wrapper around the pygame mixer module
"""
from game_state import GameState
from asset_loader import AssetLoader
from pygame.mixer import init
import pygame.mixer as mixer

class MusicPlayer:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __MusicPlayer:
        def __init__(self):
            init()  # initialize the pygame mixer
            self.isEnabled = True
            self.currentSong = ''
            GameState().onSettingChange += self.settingsChangeHandler()

        def settingsChangeHandler(self):
            def _settingsChangeHandler(*args, **kwargs):
                if args[0] == 'backgroundMusic':
                    self.isEnabled = True if args[1] == 0 else False
                    if self.isEnabled:
                        if self.currentSong != '':
                            self.playNext(self.currentSong)
                        else:
                            self.playNext(AssetLoader().getMusicPath('title'))
                    else:
                        mixer.music.stop()
            return _settingsChangeHandler

        def update(self, dt):
            pass

        def playNext(self, song):
            if self.isEnabled:
                self.currentSong = song
                mixer.music.load(song)
                mixer.music.play(-1)

        def pause(self):
            if self.isEnabled:
                mixer.music.pause()

        def resume(self):
            if self.isEnabled:
                mixer.music.unpause()

        def fadeOut(self):
            if self.isEnabled:
                pass
            pass

    instance = None
    def __new__(cls):
        if not MusicPlayer.instance:
            MusicPlayer.instance = MusicPlayer.__MusicPlayer()
        return MusicPlayer.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
