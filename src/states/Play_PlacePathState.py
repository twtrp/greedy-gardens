from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_PlacePathState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Placing")

        # value
        self.cell_pos = -1

        #state
        self.is_placed = False

        self.load_assets()

    def load_assets(self):
        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')

    def update(self, dt, events):

        for event in events:
            self.mouse_pos = pygame.mouse.get_pos()
            self.cell_pos = -1
            for i, rect in enumerate(self.parent.grid_hitboxes):
                if rect.collidepoint(self.mouse_pos):
                    self.cell_pos = i
                    if not self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if "N" in self.parent.current_path:
                                self.parent.game_board.board[i].north = True
                            if "W" in self.parent.current_path:
                                self.parent.game_board.board[i].west = True 
                            if "E" in self.parent.current_path:
                                self.parent.game_board.board[i].east = True
                            if "S" in self.parent.current_path:
                                self.parent.game_board.board[i].south = True
                            self.parent.game_board.board[i].path = True
                            self.is_placed = True
                    else:
                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')
                        # # for debug
                        # print(f"Hit box {i} clicked!")
                        # self.parent.game_board.board[i].show_detail()
                    
        if self.is_placed:
            if "strike" in self.parent.current_path:
                self.parent.is_strike = True
            else: 
                self.parent.drawing = True
            print("exiting place")
            self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.cell_pos >= 0:
            utils.blit(dest=canvas, source=self.selecting_tile , pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')