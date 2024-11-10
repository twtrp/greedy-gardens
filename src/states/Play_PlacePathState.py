from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_PlacePathState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Placing")

        # value
        self.cell_pos = -1
        pos_x = 0
        pos_y = 0

    def update(self, dt, events):

        for event in events:
            self.mouse_pos = pygame.mouse.get_pos()
            self.cell_pos = -1
            for i, rect in enumerate(self.parent.grid_hitboxes):
                if rect.collidepoint(self.mouse_pos):
                    self.cell_pos = int(i)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if "N" in self.parent.current_path:
                            self.parent.game_board.board[i].north = True
                        if "W" in self.parent.current_path:
                            self.parent.game_board.board[i].west = True
                        if "E" in self.parent.current_path:
                            self.parent.game_board.board[i].east = True
                        if "S" in self.parent.current_path:
                            self.parent.game_board.board[i].south = True
                        # for debug
                        print(f"Hit box {i} clicked!")
                        self.parent.game_board.board[i].show_detail()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.cell_pos >= 0:
            self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
            scaled_selecting_tile = pygame.transform.scale_by(surface=self.selecting_tile, factor=1.25)
            utils.blit(dest=canvas, source=scaled_selecting_tile, pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')
