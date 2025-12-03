from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule

class Module_Dim(BaseTutorialModule):
    """
    cutout format: [x1, y1, x2, y2]
    """
    def __init__(
            self,
            cutouts: list = [],
            fade_duration: int = 300,
            cutout_fade_duration: int = 0,
            opacity : int = 175
        ):
        super().__init__(fade_duration=fade_duration)
        
        self.pos = (0, 0)
        self.pos_anchor = posanchors.topleft
        self.cutouts = cutouts
        self.opacity = opacity
        
        # Separate fade tracking for cutouts
        self.cutout_fade_duration = cutout_fade_duration
        self.cutout_fade_timer = 0
        self.cutout_alpha = 0
        self.is_cutout_fading = True
        
        # Base dim surface (without cutouts)
        self.dim_surface = pygame.Surface(
            size=(constants.canvas_width, constants.canvas_height),
            flags=pygame.SRCALPHA
        )
        self.dim_surface.fill((*colors.black, self.opacity))
        
        # Cutout surface (separate)
        self.cutout_surface = pygame.Surface(
            size=(constants.canvas_width, constants.canvas_height),
            flags=pygame.SRCALPHA
        )
        
        # Create the final composited surface
        self.surface = pygame.Surface(
            size=(constants.canvas_width, constants.canvas_height),
            flags=pygame.SRCALPHA
        )
    
    def _update_inject(self, dt, events):
        # Update cutout fade animation separately
        if self.is_cutout_fading:
            self.cutout_fade_timer += dt * 1000
            if self.cutout_fade_timer >= self.cutout_fade_duration:
                self.cutout_alpha = 255
                self.is_cutout_fading = False
            else:
                self.cutout_alpha = int((self.cutout_fade_timer / self.cutout_fade_duration) * 255)
    
    def _render_inject(self, canvas):
        # Clear the cutout surface
        self.cutout_surface.fill((0, 0, 0, 0))
        
        # Draw cutouts with their own alpha
        for cutout in self.cutouts:
            pygame.draw.rect(
                surface=self.cutout_surface,
                rect=pygame.Rect(
                    cutout[0],
                    cutout[1],
                    cutout[2]-cutout[0],
                    cutout[3]-cutout[1]
                ),
                color=(*colors.black, self.cutout_alpha)
            )
        
        # Composite: start with dim surface, then subtract cutouts
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(self.dim_surface, (0, 0))
        self.surface.blit(self.cutout_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)