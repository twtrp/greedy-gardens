from src.library.essentials import *

class Button:
    def __init__(self,
                 game: object,
                 id: str, 
                 surface: pygame.Surface = None,
                 width: int = 0,
                 height: int = 0,
                 pos: tuple = (0, 0),
                 pos_anchor: str = 'topleft',
                 padding_x: int = 0,
                 padding_y: int = 0,
                 enable_click: bool = True,
                 hover_cursor: dict = cursors.hand):
        self.game = game
        self.scale_x = self.game.screen_width / constants.canvas_width
        self.scale_y = self.game.screen_height / constants.canvas_height

        self.id = id
        if surface is not None:
            self.surface = surface
        else:
            self.surface = pygame.Surface((width, height))
        self.para_width = width
        self.para_height = height

        self.para_padding_x = padding_x
        self.para_padding_y = padding_y
        self.padding_x = self.para_padding_x * self.scale_x
        self.padding_y = self.para_padding_y * self.scale_y

        self.hovered = False
        self.pressed = False
        self.clicked = False
        self.enable_click = enable_click
        self.hover_cursor = hover_cursor

        self.rect = self.surface.get_rect()
        if self.para_width != 0:
            self.rect.width = self.para_width * self.scale_x + 2 * self.padding_x
        if self.para_height != 0:
            self.rect.height = self.para_height * self.scale_y + 2 * self.padding_y
        setattr(self.rect, pos_anchor, (pos[0] * self.scale_x, pos[1] * self.scale_y))


    # Class methods

    def toggle_click(self, enable: bool):
        self.enable_click = enable


    def set_pos(self, pos: tuple, pos_anchor: str):
        setattr(self.rect, pos_anchor, pos)


    # Main methods

    def update(self, dt, events):
        new_scale_x = self.game.screen_width / constants.canvas_width
        new_scale_y = self.game.screen_height / constants.canvas_height

        # Check if scaling factors have changed
        if new_scale_x != self.scale_x or new_scale_y != self.scale_y:
            # Update scale values
            self.scale_x = new_scale_x
            self.scale_y = new_scale_y

            # Recalculate padding based on new scale
            self.padding_x = self.para_padding_x * self.scale_x
            self.padding_y = self.para_padding_y * self.scale_y

            # Set the rect width and height without additive increases
            self.rect.width = self.para_width * self.scale_x + 2 * self.padding_x
            self.rect.height = self.para_height * self.scale_y + 2 * self.padding_y

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            self.hovered = True
            if self.hover_cursor is not None:
                utils.set_cursor(self.hover_cursor)
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
        '''
        Render button outline
        '''
        pygame.draw.rect(canvas, (255, 0, 0), self.rect, 2)