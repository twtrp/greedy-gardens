from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule
import math

class Module_Arrow(BaseTutorialModule):
    def __init__(
            self,
            pos: tuple = (constants.canvas_width // 2, constants.canvas_height // 2),
            direction: str = 'down',
            enable_animation: bool = True,
            animation_amplitude: int = 5,
            animation_speed: float = 1.0,
            fade_duration: int = 300,
        ):
        super().__init__(fade_duration=fade_duration)
        
        if direction not in ['left', 'right', 'down', 'up']:
            raise ValueError(f"direction must be 'left', 'right', 'down', or 'up', got '{direction}'")
        
        self.direction = direction
        self.base_pos = list(pos)  # Store original position
        self.pos = list(pos)  # Current animated position
        
        if self.direction == 'left':
            self.pos_anchor = posanchors.midleft
        elif self.direction == 'right':
            self.pos_anchor = posanchors.midright
        elif self.direction == 'up':
            self.pos_anchor = posanchors.midtop
        elif self.direction == 'down':
            self.pos_anchor = posanchors.midbottom
        
        # Animation properties
        self.enable_animation = enable_animation
        self.animation_amplitude = animation_amplitude
        self.animation_speed = animation_speed
        self.animation_time = 0

        self.surface = utils.get_sprite(
            sprite_sheet=spritesheets.gui,
            target_sprite=f'pointer_{self.direction}'
        )
        self.surface = pygame.transform.scale_by(surface=self.surface, factor=3)
    
    def _update_inject(self, dt, events):
        if self.enable_animation:
            self.animation_time += dt * self.animation_speed
            
            offset = math.sin(self.animation_time * math.pi) * self.animation_amplitude
            
            if self.direction == 'left':
                self.pos = [self.base_pos[0] + offset + self.animation_amplitude, self.base_pos[1]]
            elif self.direction == 'right':
                self.pos = [self.base_pos[0] - offset - self.animation_amplitude, self.base_pos[1]]
            elif self.direction == 'up':
                self.pos = [self.base_pos[0], self.base_pos[1] + offset + self.animation_amplitude]
            elif self.direction == 'down':
                self.pos = [self.base_pos[0], self.base_pos[1] - offset - self.animation_amplitude] 
