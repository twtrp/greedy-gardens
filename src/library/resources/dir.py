from src.library.core import *
import os
import sys


'''Mac OS'''
def resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
assets = resource_path('assets')
data = resource_path('data')
src = resource_path('src')


'''Windows and Linux'''
# assets = os.path.join('assets')
# data = os.path.join('data')
# src = os.path.join('src')

fonts = os.path.join(assets, 'fonts')
graphics = os.path.join(assets, 'graphics')
sounds = os.path.join(assets, 'sounds')

menu_bg = os.path.join(graphics, 'menu_bg')
play_bg = os.path.join(graphics, 'play_bg')
sprites = os.path.join(graphics, 'sprites')
music = os.path.join(sounds, 'music')
sfx = os.path.join(sounds, 'sfx')
