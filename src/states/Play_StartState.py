from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.load_assets()

    def load_assets(self):
        canvas_width = self.game.canvas.get_width()
        canvas_height = self.game.canvas.get_height()

        # Load white side box
        self.boxes = []
        self.box_color = (*colors.white, 191) # 75% transparency (191)
        self.border_color = colors.black
        self.border_thickness = 3
        box_width = 265
        
        left_box_rect = pygame.Rect(self.border_thickness, self.border_thickness, box_width, canvas_height - 2 * self.border_thickness)
        right_box_rect = pygame.Rect(canvas_width - box_width - self.border_thickness, self.border_thickness, box_width, canvas_height - 2 * self.border_thickness)

        self.boxes = [left_box_rect, right_box_rect]

        self.transparent_surface = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        self.transparent_surface.fill((0, 0, 0, 0))

        # Render boxes in the list
        for box in self.boxes:
            border_rect = pygame.Rect(
                box.x - self.border_thickness,
                box.y - self.border_thickness,
                box.width + 2 * self.border_thickness,
                box.height + 2 * self.border_thickness
            )
            pygame.draw.rect(self.transparent_surface, self.border_color, border_rect)
            pygame.draw.rect(self.transparent_surface, self.box_color, box)
        
        canvas.blit(self.transparent_surface, (0, 0))