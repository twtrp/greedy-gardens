from src.library.essentials import *
from src.template.BaseState import BaseState


class Play_PlacePathState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.game = game

        print("Placing")

        # value
        self.cell_pos = -1

        #state
        self.is_placed = False

        self.select_frame = self.parent.selecting_tile

    def update(self, dt, events):
        
        self.cell_pos = -1
        for button in self.parent.grid_buttons:
            if button.hovered:
                self.cell_pos = button.id
                if not self.parent.game_board.board[button.id].path and not self.parent.game_board.board[button.id].home:
                    self.select_frame = self.parent.selecting_tile
                    if button.clicked:
                        if "N" in self.parent.current_path:
                            self.parent.game_board.board[button.id].north = True
                        if "W" in self.parent.current_path:
                            self.parent.game_board.board[button.id].west = True 
                        if "E" in self.parent.current_path:
                            self.parent.game_board.board[button.id].east = True
                        if "S" in self.parent.current_path:
                            self.parent.game_board.board[button.id].south = True
                        self.parent.game_board.board[button.id].path = True
                        # self.parent.game_board.eval_new_tile(button.id)
                        self.parent.game_board.check_connection(self.parent.game_board.connected_indices, self.parent.game_board.home_index)
                        self.is_placed = True
                else:
                    self.select_frame = self.parent.cant_selecting_tile
                    # for debug
                    # print(f"Hit box {button.id} clicked!")
                    # self.parent.game_board.board[button.id].show_detail()
        
        # for event in events:
        #     self.mouse_pos = pygame.mouse.get_pos()
        #     # self.cell_pos = -1
        #     for i, rect in enumerate(self.parent.grid_hitboxes):
        #         if rect.collidepoint(self.mouse_pos):
        #             self.cell_pos = i
        #             if not self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
        #                 self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile', mode='alpha')
        #                 if event.type == pygame.MOUSEBUTTONDOWN:
        #                     if "N" in self.parent.current_path:
        #                         self.parent.game_board.board[i].north = True
        #                     if "W" in self.parent.current_path:
        #                         self.parent.game_board.board[i].west = True 
        #                     if "E" in self.parent.current_path:
        #                         self.parent.game_board.board[i].east = True
        #                     if "S" in self.parent.current_path:
        #                         self.parent.game_board.board[i].south = True
        #                     self.parent.game_board.board[i].path = True
        #                     self.is_placed = True
        #             else:
        #                 self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile', mode='alpha')
        #                 # for debug
        #                 print(f"Hit box {i} clicked!")
        #                 self.parent.game_board.board[i].show_detail()
                    
        if self.is_placed:
            if self.parent.game_board.magic_fruit_index:
                self.parent.magic_eventing, magic_number, cell_pos = self.parent.game_board.magic_fruit_found()
                if self.parent.magic_eventing:
                    if magic_number == 1:
                        self.parent.current_event = self.parent.magic_fruit1_event
                    elif magic_number == 2:
                        self.parent.current_event = self.parent.magic_fruit2_event
                    elif magic_number == 3:
                        self.parent.current_event = self.parent.magic_fruit3_event
                    self.parent.game_board.board[cell_pos].magic_fruit = 0
                    self.exit_state()

                elif not self.parent.magic_eventing:
                    if "strike" in self.parent.current_path:
                        self.parent.is_strike = True
                    else: 
                        self.parent.drawing = True
                    self.parent.current_path = None
                    print("exiting place")
                    self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.cell_pos >= 0:
            utils.blit(dest=canvas, source=self.select_frame , pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')
