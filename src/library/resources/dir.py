from src.library.core import *
import os
import sys


'''Windows and Linux'''
assets = os.path.join('assets')
data = os.path.join('data')
src = os.path.join('src')

fonts = os.path.join(assets, 'fonts')
graphics = os.path.join(assets, 'graphics')
sounds = os.path.join(assets, 'sounds')

branding = os.path.join(graphics, 'branding')
bts = os.path.join(graphics, 'bts')
menu_bg = os.path.join(graphics, 'menu_bg')
play_bg = os.path.join(graphics, 'play_bg')
sprites = os.path.join(graphics, 'sprites')
music = os.path.join(sounds, 'music')
sfx = os.path.join(sounds, 'sfx')


''' mac-only override (runs only on macOS) '''
# def _mac_resources_base():
#     # PyInstaller onefile uses _MEIPASS
#     if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
#         return sys._MEIPASS
#     # PyInstaller onefolder .app: exe = .../MyApp.app/Contents/MacOS/MyApp
#     if getattr(sys, 'frozen', False):
#         macos_dir = os.path.dirname(sys.executable)             # .../Contents/MacOS
#         contents  = os.path.dirname(macos_dir)                  # .../Contents
#         resources = os.path.join(contents, "Resources")         # bundled data lives here
#         return resources
#     # Dev mode (running from source)
#     return os.path.dirname(__file__)

# def resource_path(rel_path):
#     base = _mac_resources_base()
#     inside = os.path.join(base, rel_path)       # bundled path
#     if os.path.exists(inside):
#         return inside
#     # fallback: allow external folders next to the .app (optional)
#     try:
#         appdir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))  # .../MyApp.app
#     except Exception:
#         appdir = os.getcwd()
#     sibling = os.path.join(os.path.dirname(appdir), rel_path)
#     return sibling if os.path.exists(sibling) else inside

# # Override ONLY on mac
# assets = resource_path('assets')
# data   = resource_path('data')
# src    = resource_path('src')

# fonts   = resource_path('assets/fonts')
# graphics= resource_path('assets/graphics')
# sounds  = resource_path('assets/sounds')

# menu_bg = resource_path('assets/graphics/menu_bg')
# play_bg = resource_path('assets/graphics/play_bg')
# sprites = resource_path('assets/graphics/sprites')
# music   = resource_path('assets/sounds/music')
# sfx     = resource_path('assets/sounds/sfx')
