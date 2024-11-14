from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Deck import Deck

class Play_PlayEventState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("playing event")

        # value
        self.box_width = 68
        self.box_height = 352

        self.cell_pos = -1

        # state
        self.played_event = False
        self.selecting_path = False
        self.selected_cell = None

        self.load_assets()

    def load_assets(self):
        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')

        self.path_WE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE')
        self.path_NS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS')
        self.path_NW_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW')
        self.path_NE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE')
        self.path_WS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS')
        self.path_ES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES')

    def update(self, dt, events):
        if not self.played_event:
            if self.parent.current_event == 'event_free':
                # print('event_free')
                self.selecting_path = True
                for event in events:
                    self.mouse_pos = pygame.mouse.get_pos()
                    self.cell_pos = -1
                    for i, rect in enumerate(self.parent.grid_hitboxes):
                        if rect.collidepoint(self.mouse_pos):
                            self.cell_pos = i
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if not self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                                    if "N" in self.parent.current_path:
                                        self.parent.game_board.board[i].north = True
                                    if "W" in self.parent.current_path:
                                        self.parent.game_board.board[i].west = True 
                                    if "E" in self.parent.current_path:
                                        self.parent.game_board.board[i].east = True
                                    if "S" in self.parent.current_path:
                                        self.parent.game_board.board[i].south = True
                                    self.parent.game_board.board[i].temp = True
                                    self.parent.game_board.board[i].path = True
                                    self.played_event = True
            elif self.parent.current_event == 'event_keep':
                print('event_keep')
                self.played_event = True
            elif self.parent.current_event == 'event_merge':
                print('event_merge')
                if len(self.parent.drawn_cards_path) >= 2 and Deck.not_all_duplicate(self.parent.drawn_cards_path):
                    for event in events:
                        self.mouse_pos = pygame.mouse.get_pos()
                        cell_pos = -1
                        for i, rect in enumerate(self.parent.grid_hitboxes):
                            if rect.collidepoint(self.mouse_pos):
                                self.cell_pos = i
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if self.selected_cell is None:
                                        if self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                                            self.selected_cell = i
                                    else:
                                        if (i != self.selected_cell and 
                                            self.parent.game_board.board[i].path and
                                            not self.parent.game_board.board[i].home and
                                            not self.parent.game_board.board[i].would_be_same(self.parent.game_board.board[self.selected_cell])):
                                            
                                            self.parent.game_board.board[i].combine_directions(self.parent.game_board.board[self.selected_cell])
                                            self.parent.game_board.board[self.selected_cell].north = False
                                            self.parent.game_board.board[self.selected_cell].west = False
                                            self.parent.game_board.board[self.selected_cell].east = False
                                            self.parent.game_board.board[self.selected_cell].south = False
                                            self.parent.game_board.board[self.selected_cell].path = False
                                            self.selected_cell = None
                                            self.played_event = True
                                        elif i == self.selected_cell:
                                            self.selected_cell = None
                else:
                    print("No merge possible")
                    self.played_event = True
                                    
            elif self.parent.current_event == 'event_point':
                print('event_point')
                self.played_event = True
            elif self.parent.current_event == 'event_redraw':
                print('event_redraw')
                self.played_event = True
            elif self.parent.current_event == 'event_remove':
                print('event_remove')
                self.played_event = True
            elif self.parent.current_event == 'event_reveal':
                print('event_reveal')
                self.played_event = True
            elif self.parent.current_event == 'event_swap':
                print('event_swap')
                self.played_event = True
            else: # for any bug
                print(f"There is no such event {self.parent.current_event}")
                self.played_event = True
        else:
            if self.parent.strikes >= 3:
                            self.parent.is_3_strike = True
                            self.parent.strikes = 0
            else:
                self.parent.drawing = True
            print("exiting play event")
            self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.selecting_path:
            utils.draw_rect(dest=canvas,
                                    size=(self.box_width, self.box_height),
                                    pos=(self.parent.box_width - 4, constants.canvas_height - self.box_height),
                                    pos_anchor='topleft',
                                    color=(*colors.white, 191), # 75% transparency
                                    inner_border_width=4,
                                    outer_border_width=0,
                                    outer_border_color=colors.black)
            
            utils.blit(dest=canvas, source=self.path_WE_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 320), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NS_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 262), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NW_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 204), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NE_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 146), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_WS_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 88), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_ES_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 30), pos_anchor='center')

        if self.cell_pos >= 0:
            utils.blit(dest=canvas, source=self.selecting_tile, pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')

        if self.selected_cell:
            utils.blit(dest=canvas, source=self.selecting_tile, pos=(self.parent.grid_start_x + ((self.selected_cell % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell // 8) * self.parent.cell_size)), pos_anchor='topleft')