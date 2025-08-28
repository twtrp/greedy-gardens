from src.library.core import *
from src.library.resource_loader import *

def blit(dest: pygame.Surface,
         source: pygame.Surface,
         pos: tuple = (0, 0),
         pos_anchor: str = posanchors.topleft,
         debug_outline: bool = False,
         debug_outline_color: pygame.Color = (255, 0, 0)
        )     None:
    '''
    Use this instead of pygame's blit.
    Returns nothing

    dest = surface to blit to
    source = surface to blit
    pos = position on the dest surface to blit to
    pos_anchor = center, topleft, topright, bottomleft, bottomright, midtop, midbottom, midleft, midright
    debug_outline = True to draw a debug outline around the source surface
    debug_outline_color = color of the debug outline
    '''
    if pos_anchor == posanchors.topleft:
        dest.blit(source=source, dest=pos)
    else:
        source_rect = source.get_rect()
        setattr(source_rect, pos_anchor, pos)
        dest.blit(source=source, dest=source_rect)
    
    if debug_outline:
        source_rect = source.get_rect()
        pygame.draw.rect(dest, debug_outline_color, source_rect, 1)


def effect_silhouette(surface: pygame.Surface, 
                      color: pygame.Color = (0, 0, 0)
                     )     pygame.Surface:
    '''
    Use this to create a silhouette of a surface
    Returns Surface

    surface = surface to create a silhouette of
    color = color of the silhouette
    '''
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


def effect_long_shadow(surface: pygame.Surface,
                       direction: str = 'top-left',
                       distance: int = 1,
                       color: pygame.Color = (255, 255, 255)
                      )     pygame.Surface:
    '''
    Use this to apply 3D on a surface
    Returns Surface

    surface = surface to apply 3D effect on
    direction = 'top-left', 'top', 'top-right', 'left', 'right', 'bottom-left', 'bottom', 'bottom-right'
    distance = distance of the 3D effect
    color = color of the 3D effect
    '''
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


def effect_outline(surface: pygame.Surface,
                   distance: int = 1,
                   color: pygame.Color = (255, 255, 255),
                   no_corner: bool = False
                  )     pygame.Surface:
    '''
    Use this to outline a surface
    Returns Surface

    surface = surface to outline
    distance = distance of the outline effect
    color = color of the outline
    no_corner = True for non-corner outline, False for corner outline
    '''
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