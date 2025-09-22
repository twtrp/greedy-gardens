from src.library.essentials import *

class Button:
    def __init__(self,
                 game: object,
                 id: str,
                 group: str = 'default',
                 surface: pygame.Surface = None,
                 width: int = 0,
                 height: int = 0,
                 pos: tuple = (0, 0),
                 pos_anchor: str = posanchors.topleft,
                 padding_x: int = 0,
                 padding_y: int = 0,
                 enable_click: bool = True,
                 hover_cursor: dict = cursors.hand):
        self.game = game
        self.id = id
        self.group = group

        self.para_width = width
        self.para_height = height
        self.para_padding_x = padding_x
        self.para_padding_y = padding_y
        self.pos = pos
        self.pos_anchor = pos_anchor

        # Keep an unscaled base surface so we always scale from the original
        # This prevents cumulative scaling when display mode / screen size changes
        if surface is not None:
            self.base_surface = surface
        else:
            # ensure a non-zero base surface when width/height provided
            bw = self.para_width if self.para_width != 0 else 1
            bh = self.para_height if self.para_height != 0 else 1
            self.base_surface = pygame.Surface((bw, bh), pygame.SRCALPHA)

        self.hovered = False
        self.pressed = False
        self.clicked = False
        self.enable_click = enable_click
        self.hover_cursor = hover_cursor

        self.update_scale()
        self.create_surface()
        self.set_pos(self.pos, self.pos_anchor)

    def create_surface(self):
        # Create the button surface in canvas-space (unscaled). This lets the
        # entire canvas be scaled later when rendering, keeping rendering and
        # input logic consistent.
        # padding and sizes are expected to be in canvas coordinates
        self.padding_x = self.para_padding_x
        self.padding_y = self.para_padding_y

        base_w = self.para_width if self.para_width != 0 else self.base_surface.get_width()
        base_h = self.para_height if self.para_height != 0 else self.base_surface.get_height()

        actual_width = int(base_w + 2 * self.padding_x)
        actual_height = int(base_h + 2 * self.padding_y)

        # Create the button surface (canvas-space)
        self.surface = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        target_w = max(1, int(actual_width - 2 * self.padding_x))
        target_h = max(1, int(actual_height - 2 * self.padding_y))
        scaled_button_surface = pygame.transform.scale(self.base_surface, (target_w, target_h))
        self.surface.blit(scaled_button_surface, (int(self.padding_x), int(self.padding_y)))

        # Rectangle in canvas coordinates (used for rendering onto the canvas)
        self.canvas_rect = self.surface.get_rect()

        # Rectangle in screen coordinates (used for mouse collision). Will be
        # computed from canvas_rect using the game's display_scale and offset.
        try:
            scale = self.game.display_scale
        except Exception:
            scale = 1.0
        screen_w = max(1, int(self.canvas_rect.width * scale))
        screen_h = max(1, int(self.canvas_rect.height * scale))
        self.rect = pygame.Rect(0, 0, screen_w, screen_h)

    def update_scale(self):
        # For layout we keep canvas-space units; display scaling is handled
        # centrally by the Game instance. This method primarily triggers when
        # the game display geometry changes so we can recompute the screen rect.
        try:
            scale = self.game.display_scale
        except Exception:
            scale = self.game.screen_width / constants.canvas_width
        self.scale_x = scale
        self.scale_y = scale
        self.padding_x = self.para_padding_x
        self.padding_y = self.para_padding_y

    def toggle_click(self, enable: bool):
        self.enable_click = enable

    def set_pos(self, pos: tuple, pos_anchor: str):
        # Position is provided in canvas coordinates. Set canvas_rect for
        # rendering, and compute the screen-space rect for collision.
        setattr(self.canvas_rect, pos_anchor, (int(pos[0]), int(pos[1])))
        # Compute screen rect using display scale/offset
        try:
            scale = self.game.display_scale
            offx, offy = int(self.game.display_offset[0]), int(self.game.display_offset[1])
        except Exception:
            scale = 1.0
            offx, offy = 0, 0

        screen_x = int(self.canvas_rect.left * scale) + offx
        screen_y = int(self.canvas_rect.top * scale) + offy
        screen_w = max(1, int(self.canvas_rect.width * scale))
        screen_h = max(1, int(self.canvas_rect.height * scale))
        self.rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)

    def check_collision(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, dt, events):
        new_scale_x = self.game.screen_width / constants.canvas_width
        new_scale_y = self.game.screen_height / constants.canvas_height

        if new_scale_x != self.scale_x or new_scale_y != self.scale_y:
            self.update_scale()
            # Recreate the scaled surface from the original base surface
            self.create_surface()
            self.set_pos(self.pos, self.pos_anchor)

        # Use screen-space mouse for collision because self.rect is in screen coords
        mx, my = pygame.mouse.get_pos()
        try:
            offx, offy = self.game.display_offset
            scale = self.game.display_scale
        except Exception:
            offx, offy = (0, 0)
            scale = 1.0

        # If mouse is inside the visible (scaled) canvas area, perform collision
        within_canvas = (mx >= offx and my >= offy and mx < offx + int(constants.canvas_width * scale) and my < offy + int(constants.canvas_height * scale))
        if not within_canvas:
            self.hovered = False
        else:
            self.hovered = self.rect.collidepoint((mx, my))

        if self.enable_click:
            self.clicked = False
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.hovered:
                        self.pressed = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.hovered and self.pressed:
                        self.clicked = True
                    self.pressed = False
        else:
            self.pressed = False
            self.clicked = False

    def render(self, canvas):
        # Draw the button on the provided canvas (canvas-space). Use
        # canvas_rect which is positioned in canvas coordinates.
        canvas.blit(self.surface, self.canvas_rect)
        # Optional debug outline on the canvas
        # pygame.draw.rect(canvas, (255, 0, 0), self.canvas_rect, 1)