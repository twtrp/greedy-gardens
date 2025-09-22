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
        # If running as a frozen bundle (pyinstaller), use the bundle temp folder
        if getattr(sys, "frozen", False):
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            return os.path.join(base, *parts)

        # When running from source on macOS, assets are stored at the repository root
        # (not under src). Walk up parent directories from this file to find an
        # `assets/` directory and return the joined path. If not found, fall back
        # to using the directory of this file.
        here = os.path.abspath(os.path.dirname(__file__))
        cur = here
        root = os.path.abspath(os.sep)
        while True:
            candidate = os.path.join(cur, *parts)
            # If parts starts with 'assets', also check for the directory itself when parts==('assets',)
            # but os.path.exists covers both files and dirs; prefer isdir for directories.
            if os.path.exists(candidate):
                return candidate
            # Additionally, if the first part is 'assets', check for an assets folder directly under cur
            if parts and parts[0] == 'assets':
                assets_dir = os.path.join(cur, 'assets')
                if os.path.isdir(assets_dir):
                    return os.path.join(assets_dir, *parts[1:]) if len(parts) > 1 else assets_dir
            if cur == root:
                break
            cur = os.path.dirname(cur)

        # Fallback: return path relative to this file
        return os.path.join(here, *parts)

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