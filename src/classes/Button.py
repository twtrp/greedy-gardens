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
        self.id = id

        # Set the surface or create a default one with specified dimensions
        self.surface = surface if surface is not None else pygame.Surface((width, height))
        
        # Initial properties
        self.para_width = width
        self.para_height = height
        self.para_padding_x = padding_x
        self.para_padding_y = padding_y
        self.pos = pos
        self.pos_anchor = pos_anchor

        # Interaction flags
        self.hovered = False
        self.pressed = False
        self.clicked = False
        self.enable_click = enable_click
        self.hover_cursor = hover_cursor

        # Initial scale and padding calculations
        self.update_scale()
        self.rect = self.surface.get_rect()
        self.update_rect_dimensions()
        self.set_pos(self.pos, self.pos_anchor)


    def update_scale(self):
        """Update scale factors and padding based on current screen size."""
        self.scale_x = self.game.screen_width / constants.canvas_width
        self.scale_y = self.game.screen_height / constants.canvas_height
        self.padding_x = self.para_padding_x * self.scale_x
        self.padding_y = self.para_padding_y * self.scale_y


    def update_rect_dimensions(self):
        """Update the dimensions of the rect based on scale and padding."""
        if self.para_width != 0:
            self.rect.width = self.para_width * self.scale_x + 2 * self.padding_x
        if self.para_height != 0:
            self.rect.height = self.para_height * self.scale_y + 2 * self.padding_y


    def toggle_click(self, enable: bool):
        self.enable_click = enable


    def set_pos(self, pos: tuple, pos_anchor: str):
        setattr(self.rect, pos_anchor, (pos[0] * self.scale_x, pos[1] * self.scale_y))


    def update(self, dt, events):
        # Check if the scale factors have changed, and update if necessary
        new_scale_x = self.game.screen_width / constants.canvas_width
        new_scale_y = self.game.screen_height / constants.canvas_height

        if new_scale_x != self.scale_x or new_scale_y != self.scale_y:
            self.update_scale()
            self.update_rect_dimensions()
            self.set_pos(self.pos, self.pos_anchor)

        # Check for hover state
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.hovered = True
            if self.hover_cursor:
                utils.set_cursor(self.hover_cursor)
        else:
            self.hovered = False

        # Handle click events if enabled
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
        """Render button outline. Doesn't work in fullscreen not bothered to fix. Sorry."""
        pygame.draw.rect(canvas, (255, 0, 0), self.rect, 2)
