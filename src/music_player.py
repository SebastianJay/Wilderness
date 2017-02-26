"""
Definition of MusicPlayer, which is a wrapper around the pygame mixer module
"""
from pygame.mixer import init
import pygame.mixer as mixer

class MusicPlayer:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __MusicPlayer:
        def __init__(self):
            init()  # initialize the mixer

        def update(self, dt):
            pass

        def playNext(self, song):
            mixer.music.load(song)
            mixer.music.play(-1)

        def pause(self):
            mixer.music.pause()

        def resume(self):
            mixer.music.unpause()

        def fadeOut(self):
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
