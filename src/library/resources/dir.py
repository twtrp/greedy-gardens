from src.library.core import *
import platform

if platform.system() in ['Windows', 'Linux']:
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

elif platform.system() == 'Darwin':
    '''MacOS'''
    def resource_path(*parts):
        if getattr(sys, "frozen", False): 
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base,*parts)

    assets = resource_path('assets')
    data = resource_path('data')
    src = resource_path('src')

    fonts = resource_path('assets', 'fonts')
    graphics = resource_path('assets', 'graphics')
    sounds = resource_path('assets', 'sounds')

    branding = resource_path('assets', 'graphics', 'branding')
    bts = resource_path('assets', 'graphics', 'bts')
    menu_bg = resource_path('assets', 'graphics', 'menu_bg')
    play_bg = resource_path('assets', 'graphics', 'play_bg')
    sprites = resource_path('assets', 'graphics', 'sprites')
    music = resource_path('assets', 'sounds', 'music')
    sfx = resource_path('assets', 'sounds', 'sfx')