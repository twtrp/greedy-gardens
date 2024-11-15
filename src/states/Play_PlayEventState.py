from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.Deck import Deck
from src.classes.Cell import Cell

class Play_PlayEventState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("playing event")

        # value
        self.box_width = 68
        self.box_height = 352

        self.cell_pos = -1

        self.button_list = []

        self.choice = 0
        self.choices = ['path_WE', 'path_NS', 'path_NW', 'path_NE', 'path_WS', 'path_ES']

        # state
        self.played_event = False
        self.selecting_path = False
        self.selected_cell = None
        self.choosing = False

        self.load_assets()

    def load_assets(self):
        # Load text
        self.choice_title = utils.get_text(text='choose', font=fonts.lf2, size='large', color=colors.mono_175)

        # Load Button
        self.point_button_option_list = [
            {
                'id': 'add today',
                'text1': 'Get 1 point today,',
                'text2': 'Lose 1 point next day',
            },
            {
                'id': 'lose today',
                'text1': 'Lose 1 point today,',
                'text2': 'Get 1 point next day',
            }
        ]
        self.point_button_option_surface_list = []
        for i, option in enumerate(self.point_button_option_list):
            text1 = utils.get_text(text=option['text1'], font=fonts.lf2, size='medium', color=colors.white)
            text2 = utils.get_text(text=option['text2'], font=fonts.lf2, size='medium', color=colors.white)
            self.point_button_option_surface_list.append({
                'id': option['id'],
                'surface1': text1,
                'surface2': text2,
                'scale': 1.0
            })
            self.button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=400,
                height=95,
                pos=(constants.canvas_width/2, 290 + (i*2)*75),
                pos_anchor=posanchors.center
            ))

        # Load image/sprite
        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')

        self.small_selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='small_selecting_tile')
        self.path_WE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE')
        self.path_NS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS')
        self.path_NW_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW')
        self.path_NE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE')
        self.path_WS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS')
        self.path_ES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES')

    def update(self, dt, events):
        # Each event
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
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_w and self.choice > 0:
                                    self.choice -= 1
                                elif event.key == pygame.K_s and self.choice < 5:
                                    self.choice += 1
                            if not self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                                self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if "N" in self.choices[self.choice]:
                                        self.parent.game_board.board[i].north = True
                                    if "W" in self.choices[self.choice]:
                                        self.parent.game_board.board[i].west = True 
                                    if "E" in self.choices[self.choice]:
                                        self.parent.game_board.board[i].east = True
                                    if "S" in self.choices[self.choice]:
                                        self.parent.game_board.board[i].south = True
                                    self.parent.game_board.board[i].temp = True
                                    self.parent.game_board.board[i].path = True
                                    self.played_event = True
                            else:
                                self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')

            elif self.parent.current_event == 'event_keep':
                print('event_keep')
                self.played_event = True

            elif self.parent.current_event == 'event_merge':
                # print('event_merge')
                if len(self.parent.drawn_cards_path) >= 2 and Deck.not_all_duplicate(self.parent.drawn_cards_path):
                    for event in events:
                        self.mouse_pos = pygame.mouse.get_pos()
                        cell_pos = -1
                        for i, rect in enumerate(self.parent.grid_hitboxes):
                            if rect.collidepoint(self.mouse_pos):
                                self.cell_pos = i
                                if self.selected_cell is None:
                                    if self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            self.selected_cell = i
                                    else:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')
                                else:
                                    if (i != self.selected_cell and
                                        self.parent.game_board.board[i].path and
                                        not self.parent.game_board.board[i].home and
                                        not self.parent.game_board.board[i].would_be_same(self.parent.game_board.board[self.selected_cell])):
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')   
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            self.parent.game_board.board[i].combine_directions(self.parent.game_board.board[self.selected_cell])
                                            self.parent.game_board.board[self.selected_cell].north = False
                                            self.parent.game_board.board[self.selected_cell].west = False
                                            self.parent.game_board.board[self.selected_cell].east = False
                                            self.parent.game_board.board[self.selected_cell].south = False
                                            self.parent.game_board.board[self.selected_cell].path = False
                                            self.selected_cell = None
                                            self.played_event = True
                                    elif i == self.selected_cell:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            self.selected_cell = None
                                    else:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')
                else:
                    print("No merge possible")
                    self.played_event = True
                                    
            elif self.parent.current_event == 'event_point':
                # print('event_point')
                self.choosing = True
                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    
                    if button.hovered:
                        if button.hover_cursor is not None:
                            self.cursor = button.hover_cursor

                        for option in self.point_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = min(option['scale'] + 2.4*dt, 1.2)

                    else:
                        for option in self.point_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

                    if button.clicked:
                        if button.id == 'add today':
                            print(f'adding score day {self.parent.current_day}')
                            utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                            setattr(self.parent, f'day{self.parent.current_day}_score', getattr(self.parent, f'day{self.parent.current_day}_score') + 1)
                            if (self.parent.current_day < self.parent.day):
                                setattr(self.parent, f'day{self.parent.current_day + 1}_score', getattr(self.parent, f'day{self.parent.current_day + 1}_score') - 1)
                            self.choosing = False
                            self.played_event = True

                        elif button.id == 'lose today':
                            print(f'losing score day {self.parent.current_day}')
                            utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                            setattr(self.parent, f'day{self.parent.current_day}_score', getattr(self.parent, f'day{self.parent.current_day}_score') - 1)
                            if (self.parent.current_day < self.parent.day):
                                setattr(self.parent, f'day{self.parent.current_day + 1}_score', getattr(self.parent, f'day{self.parent.current_day + 1}_score') + 1)
                            self.choosing = False
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
                if len(self.parent.drawn_cards_path) >= 2 and Deck.not_all_duplicate(self.parent.drawn_cards_path):
                    for event in events:
                        self.mouse_pos = pygame.mouse.get_pos()
                        cell_pos = -1
                        for i, rect in enumerate(self.parent.grid_hitboxes):
                            if rect.collidepoint(self.mouse_pos):
                                self.cell_pos = i
                                if self.selected_cell is None:
                                    if self.parent.game_board.board[i].path and not self.parent.game_board.board[i].home:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            self.selected_cell = i
                                    else:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')
                                else:
                                    if (i != self.selected_cell and 
                                        self.parent.game_board.board[i].path and
                                        not self.parent.game_board.board[i].home and
                                        not self.parent.game_board.board[i].is_the_same(self.parent.game_board.board[self.selected_cell])):
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            Cell.swap_path(self.parent.game_board.board[i], self.parent.game_board.board[self.selected_cell])
                                            self.selected_cell = None
                                            self.played_event = True
                                    elif i == self.selected_cell:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
                                        if event.type == pygame.MOUSEBUTTONDOWN:    
                                            self.selected_cell = None
                                    else:
                                        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile')
                else:
                    print("No swap possible")
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
        if self.choosing:
            utils.draw_rect(dest=canvas,
                                    size=(constants.canvas_width - 2*self.parent.box_width, constants.canvas_height),
                                    pos=(self.parent.box_width, 0),
                                    pos_anchor='topleft',
                                    color=(*colors.black, 128), # 50% transparency
                                    inner_border_width=0,
                                    outer_border_width=0,
                                    outer_border_color=colors.black)
            
            utils.blit(dest=canvas, source=self.choice_title, pos=(constants.canvas_width/2, 180), pos_anchor=posanchors.center)
            for i, option in enumerate(self.point_button_option_surface_list):
                scaled_point_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
                utils.blit(dest=canvas, source=scaled_point_button, pos=(constants.canvas_width/2, 265 + (i*2)*75), pos_anchor=posanchors.center)
                scaled_point_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
                utils.blit(dest=canvas, source=scaled_point_button, pos=(constants.canvas_width/2, 315 + (i*2)*75), pos_anchor=posanchors.center)
            
            # # show button hit box
            # for button in self.button_list:
            #     button.render(canvas)

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
            utils.blit(dest=canvas, source=self.small_selecting_tile, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 320 + 58*self.choice), pos_anchor='center')

        if self.cell_pos >= 0:
            utils.blit(dest=canvas, source=self.selecting_tile, pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')

        if self.selected_cell:
            utils.blit(dest=canvas, source=self.selecting_tile, pos=(self.parent.grid_start_x + ((self.selected_cell % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell // 8) * self.parent.cell_size)), pos_anchor='topleft')