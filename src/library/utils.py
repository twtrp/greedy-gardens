from src.library.core import *
from src.library.resource_loader import *


# Surface functions

def blit(dest, source, pos=(0, 0), pos_anchor='topleft', debug_outline=False, debug_outline_color=(255, 0, 0)):
    """
    Use this instead of pygame's blit.
    Returns nothing

    dest: Surface = surface to blit to
    source: Surface = surface to blit
    pos: coords = position on the dest surface to blit to
    pos_anchor: str = center, topleft, topright, bottomleft, bottomright, midtop, midbottom, midleft, midright
    debug_outline: bool = True to draw a debug outline around the source surface
    debug_outline_color: Color = color of the debug outline
    """
    if pos_anchor == 'topleft':
        dest.blit(source=source, dest=pos)
    else:
        source_rect = source.get_rect()
        setattr(source_rect, pos_anchor, pos)
        dest.blit(source=source, dest=source_rect)
    
    if debug_outline:
        pygame.draw.rect(dest, debug_outline_color, source_rect, 1)


def get_text(text, font, size, color):
    """
    Use this to get a text surface
    Returns Surface

    text: str = text to render
    font: dict = the font dictionary imported from fonts.py
    size: str = font size key defined in the font_data
    color: Color = text color
    """
    text_font = pygame.font.Font(os.path.join(dir.fonts, font['file']), font['sizes'][size])
    text_font_render = text_font.render(text=text, antialias=False, color=color)
    return text_font_render


def get_font_size_number(font, size):
    """
    Returns int

    font: str = font name defined in objects.fonts
    size: str = font size key defined in objects.fonts
    """
    return font['sizes'][size]


def get_font_deco_distance(font, size):
    """
    Returns int

    font: str = font name defined in objects.fonts
    size: str = font size key defined in objects.fonts
    """
    font_size = font['sizes'][size]
    pixel_size_divisor = font['pixel_size_divisor']
    return font_size//pixel_size_divisor


def load_image(dir, name, mode=None, colorkey=(0, 0, 0)):
    """
    Use this instead of pygame's load image
    Returns Surface

    dir: str = directory of the image. please use the constants defined in this file
    name: str = name of the image with .filetype
    mode: str = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey: Color = color to set as transparent if mode is 'colorkey'
    """
    image = pygame.image.load(os.path.join(dir, name))
    if mode == 'alpha':
        return image.convert_alpha()
    elif mode == 'colorkey':
        image = image.convert()           
        image.set_colorkey(colorkey)
        return image
    else:
        return image.convert()
    

def load_sprite(sprite_sheet, target_sprite, mode='colorkey', colorkey=(0, 0, 0)):
    """
    Use this to get a single sprite from a sprite sheet
    Returns Surface

    sprite_sheet: str = name of the sprite sheet image with .filetype
    target_sprite: str = name of the sprite to get from the sprite sheet map
    mode: str = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey: Color = color to set as transparent if mode is 'colorkey'
    """
    shared_data = sprite_sheet['shared_data']
    sprite_data = sprite_sheet['sprites'][target_sprite]
    full_sprite_data = {**shared_data, **sprite_data}

    width = full_sprite_data['width']
    height = full_sprite_data['height']
    x = full_sprite_data['x']
    y = full_sprite_data['y']

    sprite_sheet_image = load_image(dir=dir.sprites, name=sprite_sheet['file'], mode=mode, colorkey=colorkey)
    sprite = pygame.Surface(size=(width, height), flags=pygame.SRCALPHA)
    sprite.blit(source=sprite_sheet_image, dest=(0, 0), area=(x, y, width, height))

    return sprite


def load_sprite_sheet(sprite_sheet, mode='colorkey', colorkey=(0, 0, 0)):
    """
    Use this to get all sprites from a sprite sheet as set
    Returns dict of Surfaces

    sprite_sheet: str = name of the sprite sheet image with .filetype
    mode: str = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey: Color = color to set as transparent if mode is 'colorkey'
    """
    sprites = {}
    for sprite_name in sprite_sheet['sprites']:
        sprites[sprite_name] = load_sprite(sprite_sheet=sprite_sheet, target_sprite=sprite_name, mode=mode, colorkey=colorkey)
    
    return sprites


def effect_pixelate(surface, pixel_size=1):
    """
    Use this to pixelate a surface
    Returns Surface

    surface: Surface = surface to pixelate
    pixel_size: int = size of the pixelation filter
    """
    original_width = surface.get_width()
    original_height = surface.get_height()
    
    scaled_down_surface = pygame.transform.scale(surface=surface, size=(original_width / pixel_size, original_height / pixel_size))
    scaled_up_surface = pygame.transform.scale(surface=scaled_down_surface, size=(original_width, original_height))
    return scaled_up_surface


def effect_silhouette(surface, color=(0, 0, 0)):
    """
    Use this to create a silhouette of a surface
    Returns Surface

    surface: Surface = surface to create a silhouette of
    color: Color = color of the silhouette
    """
    mask = pygame.mask.from_surface(surface=surface)
    mask_surface = mask.to_surface(unsetcolor=(1, 2, 3))
    mask_surface.set_colorkey((1, 2, 3))
    mask_width = mask_surface.get_width()
    mask_height = mask_surface.get_height()
    for x in range(mask_width):
        for y in range(mask_height):
            if mask_surface.get_at((x, y))[0] == 255:
                mask_surface.set_at((x, y), color)
    return mask_surface


def effect_long_shadow(surface, direction='top-left', distance=1, color=(255, 255, 255)):
    """
    Use this to emboss a surface
    Returns Surface

    surface: Surface = surface to emboss
    direction: str = 'top-left', 'top', 'top-right', 'left', 'right', 'bottom-left', 'bottom', 'bottom-right'
    distance: int = distance of the emboss effect
    color: Color = color of the emboss effect
    """
    if direction == 'top-left':
        shadow_vector = (-1, -1)
    elif direction == 'top':
        shadow_vector = (0, -1)
    elif direction == 'top-right':
        shadow_vector = (1, -1)
    elif direction == 'left':
        shadow_vector = (-1, 0)
    elif direction == 'right':
        shadow_vector = (1, 0)
    elif direction == 'bottom-left':
        shadow_vector = (-1, 1)
    elif direction == 'bottom':
        shadow_vector = (0, 1)
    elif direction == 'bottom-right':
        shadow_vector = (1, 1)
    else:
        shadow_vector = (0, 0)
        print('WARNING: invalid long shadow direction')
    
    padding_x = abs(shadow_vector[0])*distance
    padding_y = abs(shadow_vector[1])*distance
    final_surface = pygame.Surface(size=(surface.get_width() + padding_x, surface.get_height() + padding_y), flags=pygame.SRCALPHA)
    surface_silhouette = effect_silhouette(surface=surface, color=color)
    for i in range(1, distance + 1):
        blit(dest=final_surface, source=surface_silhouette, pos=(shadow_vector[0]*i, shadow_vector[1]*i))

    blit(dest=final_surface, source=surface)
    return final_surface


def effect_outline(surface, distance=1, color=(255, 255, 255), no_corner=False):
    """
    Use this to outline a surface
    Returns Surface

    surface: Surface = surface to outline
    color: Color = color of the outline
    distance: int = distance of the outline effect
    noncorner: bool = True for non-corner outline, False for corner outline
    """
    padding_x = 2*distance
    padding_y = 2*distance
    final_surface = pygame.Surface(size=(surface.get_width() + padding_x, surface.get_height() + padding_y), flags=pygame.SRCALPHA)
    surface_silhouette = effect_silhouette(surface=surface, color=color)
    if not no_corner:
        for dx in range(-distance, distance + 1):
            for dy in range(-distance, distance + 1):
                if dx == 0 and dy == 0:
                    continue
                blit(dest=final_surface, source=surface_silhouette, pos=(dx + distance, dy + distance))
    else:
        for dx in range(-distance, distance + 1):
            if dx == 0:
                continue
            blit(dest=final_surface, source=surface_silhouette, pos=(dx + distance, distance))
        for dy in range(-distance, distance + 1):
            if dy == 0:
                continue
            blit(dest=final_surface, source=surface_silhouette, pos=(distance, dy + distance))

    blit(dest=final_surface, source=surface, pos=(distance, distance))
    return final_surface


# Color functions

def color_darken(color, factor):
    """
    Darken a color by a given percentage.
    Returns Color

    color: Color = original color
    factor: float [0,1] = percentage to darken the color by. 0 means no change. 1 means black
    """
    if not isinstance(color, pygame.Color):
        color = pygame.Color(color)
    return color.lerp(pygame.Color(0, 0, 0), factor)


def color_lighten(color, factor):
    """
    Lighten a color by a given percentage.
    Returns Color

    color: Color = original color
    factor: float [0,1] = percentage to lighten the color by. 0 means no change. 1 means white
    """
    if not isinstance(color, pygame.Color):
        color = pygame.Color(color)
    return color.lerp(pygame.Color(255, 255, 255), factor)


# Sound functions

def music_load(music_channel, name):
    """
    Use this to load music if the queue is empty
    Returns nothing

    music_channel: pygame.mixer.music
    name: str = name of the music file with .filetype
    """
    music_channel.load(filename=os.path.join(dir.music, name))


def music_queue(music_channel, name, loops=0):
    """
    Use this to add music to the queue
    Returns nothing

    music_channel: pygame.mixer.music
    name: str = name of the music file with .filetype
    loops: int = number of times to loop the music. 0 means no loop. -1 means infinite loop
    """
    music_channel.queue(filename=os.path.join(dir.music, name), loops=loops)


def sound_play(sound_channel, sound_name, loops=0, maxtime=0, fade_ms=0):
    """
    Use this to play sound effects
    Returns nothing

    sound_channel: pygame.mixer.Channel
    sound_name: str = name of the sound effect file with .filetype
    loops: int = number of times to loop the sound effect. 0 means no loop. -1 means infinite loop
    maxtime: int = number of milliseconds to play the sound effect
    fade_ms: int = number of milliseconds to fade the sound effect in or out
    """
    sound = pygame.mixer.Sound(file=os.path.join(dir.sfx, sound_name))
    sound_channel.play(sound, loops=loops, maxtime=maxtime, fade_ms=fade_ms)
