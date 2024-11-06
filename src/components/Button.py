from src.library.essentials import *

class Button:
    def __init__(self,
                 id: str, 
                 surface: pygame.Surface,
                 width: int = 0,
                 height: int = 0,
                 pos: tuple = (0, 0),
                 pos_anchor: str = 'topleft',
                 padding_x: int = 0,
                 padding_y: int = 0):
        self.id = id
        self.surface = surface
        self.padding_x = padding_x
        self.padding_y = padding_y

        self.hovered = False
        self.pressed = False
        self.clicked = False

        self.enable_hover = True
        self.enable_click = True

        self.rect: pygame.Rect = self.surface.get_rect()
        if width != 0:
            self.rect.width = width
        if height != 0:
            self.rect.height = height
        self.rect.width += 2*self.padding_x
        self.rect.height += 2*self.padding_y
        setattr(self.rect, pos_anchor, pos)


    # Class methods

    def toggle_hover(self, enable: bool):
        self.enable_hover = enable


    def toggle_click(self, enable: bool):
        self.enable_click = enable


    def set_pos(self, pos: tuple, pos_anchor: str):
        setattr(self.rect, pos_anchor, pos)
        

    #Main methods

    def update(self, dt, events):
        pos = pygame.mouse.get_pos()
        
        if self.enable_hover:
            if self.rect.collidepoint(pos):
                self.hovered = True
            else:
                self.hovered = False
        else:
            self.hovered = False

        if self.enable_click:
            if self.clicked:
                self.clicked = False

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.rect.collidepoint(pos):
                        self.pressed = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.rect.collidepoint(pos) and self.pressed:
                        self.clicked = True
                    self.pressed = False

        else:
            self.pressed = False
            self.clicked = False


    def render(self, canvas):
        """
        Render button outline
        """
        pygame.draw.rect(canvas, (255, 0, 0), self.rect, 2)

        