from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.Deck import Deck
from src.classes.Cards import Cards
from src.classes.Cell import Cell


class Play_PlayEventState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        # print("playing event")

        # value
        self.box_width = 60
        self.box_height = 352

        self.cell_pos = -1

        self.button_list = []

        self.choice = 0
        self.choices = ['path_WE', 'path_NS', 'path_NW', 'path_NE', 'path_WS', 'path_ES']

        # state
        self.played_event = False
        self.selecting_path = False
        self.selected_cell = None
        self.selected_cell_2 = None
        if (self.parent.current_event == 'event_point' or
            self.parent.current_event == 'event_redraw' or
            self.parent.current_event == 'event_reveal'):
            self.choosing = True
            utils.sound_play(sound=sfx.appear, volume=self.game.sfx_volume)
        else:
            self.choosing = False
        self.drawn_move = False

        self.card_path1_image = None
        self.card_path2_image = None
        self.fruit_drawn_image = None

        self.select_frame = self.parent.selecting_tile

        # event redraw
        self.fruit_drawn_image_props = {
            'x': 1080,
            'y': 130,
            'scale': 1,
        }

        # event move
        self.card_path1_image_scale = 1
        self.card_path2_image_scale = 1

        self.load_assets()

    def load_assets(self):
        # Load text
        self.choice_point_title = utils.get_text(text='Choose', font=fonts.wacky_pixels, size='medium', color=colors.mono_205)
        self.choice_redraw_title = utils.get_text(text='Choose a fruit to redraw', font=fonts.wacky_pixels, size='medium', color=colors.mono_205)
        self.remaining_fruits_title = utils.get_text(text='Remaining Fruits', font=fonts.windows, size='smaller', color=colors.mono_205)
        self.hover_to_view_title = utils.get_text(text='Hover here to view board', font=fonts.lf2, size='small', color=colors.yellow_light)
        self.hover_to_view_surface = [{
                    'id': 'view board',
                    'surface': self.hover_to_view_title,
                    'scale': 1.0,
                },]
        
        # Load Button
        self.button_list.append(Button(
                    game=self.game,
                    id='view board',
                    width=600,
                    height=50,
                    pos=(constants.canvas_width/2, 695),
                    pos_anchor=posanchors.center,
                    hover_cursor=cursors.normal
                ))
        if self.parent.current_event == 'event_point':
            if self.parent.current_day < self.parent.day:
                self.point_button_option_list = [
                    {
                        'id': 'add today',
                        'text1': '+1 point today,',
                        'text2': '-1 point tomorrow',
                    },
                    {
                        'id': 'lose today',
                        'text1': '-1 point today,',
                        'text2': '+1 point tomorrow',
                    },
                ]
            else:
                self.point_button_option_list = [
                    {
                        'id': 'add today',
                        'text1': '+1 point today',
                        'text2': '',
                    },
                ]
            self.point_button_option_surface_list = []
            for i, option in enumerate(self.point_button_option_list):
                text1 = utils.get_text(text=option['text1'], font=fonts.lf2, size='medium', color=colors.white)
                # Only create text2 surface if text2 is not empty
                if option['text2'].strip():  # Check if text2 has actual content
                    text2 = utils.get_text(text=option['text2'], font=fonts.lf2, size='medium', color=colors.white)
                else:
                    text2 = None
                self.point_button_option_surface_list.append({
                    'id': option['id'],
                    'surface1': text1,
                    'surface2': text2,
                    'scale': 1.0
                })
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=600,
                    height=100,
                    pos=(constants.canvas_width/2, constants.canvas_height/2 - 75 + i*150),
                    pos_anchor=posanchors.center
                ))
        elif self.parent.current_event == 'event_redraw':
            self.redraw_button_option_list = []
            if not self.parent.current_day < self.parent.day:
                self.redraw_button_option_list.append({
                    'id': 'dummy',
            })
            self.redraw_button_option_list.append({
                'id': 'today fruit',
                'text': f'Day {self.parent.current_day}',
                'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
            })
            if self.parent.current_day < self.parent.day:
                self.redraw_button_option_list.append({
                    'id': 'tomorrow fruit',
                    'text': f'Day {self.parent.current_day + 1}',
                    'fruit': getattr(self.parent, f'day{self.parent.current_day + 1}_fruit'),
                })
            self.redraw_button_option_list.append({
                'id': 'seasonal fruit',
                'text': 'Seasonal',
                'fruit': self.parent.seasonal_fruit,
            })
            self.redraw_button_option_list.append({
                'id': 'do nothing',
                'text': 'Do Nothing',
                'fruit': 'nothing',
            })
            self.redraw_button_option_surface_list = []
            visual_index = 0  # Track visual position independent of list index
            for i, option in enumerate(self.redraw_button_option_list):
                if option['id'] == 'dummy':
                    self.redraw_button_option_surface_list.append({
                        'id': 'dummy',
                        'surface': None,
                        'surface_fruit': None,
                        'scale': 1.0,
                        'scale_fruit': 3.0
                    })
                    continue
                text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
                fruit = self.parent.fruit_sprites[option['fruit']]
                self.redraw_button_option_surface_list.append({
                    'id': option['id'],
                    'surface': text,
                    'surface_fruit': fruit,
                    'scale': 1.0,
                    'scale_fruit': 3.0
                })
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=600,
                    height=50,
                    pos=(constants.canvas_width/2, 265 + visual_index*75),  # Use visual_index instead of i
                    pos_anchor=posanchors.center
                ))
                visual_index += 1  # Increment only for non-dummy entries
            
            # Create shuffled remaining fruits display for redraw event
            remaining_fruits = self.parent.deck_fruit.cards.copy()
            random.shuffle(remaining_fruits)
            self.remaining_fruits_display = remaining_fruits[:6]  # Show first 6 fruits
        elif self.parent.current_event == 'event_remove':
            self.remove_button_option_list = [
                {
                    'id': 'remove',
                    'text': 'Delete',
                    'color1': colors.mono_175,
                    'color2': colors.white,
                },
            ]
            self.remove_button_option_surface_list = []
            for i, option in enumerate(self.remove_button_option_list):
                text1 = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=option['color1'])
                text2 = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=option['color2'])
                self.remove_button_option_surface_list.append({
                    'id': option['id'],
                    'surface1': text1,
                    'surface2': text2,
                    'scale': 1.0
                })
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=200,
                    height=40,
                    pos=(constants.canvas_width/2, 690),
                    pos_anchor=posanchors.center
                ))

        elif self.parent.current_event == 'event_reveal':
            self.reveal_button_option_list = [
                {
                    'id': 'reveal path',
                    'text': 'Reveal next 3 path cards',
                },
                {
                    'id': 'reveal event',
                    'text': 'Reveal next 4 event cards',
                },
            ]
            self.reveal_button_option_surface_list = []
            for i, option in enumerate(self.reveal_button_option_list):
                text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
                self.reveal_button_option_surface_list.append({
                    'id': option['id'],
                    'surface': text,
                    'scale': 1.0
                })
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=600,
                    height=50,
                    pos=(constants.canvas_width/2, constants.canvas_height/2 - 50 + i*100),
                    pos_anchor=posanchors.center
                ))
            
        # Load image/sprite
        self.selected_tile = self.parent.selected_tile
        self.small_selecting_tile = self.parent.small_selecting_tile
        self.path_WE_image = self.parent.path_WE_image
        self.path_NS_image = self.parent.path_NS_image
        self.path_NW_image = self.parent.path_NW_image
        self.path_NE_image = self.parent.path_NE_image
        self.path_WS_image = self.parent.path_WS_image
        self.path_ES_image = self.parent.path_ES_image

    def update(self, dt, events):
        # Each event
        if not self.played_event:
            if self.parent.current_event == 'event_free':
                # print('event_free')
                self.selecting_path = True

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if (event.key == pygame.K_w or event.key == pygame.K_UP) and self.choice > 0:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.choice -= 1
                        elif (event.key == pygame.K_s or event.key == pygame.K_DOWN) and self.choice < 5:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.choice += 1
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4 and self.choice > 0:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.choice -= 1
                        elif event.button == 5 and self.choice < 5:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.choice += 1

                self.cell_pos = -1
                for button in self.parent.grid_buttons:
                    if button.hovered:
                        self.cursor = cursors.dig
                        self.cell_pos = button.id
                        if not self.parent.game_board.board[button.id].path and not self.parent.game_board.board[button.id].home:
                            self.select_frame = self.parent.selecting_tile
                            if button.clicked:
                                utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                if "N" in self.choices[self.choice]:
                                    self.parent.game_board.board[button.id].north = True
                                if "W" in self.choices[self.choice]:
                                    self.parent.game_board.board[button.id].west = True 
                                if "E" in self.choices[self.choice]:
                                    self.parent.game_board.board[button.id].east = True
                                if "S" in self.choices[self.choice]:
                                    self.parent.game_board.board[button.id].south = True
                                self.parent.game_board.board[button.id].temp = True
                                self.parent.game_board.board[button.id].path = True
                                self.check_magic_fruit_collection(button)
                                self.played_event = True
                        else:
                            self.select_frame = self.parent.cant_selecting_tile

            elif self.parent.current_event == 'event_move':
                # print('event_move')
                # Check if there are any paths on the board to move
                if any(cell.path and not cell.home for cell in self.parent.game_board.board):
                    self.cell_pos = -1
                    for button in self.parent.grid_buttons:
                        if button.hovered:
                            self.cursor = button.hover_cursor
                            self.cell_pos = button.id
                            if self.selected_cell is None:
                                # First selection: must be a path (not home)
                                if self.parent.game_board.board[button.id].path and not self.parent.game_board.board[button.id].home:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                        self.selected_cell = button.id
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                            else:
                                # Second selection: must be a blank tile
                                if not self.parent.game_board.board[button.id].path:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        # Move the path from selected_cell to current button.id
                                        source_cell = self.parent.game_board.board[self.selected_cell]
                                        target_cell = self.parent.game_board.board[button.id]
                                        
                                        # Copy path data to target
                                        target_cell.north = source_cell.north
                                        target_cell.south = source_cell.south
                                        target_cell.east = source_cell.east
                                        target_cell.west = source_cell.west
                                        target_cell.path = source_cell.path
                                        target_cell.path_type = source_cell.path_type
                                        target_cell.temp = source_cell.temp
                                        
                                        # Clear source cell
                                        source_cell.north = False
                                        source_cell.south = False
                                        source_cell.east = False
                                        source_cell.west = False
                                        source_cell.path = False
                                        source_cell.path_type = None
                                        source_cell.temp = False
                                        
                                        self.check_magic_fruit_collection(button)
                                        self.selected_cell = None
                                        self.played_event = True
                                elif button.id == self.selected_cell:
                                    # Deselect if clicking the same cell
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                        self.selected_cell = None
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                else:
                    # No paths to move
                    self.played_event = True

            elif self.parent.current_event == 'event_merge':
                # print('event_merge')
                if len(self.parent.drawn_cards_path) >= 2 and Deck.not_all_duplicate(self.parent.drawn_cards_path):

                    self.cell_pos = -1
                    for button in self.parent.grid_buttons:
                        if button.hovered:
                            self.cursor = button.hover_cursor
                            self.cell_pos = button.id
                            if self.selected_cell is None:
                                if (self.parent.game_board.board[button.id].path and 
                                    not self.parent.game_board.board[button.id].temp and
                                    not self.parent.game_board.board[button.id].home):
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                        self.selected_cell = button.id
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                            else:
                                if (button.id != self.selected_cell and
                                    self.parent.game_board.board[button.id].path and
                                    not self.parent.game_board.board[button.id].temp and
                                    not self.parent.game_board.board[button.id].home and
                                    not self.parent.game_board.board[button.id].would_be_same(self.parent.game_board.board[self.selected_cell])):
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        # print("clicked")
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        old_path1 = ""
                                        if self.parent.game_board.board[button.id].north:
                                            old_path1 += "N"
                                        if self.parent.game_board.board[button.id].west:
                                            old_path1 += "W"
                                        if self.parent.game_board.board[button.id].east:
                                            old_path1 += "E"
                                        if self.parent.game_board.board[button.id].south:
                                            old_path1 += "S"
                                        old_path2 = ""
                                        if self.parent.game_board.board[self.selected_cell].north:
                                            old_path2 += "N"
                                        if self.parent.game_board.board[self.selected_cell].west:
                                            old_path2 += "W"
                                        if self.parent.game_board.board[self.selected_cell].east:
                                            old_path2 += "E"
                                        if self.parent.game_board.board[self.selected_cell].south:
                                            old_path2 += "S"
                                        self.parent.game_board.board[button.id].combine_directions(self.parent.game_board.board[self.selected_cell])
                                        new_path = "path_"
                                        if self.parent.game_board.board[button.id].north:
                                            new_path += "N"
                                        if self.parent.game_board.board[button.id].west:
                                            new_path += "W"
                                        if self.parent.game_board.board[button.id].east:
                                            new_path += "E"
                                        if self.parent.game_board.board[button.id].south:
                                            new_path += "S"
                                        self.parent.game_board.board[self.selected_cell].north = False
                                        self.parent.game_board.board[self.selected_cell].west = False
                                        self.parent.game_board.board[self.selected_cell].east = False
                                        self.parent.game_board.board[self.selected_cell].south = False
                                        self.parent.game_board.board[self.selected_cell].path = False
                                        for n in range(len(self.parent.drawn_cards_path)-1, -1, -1):  
                                            if old_path1 in self.parent.drawn_cards_path[n].card_name:
                                                self.parent.drawn_cards_path.pop(n)  
                                                break
                                        for m in range(len(self.parent.drawn_cards_path)-1, -1, -1):  
                                            if old_path2 in self.parent.drawn_cards_path[m].card_name:
                                                self.parent.drawn_cards_path.pop(m)  
                                                break
                                        self.parent.drawn_cards_path.append(Cards("path", new_path, False))
                                        self.check_magic_fruit_collection(button)
                                        self.selected_cell = None
                                        self.played_event = True
                                elif button.id == self.selected_cell:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                        self.selected_cell = None
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile

                else:
                    # print("No merge possible")
                    self.show_event_cancelled_popup()
                    self.played_event = True
                                    
            elif self.parent.current_event == 'event_point':
                # print('event_point')
                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    if button.hovered:
                        if button.id == 'view board':
                            self.choosing = False
                        if button.id != 'do nothing':
                            if button.hover_cursor is not None:
                                self.cursor = button.hover_cursor
                            for option in self.point_button_option_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                    else:
                        if button.id == 'view board':
                                self.choosing = True
                        for option in self.point_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                    if button.clicked:
                        if button.id == 'add today':
                            # print(f'adding score day {self.parent.current_day}')
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            setattr(self.parent, f'day{self.parent.current_day}_score', getattr(self.parent, f'day{self.parent.current_day}_score') + 1)
                            if (self.parent.current_day < self.parent.day):
                                setattr(self.parent, f'day{self.parent.current_day + 1}_score', getattr(self.parent, f'day{self.parent.current_day + 1}_score') - 1)
                            self.choosing = False
                            self.played_event = True
                        elif button.id == 'lose today':
                            # print(f'losing score day {self.parent.current_day}')
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            setattr(self.parent, f'day{self.parent.current_day}_score', getattr(self.parent, f'day{self.parent.current_day}_score') - 1)
                            if (self.parent.current_day < self.parent.day):
                                setattr(self.parent, f'day{self.parent.current_day + 1}_score', getattr(self.parent, f'day{self.parent.current_day + 1}_score') + 1)
                            self.choosing = False
                            self.played_event = True

            elif self.parent.current_event == 'event_redraw':
                # print('event_redraw')
                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    if not self.fruit_drawn_image:
                        if button.hovered:
                            if button.id == 'view board':
                                self.choosing = False
                            if button.hover_cursor is not None:
                                self.cursor = button.hover_cursor
                            for option in self.redraw_button_option_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                                    option['scale_fruit'] = min(option['scale_fruit'] + 7.2*dt, 3.6)
                        else:
                            if button.id == 'view board':
                                    self.choosing = True
                            for option in self.redraw_button_option_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                                    option['scale_fruit'] = max(option['scale_fruit'] - 7.2*dt, 3.0)
                    if button.clicked and self.choosing:
                        if not button.id == 'do nothing':
                            self.fruit_drawn_image_props = {
                                'x': 1080,
                                'y': 130,
                                'scale': 1,
                            }
                            def on_complete():
                                self.parent.tween_list.clear()
                            utils.multitween(
                                tween_list=self.parent.tween_list,
                                container=self.fruit_drawn_image_props,
                                keys=['x', 'y', 'scale'],
                                end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                                time=0.4,
                                ease_type=tweencurves.easeOutQuart,
                                on_complete=on_complete
                            )

                        random.seed(self.parent.seed)
                            
                        if button.id == 'today fruit':
                            # print('redraw today fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            if self.card_drawn:
                                old_fruit = getattr(self.parent, f'day{self.parent.current_day}_fruit')
                                # Delay assignment until card dismissed
                                self.pending_assignment = {
                                    'attr': f'day{self.parent.current_day}_fruit',
                                    'card': self.card_drawn,
                                    'old_fruit': old_fruit,
                                    'append_to_deck': True,
                                    'drawn_list': 'fruit'
                                }
                                self.fruit_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                                self.choosing = False
                                self.parent.is_current_task_event = False
                                self.parent.drawing_path_card = True
                        elif button.id == 'tomorrow fruit':
                            # print('redraw tomorrow fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            if self.card_drawn:
                                old_fruit = getattr(self.parent, f'day{self.parent.current_day + 1}_fruit')
                                # Delay assignment until card dismissed
                                self.pending_assignment = {
                                    'attr': f'day{self.parent.current_day + 1}_fruit',
                                    'card': self.card_drawn,
                                    'old_fruit': old_fruit,
                                    'append_to_deck': True,
                                    'drawn_list': 'fruit'
                                }
                                self.fruit_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                                self.choosing = False
                                self.parent.is_current_task_event = False
                                self.parent.drawing_path_card = True
                        elif button.id == 'seasonal fruit':
                            # print('redraw seasonal fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            if self.card_drawn:
                                old_fruit = self.parent.seasonal_fruit
                                # Delay assignment until card dismissed
                                self.pending_assignment = {
                                    'attr': 'seasonal_fruit',
                                    'card': self.card_drawn,
                                    'old_fruit': old_fruit,
                                    'append_to_deck': True,
                                    'drawn_list': 'fruit'
                                }
                                self.fruit_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                                self.choosing = False
                                self.parent.is_current_task_event = False
                                self.parent.drawing_path_card = True
                        elif button.id == 'do nothing':
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.choosing = False
                            self.played_event = True
                if self.fruit_drawn_image:
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                # Commit any pending assignment before finishing
                                if hasattr(self, 'pending_assignment') and self.pending_assignment:
                                    pa = self.pending_assignment
                                    setattr(self.parent, pa['attr'], pa['card'].card_name)
                                    if pa.get('append_to_deck') and pa.get('old_fruit') is not None:
                                        self.parent.deck_fruit.cards.append(Cards('fruit', pa['old_fruit'], False))
                                        random.shuffle(self.parent.deck_fruit.cards)
                                    if pa.get('drawn_list') == 'fruit' and pa.get('card') is not None:
                                        self.parent.drawn_cards_fruit.append(pa['card'])
                                    # clear pending
                                    self.pending_assignment = None
                                self.played_event = True
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 3:  # Right click
                                # Commit any pending assignment before finishing
                                if hasattr(self, 'pending_assignment') and self.pending_assignment:
                                    pa = self.pending_assignment
                                    setattr(self.parent, pa['attr'], pa['card'].card_name)
                                    if pa.get('append_to_deck') and pa.get('old_fruit') is not None:
                                        self.parent.deck_fruit.cards.append(Cards('fruit', pa['old_fruit'], False))
                                        random.shuffle(self.parent.deck_fruit.cards)
                                    if pa.get('drawn_list') == 'fruit' and pa.get('card') is not None:
                                        self.parent.drawn_cards_fruit.append(pa['card'])
                                    # clear pending
                                    self.pending_assignment = None
                                self.played_event = True

            elif self.parent.current_event == 'event_remove':
                # print('event_remove')
                self.cell_pos = -1
                for button in self.parent.grid_buttons:
                    if button.hovered:
                        self.cursor = button.hover_cursor
                        self.cell_pos = button.id
                        if self.selected_cell is None:
                            if (button.id != self.selected_cell_2 and
                                self.parent.game_board.board[button.id].path and 
                                not self.parent.game_board.board[button.id].home):
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                    self.selected_cell = button.id
                            elif button.id == self.selected_cell_2:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                    self.selected_cell_2 = None
                            else:
                                self.select_frame = self.parent.cant_selecting_tile
                        elif self.selected_cell_2 is None:
                            if (button.id != self.selected_cell and 
                                self.parent.game_board.board[button.id].path and
                                not self.parent.game_board.board[button.id].home):
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                    self.selected_cell_2 = button.id
                            elif button.id == self.selected_cell:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                    self.selected_cell = None
                            else:
                                self.select_frame = self.parent.cant_selecting_tile
                        else:
                            if button.id == self.selected_cell:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                    self.selected_cell = None
                            elif button.id == self.selected_cell_2:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                    self.selected_cell_2 = None
                            else:
                                self.select_frame = self.parent.cant_selecting_tile

                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    if button.hovered:
                        for option in self.remove_button_option_surface_list:
                            if (self.selected_cell is not None) or (self.selected_cell_2 is not None):
                                if button.hover_cursor is not None:
                                    self.cursor = button.hover_cursor
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                    else:
                        for option in self.remove_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                    if button.clicked:
                        if (self.selected_cell is not None) or (self.selected_cell_2 is not None):
                            if button.id == 'remove':
                                utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                if self.selected_cell is not None:
                                    if not self.parent.game_board.board[self.selected_cell].temp:
                                        old_path1 = ""
                                        if self.parent.game_board.board[self.selected_cell].north:
                                            old_path1 += "N"
                                        if self.parent.game_board.board[self.selected_cell].west:
                                            old_path1 += "W"
                                        if self.parent.game_board.board[self.selected_cell].east:
                                            old_path1 += "E"
                                        if self.parent.game_board.board[self.selected_cell].south:
                                            old_path1 += "S"
                                        for n in range(len(self.parent.drawn_cards_path)-1, -1, -1):  
                                            if old_path1 in self.parent.drawn_cards_path[n].card_name:
                                                self.parent.drawn_cards_path.pop(n)  
                                                break
                                    self.parent.game_board.board[self.selected_cell].north = False
                                    self.parent.game_board.board[self.selected_cell].west = False
                                    self.parent.game_board.board[self.selected_cell].east = False
                                    self.parent.game_board.board[self.selected_cell].south = False
                                    self.parent.game_board.board[self.selected_cell].path = False
                                    self.parent.game_board.board[self.selected_cell].temp = False
                                if self.selected_cell_2 is not None:
                                    if not self.parent.game_board.board[self.selected_cell_2].temp:
                                        old_path2 = ""
                                        if self.parent.game_board.board[self.selected_cell_2].north:
                                            old_path2 += "N"
                                        if self.parent.game_board.board[self.selected_cell_2].west:
                                            old_path2 += "W"
                                        if self.parent.game_board.board[self.selected_cell_2].east:
                                            old_path2 += "E"
                                        if self.parent.game_board.board[self.selected_cell_2].south:
                                            old_path2 += "S"
                                        for m in range(len(self.parent.drawn_cards_path)-1, -1, -1):  
                                            if old_path2 in self.parent.drawn_cards_path[m].card_name:
                                                self.parent.drawn_cards_path.pop(m)  
                                                break
                                    self.parent.game_board.board[self.selected_cell_2].north = False
                                    self.parent.game_board.board[self.selected_cell_2].west = False
                                    self.parent.game_board.board[self.selected_cell_2].east = False
                                    self.parent.game_board.board[self.selected_cell_2].south = False
                                    self.parent.game_board.board[self.selected_cell_2].path = False
                                    if self.selected_cell_2 is not None:
                                        self.parent.game_board.board[self.selected_cell_2].temp = False
                                # print(self.parent.drawn_cards_path)
                                self.played_event = True
                                

            elif self.parent.current_event == 'event_reveal':
                # print('event_reveal')
                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    if button.hovered:
                        if button.id == 'view board':
                                self.choosing = False
                        for option in self.reveal_button_option_surface_list:
                            if button.hover_cursor is not None:
                                self.cursor = button.hover_cursor
                            if button.id == option['id']:
                                option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                    else:
                        if button.id == 'view board':
                                self.choosing = True
                        for option in self.reveal_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                    if button.clicked:
                        if button.id == 'reveal path':
                            self.choosing = False
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.parent.revealed_path = copy.deepcopy(self.parent.deck_path.cards[-3:])
                            for card in self.parent.revealed_path:
                                if "strike_" in card.card_name:
                                    card.card_name = card.card_name.replace("strike_", "")
                            # print(self.parent.revealed_path)
                            self.played_event = True
                        if button.id == 'reveal event':
                            self.choosing = False
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.parent.revealed_event = self.parent.deck_event.cards[-4:]
                            # print(self.parent.revealed_event)
                            # Update buttons for revealed event cards
                            # Remove existing revealed event buttons
                            self.parent.button_list = [btn for btn in self.parent.button_list if not btn.id.startswith('revealed_event_individual_')]
                            
                            # Add new buttons for each revealed event card with larger hitboxes to eliminate gaps
                            for i, card in enumerate(self.parent.revealed_event):
                                # Create a larger invisible surface for better hover detection
                                button_surface = pygame.Surface((self.parent.revealed_event_button_width, self.parent.revealed_event_button_height), pygame.SRCALPHA)
                                button_x = constants.canvas_width - self.parent.box_width - self.parent.revealed_event_button_width
                                button_y = self.parent.revealed_event_button_y_base + i * self.parent.revealed_event_button_y_spacing
                                self.parent.button_list.append(Button(
                                    game=self.parent.game,
                                    id=f'revealed_event_individual_{i}',
                                    surface=button_surface,  # Use larger invisible surface for hitbox
                                    pos=(button_x, button_y),
                                    pos_anchor='topleft',
                                    hover_cursor=cursors.hand,
                                ))
                            self.played_event = True
                # self.played_event = True

            elif self.parent.current_event == 'event_swap':
                # print('event_swap')
                # Allow swap if there are at least two path tiles on the board
                board_path_cells = [c for c in self.parent.game_board.board if c.path and not c.home]
                if len(board_path_cells) >= 2:

                    self.cell_pos = -1
                    for button in self.parent.grid_buttons:
                        if button.hovered:
                            self.cursor = button.hover_cursor
                            self.cell_pos = button.id
                            if self.selected_cell is None:
                                if self.parent.game_board.board[button.id].path and not self.parent.game_board.board[button.id].home:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                        self.selected_cell = button.id
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                            else:
                                if (button.id != self.selected_cell and
                                    self.parent.game_board.board[button.id].path and
                                    not self.parent.game_board.board[button.id].home and
                                    not self.parent.game_board.board[button.id].is_the_same(self.parent.game_board.board[self.selected_cell])):
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume, pitch_variation=0.15)
                                        Cell.swap_path(self.parent.game_board.board[button.id], self.parent.game_board.board[self.selected_cell])
                                        self.check_magic_fruit_collection(button)
                                        self.selected_cell = None
                                        self.played_event = True
                                elif button.id == self.selected_cell:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.unclick, volume=self.game.sfx_volume)
                                        self.selected_cell = None
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                else:
                    self.show_event_cancelled_popup()
                    self.played_event = True

            else: # for any bug
                # print(f"There is no such event {self.parent.current_event}")
                self.played_event = True
        else:
            if self.parent.strikes >= 3:
                self.parent.is_3_strike = True
                self.parent.strikes = 0
            else:
                self.parent.drawing = True
            self.parent.current_event = None
            # print("exiting play event")
            self.parent.play_event_state= False
            self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):

        # show button hit box
        # for button in self.button_list:
        #     button.render(canvas)

        if self.cell_pos >= 0:
            utils.blit(dest=canvas, source=self.select_frame, pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')


        if not self.choosing:
            self.parent.is_choosing = False
        else:
            self.parent.is_choosing = True

            scaled_point_button = pygame.transform.scale_by(surface=self.hover_to_view_surface[0]['surface'], factor=self.hover_to_view_surface[0]['scale'])
            utils.blit(dest=canvas, source=scaled_point_button, pos=(constants.canvas_width/2, 695), pos_anchor=posanchors.center)

            if self.parent.current_event == 'event_point':
                utils.blit(dest=canvas, source=self.choice_point_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                for i, option in enumerate(self.point_button_option_surface_list):
                    scaled_point_button1 = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
                    base_y = constants.canvas_height/2 - 75 + i*150
                    
                    # Check if this is a single-line option (surface2 is None)
                    if option['surface2'] is None:
                        # Single line - center it without offset
                        utils.blit(
                            dest=canvas,
                            source=scaled_point_button1,
                            pos=(constants.canvas_width/2, base_y),
                            pos_anchor=posanchors.center
                        )
                    else:
                        # Two lines - use offset positioning
                        scaled_point_button2 = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
                        offset = 30 * option['scale']
                        utils.blit(
                            dest=canvas,
                            source=scaled_point_button1,
                            pos=(constants.canvas_width/2, base_y - offset),
                            pos_anchor=posanchors.center
                        )
                        utils.blit(
                            dest=canvas,
                            source=scaled_point_button2,
                            pos=(constants.canvas_width/2, base_y + offset),
                            pos_anchor=posanchors.center
                        )

            elif self.parent.current_event == 'event_redraw':
                utils.blit(dest=canvas, source=self.choice_redraw_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                
                # Render remaining fruits display
                # Calculate surface dimensions
                title_width = self.remaining_fruits_title.get_width()
                fruit_count = len(self.remaining_fruits_display)
                fruit_width = fruit_count * 40 - 20  # Total width of all fruits (subtract 20 because last fruit doesn't need spacing)
                total_width = title_width + 30 + fruit_width  # 30px gap between title and fruits
                total_height = max(self.remaining_fruits_title.get_height(), 32) + 4  # Height of scaled fruit is 32px
                
                # Create surface for the entire display
                remaining_fruits_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
                
                # Blit title to surface (moved up by 4 pixels)
                utils.blit(dest=remaining_fruits_surface, source=self.remaining_fruits_title, pos=(0, total_height/2 - 4), pos_anchor=posanchors.midleft)
                
                # Blit fruits to surface with outlines, centered relative to the fruit group
                fruits_start_x = title_width + 30
                for i, fruit in enumerate(self.remaining_fruits_display):
                    fruit_sprite = self.parent.fruit_sprites[fruit.card_name]
                    scaled_fruit = pygame.transform.scale_by(surface=fruit_sprite, factor=2.0)
                    outlined_fruit = utils.effect_outline(surface=scaled_fruit, distance=2, color=colors.mono_50)
                    utils.blit(dest=remaining_fruits_surface, source=outlined_fruit, pos=(fruits_start_x + i*40, total_height/2), pos_anchor=posanchors.center)
                
                # Blit the entire surface centered to canvas
                utils.blit(dest=canvas, source=remaining_fruits_surface, pos=(constants.canvas_width/2, 600), pos_anchor=posanchors.center)
                
                visual_index = 0  # Track visual position independent of list index
                for i, option in enumerate(self.redraw_button_option_surface_list):
                    if option['id'] == 'dummy':
                        continue
                    scaled_redraw_button = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    if option["id"] == "do nothing":
                        utils.blit(dest=canvas, source=scaled_redraw_button, pos=(constants.canvas_width/2, 265 + visual_index*75), pos_anchor=posanchors.center)
                    else:
                        # Scale the text offset with the surface scale
                        text_offset = 35 * option['scale']
                        utils.blit(dest=canvas, source=scaled_redraw_button, pos=(constants.canvas_width/2 + text_offset, 265 + visual_index*75), pos_anchor=posanchors.center)
                        scaled_fruit_image = pygame.transform.scale_by(surface=option['surface_fruit'], factor=option['scale_fruit'])
                        glow_fruit_image = utils.effect_outline(surface=scaled_fruit_image, distance=3, color=colors.mono_50)
                        if option['id'] == 'seasonal fruit':
                            # Scale the fruit offset with the fruit scale
                            fruit_offset = 540 + (540 - constants.canvas_width/2) * (option['scale_fruit'] - 3.0) / 3.0
                            utils.blit(dest=canvas, source=glow_fruit_image, pos=(fruit_offset, 265 + visual_index*75), pos_anchor='center')
                        else:
                            # Scale the fruit offset with the fruit scale  
                            fruit_offset = 570 + (570 - constants.canvas_width/2) * (option['scale_fruit'] - 3.0) / 3.0
                            utils.blit(dest=canvas, source=glow_fruit_image, pos=(fruit_offset, 265 + visual_index*75), pos_anchor='center')
                    visual_index += 1  # Increment only for non-dummy entries
                        
            elif self.parent.current_event == 'event_reveal':
                utils.blit(dest=canvas, source=self.choice_point_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                for i, option in enumerate(self.reveal_button_option_surface_list):
                    scaled_reveal_button = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    utils.blit(
                        dest=canvas,
                        source=scaled_reveal_button,
                        pos=(constants.canvas_width/2, constants.canvas_height/2 - 50 + i*100),
                        pos_anchor=posanchors.center
                    )

        if self.selected_cell is not None:
            utils.blit(dest=canvas, source=self.selected_tile, pos=(self.parent.grid_start_x + ((self.selected_cell % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell // 8) * self.parent.cell_size)), pos_anchor='topleft')
        if self.selected_cell_2 is not None:
            utils.blit(dest=canvas, source=self.selected_tile, pos=(self.parent.grid_start_x + ((self.selected_cell_2 % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell_2 // 8) * self.parent.cell_size)), pos_anchor='topleft')

        if self.parent.current_event == 'event_remove':
            utils.draw_rect(
                dest=canvas,
                size=(self.parent.event_remove_control_hint.get_width() + 20, 40),
                pos=(constants.canvas_width//2, 0),
                pos_anchor=posanchors.midtop,
                color=(*colors.white, 150),
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.event_remove_control_hint,
                pos=(constants.canvas_width//2, 2),
                pos_anchor=posanchors.midtop
            )
            for i, option in enumerate(self.remove_button_option_surface_list):
                if (self.selected_cell is not None) or (self.selected_cell_2 is not None):
                    scaled_remove_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
                else:
                    scaled_remove_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
                utils.blit(dest=canvas, source=scaled_remove_button, pos=(constants.canvas_width/2, 696), pos_anchor=posanchors.center)

        if self.parent.current_event == 'event_move':
            utils.draw_rect(
                dest=canvas,
                size=(self.parent.event_move_control_hint.get_width() + 20, 40),
                pos=(constants.canvas_width//2, 0),
                pos_anchor=posanchors.midtop,
                color=(*colors.white, 150),
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.event_move_control_hint,
                pos=(constants.canvas_width//2, 2),
                pos_anchor=posanchors.midtop
            )

        if self.parent.current_event == 'event_swap':
            utils.draw_rect(
                dest=canvas,
                size=(self.parent.event_swap_control_hint.get_width() + 20, 40),
                pos=(constants.canvas_width//2, 0),
                pos_anchor=posanchors.midtop,
                color=(*colors.white, 150),
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.event_swap_control_hint,
                pos=(constants.canvas_width//2, 2),
                pos_anchor=posanchors.midtop
            )

        if self.parent.current_event == 'event_merge':
            utils.draw_rect(
                dest=canvas,
                size=(self.parent.event_merge_control_hint.get_width() + 20, 40),
                pos=(constants.canvas_width//2, 0),
                pos_anchor=posanchors.midtop,
                color=(*colors.white, 150),
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.event_merge_control_hint,
                pos=(constants.canvas_width//2, 2),
                pos_anchor=posanchors.midtop
            )

        if self.selecting_path:
            utils.draw_rect(
                dest=canvas,
                size=(self.parent.event_free_control_hint.get_width() + 20, 40),
                pos=(constants.canvas_width//2, 0),
                pos_anchor=posanchors.midtop,
                color=(*colors.white, 150),
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.event_free_control_hint,
                pos=(constants.canvas_width//2, 2),
                pos_anchor=posanchors.midtop
            )
            utils.blit(
                dest=canvas,
                source=self.parent.mouse_hint_surface,
                pos=(constants.canvas_width//2 - 214, 4),
                pos_anchor=posanchors.topleft,
            )
            utils.blit(
                dest=canvas,
                source=self.parent.key_hint_surface,
                pos=(constants.canvas_width//2 - 46, 10),
                pos_anchor=posanchors.topleft,
            )

            utils.draw_rect(
                dest=canvas,
                size=(self.box_width, self.box_height),
                pos=(self.parent.box_width - 4, constants.canvas_height - self.box_height),
                pos_anchor='topleft',
                color=(*colors.white, 166), # 75% transparency
                inner_border_width=4,
                inner_border_color=colors.mono_240,
            )

            utils.blit(dest=canvas, source=self.path_WE_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 320), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NS_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 262), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NW_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 204), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_NE_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 146), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_WS_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 88), pos_anchor='center')
            utils.blit(dest=canvas, source=self.path_ES_image, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 30), pos_anchor='center')
            utils.blit(dest=canvas, source=self.small_selecting_tile, pos=(self.parent.box_width + self.box_width/2 - 4, constants.canvas_height - 320 + 58*self.choice), pos_anchor='center')

        if self.fruit_drawn_image:
            scaled_fruit_drawn = pygame.transform.scale_by(surface=self.fruit_drawn_image, factor=self.fruit_drawn_image_props['scale'])
            # scaled_fruit_drawn = utils.effect_outline(surface=scaled_fruit_drawn, distance=4, color=colors.white)
            utils.blit(
                dest=canvas,
                source=scaled_fruit_drawn,
                pos=(self.fruit_drawn_image_props['x'], self.fruit_drawn_image_props['y']),
                pos_anchor='center'
            )


    # Class methods
    def check_magic_fruit_collection(self, button):
        if self.parent.game_board.magic_fruit_index:

            # Find ALL connected magic fruits at once
            connected_magic_fruits = self.parent.game_board.find_all_connected_magic_fruits()
            
            if connected_magic_fruits:
                # Store all magic fruits in queue for processing in order (1->2->3)
                self.parent.magic_fruit_queue = connected_magic_fruits.copy()
                
                # Process the first magic fruit immediately
                magic_number, cell_pos = connected_magic_fruits[0]
                self.parent.magic_eventing = True
                
                utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                if magic_number == 1:
                    self.parent.current_event = self.parent.magic_fruit1_event
                    # print('PlacePath Magic 1:', self.parent.magic_fruit1_event)
                elif magic_number == 2:
                    self.parent.current_event = self.parent.magic_fruit2_event
                    # print('PlacePath Magic 2:', self.parent.magic_fruit2_event)
                elif magic_number == 3:
                    self.parent.current_event = self.parent.magic_fruit3_event
                    # print('PlacePath Magic 3:', self.parent.magic_fruit3_event)
                
                # Remove the magic fruit from the board and tracking
                self.parent.game_board.board[cell_pos].magic_fruit = 0
                self.parent.game_board.magic_fruit_index.remove(cell_pos)
                self.parent.magicing_number = magic_number
                
                current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                new_score = current_score + 1
                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                
                # # Check if the path that triggered magic fruit was also a strike
                # if "strike" in self.parent.current_path:
                #     self.parent.is_striking = True
            else:
                # No magic fruits found, eval the tile for potential new connections
                self.parent.game_board.eval_new_tile(button.id)
                
                # Check again after eval for newly connected magic fruits
                connected_magic_fruits = self.parent.game_board.find_all_connected_magic_fruits()
                
                if connected_magic_fruits:
                    # Store all magic fruits in queue for processing in order (1->2->3)
                    self.parent.magic_fruit_queue = connected_magic_fruits.copy()
                    
                    # Process the first magic fruit immediately
                    magic_number, cell_pos = connected_magic_fruits[0]
                    self.parent.magic_eventing = True
                    
                    utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                    if magic_number == 1:
                        self.parent.current_event = self.parent.magic_fruit1_event
                    elif magic_number == 2:
                        self.parent.current_event = self.parent.magic_fruit2_event
                    elif magic_number == 3:
                        self.parent.current_event = self.parent.magic_fruit3_event
                    
                    # Remove the magic fruit from the board and tracking
                    self.parent.game_board.board[cell_pos].magic_fruit = 0
                    self.parent.game_board.magic_fruit_index.remove(cell_pos)
                    self.parent.magicing_number = magic_number
                    
                    current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                    new_score = current_score + 1
                    setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                    setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                    
                    # Set played_event to True to exit this event and let magic_eventing take over
                    self.played_event = True

    def show_event_cancelled_popup(self):
        """Show popup when an event is cancelled due to being impossible"""
        self.parent.event_cancelled_popup_props = {
            'alpha': 255,
            'y': 2
        }
        
        def on_complete():
            self.parent.event_cancelled_popup_props = None
        
        # Show for 2 seconds, then fade out over 1 second
        self.parent.tween_list.append(tween.to(
            container=self.parent.event_cancelled_popup_props,
            key='alpha',
            end_value=0,
            time=1.0,
            delay=2.0,
            ease_type=tweencurves.easeOutQuint
        ).on_complete(on_complete))