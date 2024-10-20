from src.library.essentials import *
from src.template.BaseEntity import BaseEntity

class Wind(BaseEntity):
    def __init__(self, surface, sprites):
        BaseEntity.__init__(self)
        self.x = random.randint(0, surface.get_width())
        self.y = random.randint(-32, surface.get_height()-32)

        self.sprites = sprites
        self.surface = surface

        self.current_stage = 1     
        self.time_passed = 0
        self.time_interval = 0.1
        self.x_step = 7
        self.y_offset = 0
        if random.random() <= 0.5:
            self.flip = True
        else:
            self.flip = False


    #Class methods
    
    def update_y_offset(self, y_offset):
        self.y_offset = y_offset


    #Main methods

    def update(self, dt, events):
        self.time_passed += dt
        self.current_stage = round(self.time_passed/self.time_interval) + 1
        if self.current_stage >= len(self.sprites):
            self.active = False


    def render(self):
        if self.current_stage < len(self.sprites):
            sprite = self.sprites[f'wind_{self.current_stage}'] 
            if self.flip:
                sprite = pygame.transform.flip(surface=sprite, flip_x=False, flip_y=True)
            utils.blit(dest=self.surface,
                               source=sprite,
                               pos=(self.x - self.x_step*self.current_stage, self.y + self.y_offset), pos_type='topleft')

        