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
        if (self.parent.current_event == 'event_keep' or
            self.parent.current_event == 'event_point' or
            self.parent.current_event == 'event_redraw' or
            self.parent.current_event == 'event_reveal'):
            self.choosing = True
            utils.sound_play(sound=sfx.appear, volume=self.game.sfx_volume)
        else:
            self.choosing = False
        self.drawn_keep = False

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

        # event keep
        self.card_path1_image_scale = 1
        self.card_path2_image_scale = 1

        self.load_assets()

    def load_assets(self):
        # Load text
        self.choice_keep_title = utils.get_text(text='Choose a card to keep', font=fonts.lf2, size='large', color=colors.mono_205)
        self.choice_point_title = utils.get_text(text='Choose', font=fonts.lf2, size='large', color=colors.mono_205)
        self.choice_redraw_title = utils.get_text(text='Choose a fruit to redraw', font=fonts.lf2, size='large', color=colors.mono_205)
        # self.remaining_fruit_title = utils.get_text(text='Remaining Fruit', font=fonts.lf2, size='large', color=colors.mono_175)
        self.hover_to_view_title = utils.get_text(text='Hover here to view board', font=fonts.lf2, size='small', color=colors.white)
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
                        'text1': 'Get 1 point today,',
                        'text2': 'Lose 1 point next day',
                    },
                    {
                        'id': 'lose today',
                        'text1': 'Lose 1 point today,',
                        'text2': 'Get 1 point next day',
                    },
                ]
            else:
                self.point_button_option_list = [
                    {
                        'id': 'add today',
                        'text1': 'Get free 1 point today',
                        'text2': '',
                    },
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
                    pos=(constants.canvas_width/2, 265 + i*75),
                    pos_anchor=posanchors.center
                ))
        elif self.parent.current_event == 'event_remove':
            self.remove_button_option_list = [
                {
                    'id': 'remove',
                    'text': 'Remove',
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
                    'text': 'Reveal top 3 path cards',
                },
                {
                    'id': 'reveal event',
                    'text': 'Reveal top 4 event cards',
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
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*1.25)
                            self.choice -= 1
                        elif (event.key == pygame.K_s or event.key == pygame.K_DOWN) and self.choice < 5:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*1.25)
                            self.choice += 1
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4 and self.choice > 0:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*1.25)
                            self.choice -= 1
                        elif event.button == 5 and self.choice < 5:
                            utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*1.25)
                            self.choice += 1

                self.cell_pos = -1
                for button in self.parent.grid_buttons:
                    if button.hovered:
                        self.cursor = cursors.dig
                        self.cell_pos = button.id
                        if not self.parent.game_board.board[button.id].path and not self.parent.game_board.board[button.id].home:
                            self.select_frame = self.parent.selecting_tile
                            if button.clicked:
                                utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume)
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
                                if self.parent.game_board.magic_fruit_index:
                                    self.parent.game_board.eval_new_tile(button.id)
                                    self.parent.magic_eventing, magic_number, cell_pos = self.parent.game_board.magic_fruit_found()
                                    if self.parent.magic_eventing:
                                        utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                                        if magic_number == 1:
                                            self.parent.current_event = self.parent.magic_fruit1_event
                                        elif magic_number == 2:
                                            self.parent.current_event = self.parent.magic_fruit2_event
                                        elif magic_number == 3:
                                            self.parent.current_event = self.parent.magic_fruit3_event
                                        self.parent.game_board.board[cell_pos].magic_fruit = 0
                                        self.parent.magicing_number = magic_number
                                        current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                                        new_score = current_score + 1
                                        setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                                        setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                                        self.parent.play_event_state= False
                                        self.exit_state()
                                self.played_event = True
                        else:
                            self.select_frame = self.parent.cant_selecting_tile

            elif self.parent.current_event == 'event_keep':
                # print('event_keep')
                if not self.drawn_keep:
                    self.card_path1 = self.parent.deck_path.draw_card()
                    self.card_path2 = self.parent.deck_path.draw_card()
                    self.card_path1_image = self.parent.cards_path_sprites[f"card_{self.card_path1.card_name}"]
                    self.card_path2_image = self.parent.cards_path_sprites[f"card_{self.card_path2.card_name}"]
                    self.card_path_button_option_list = [
                        {
                            'id': 'path 1',
                        },
                        {
                            'id': 'path 2',
                        },
                    ]
                    for i, option in enumerate(self.card_path_button_option_list):
                        self.button_list.append(Button(
                            game=self.game,
                            id=option['id'],
                            width=192,
                            height=256,
                            pos=(constants.canvas_width/2 - 105 + i*210, constants.canvas_height/2),
                            pos_anchor=posanchors.center
                        ))
                    # self.parent.current_path = self.card_drawn.card_name
                    self.drawn_keep = True
                elif self.drawn_keep:
                    for button in self.button_list:
                        button.update(dt=dt, events=events)
                        if button.hovered:
                            if button.id == 'path 1':
                                self.card_path1_image_scale = min(self.card_path1_image_scale + 2.4*dt, 1.1)
                            elif button.id == 'path 2':
                                self.card_path2_image_scale = min(self.card_path2_image_scale + 2.4*dt, 1.1)
                            elif button.id == 'view board':
                                self.choosing = False
                            if button.hover_cursor is not None:
                                self.cursor = button.hover_cursor
                        else:
                            if button.id == 'path 1':
                                self.card_path1_image_scale = max(self.card_path1_image_scale - 2.4*dt, 1.0)
                            elif button.id == 'path 2':
                                self.card_path2_image_scale = max(self.card_path2_image_scale - 2.4*dt, 1.0)
                            elif button.id == 'view board':
                                self.choosing = True
                        if button.clicked:
                            if button.id == 'path 1':
                                # print(f'select path 1')
                                utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                self.parent.deck_path.cards.append(self.card_path1)
                                self.choosing = False
                                self.played_event = True
                            elif button.id == 'path 2':
                                # print(f'select path 2')
                                utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                self.parent.deck_path.cards.append(self.card_path2)
                                self.choosing = False
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
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume)
                                        utils.sound_play(sound=sfx.dirt, volume=self.game.sfx_volume)
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
                                        if self.parent.game_board.magic_fruit_index:
                                            self.parent.game_board.eval_new_tile(button.id)
                                            self.parent.magic_eventing, magic_number, cell_pos = self.parent.game_board.magic_fruit_found()
                                            if self.parent.magic_eventing:
                                                utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                                                if magic_number == 1:
                                                    self.parent.current_event = self.parent.magic_fruit1_event
                                                elif magic_number == 2:
                                                    self.parent.current_event = self.parent.magic_fruit2_event
                                                elif magic_number == 3:
                                                    self.parent.current_event = self.parent.magic_fruit3_event
                                                self.parent.game_board.board[cell_pos].magic_fruit = 0
                                                self.parent.magicing_number = magic_number
                                                current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                                                new_score = current_score + 1
                                                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                                                setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                                                self.parent.play_event_state= False
                                                self.exit_state()
                                        self.selected_cell = None
                                        self.played_event = True
                                elif button.id == self.selected_cell:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                        self.selected_cell = None
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile

                else:
                    # print("No merge possible")
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
                                ease_type=tweencurves.easeOutQuint,
                                on_complete=on_complete
                            )
                            
                        if button.id == 'today fruit':
                            # print('redraw today fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            old_fruit = getattr(self.parent, f'day{self.parent.current_day}_fruit')
                            setattr(self.parent, f'day{self.parent.current_day}_fruit', self.card_drawn.card_name)
                            self.parent.deck_fruit.cards.append(Cards('fruit', old_fruit, False))
                            random.shuffle(self.parent.deck_fruit.cards)
                            self.fruit_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                            self.choosing = False
                            self.parent.is_current_task_event = False
                            self.parent.drawing_path_card = True
                        elif button.id == 'tomorrow fruit':
                            # print('redraw tomorrow fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            old_fruit = getattr(self.parent, f'day{self.parent.current_day + 1}_fruit')
                            setattr(self.parent, f'day{self.parent.current_day + 1}_fruit', self.card_drawn.card_name)
                            self.parent.deck_fruit.cards.append(Cards('fruit', old_fruit, False))
                            random.shuffle(self.parent.deck_fruit.cards)
                            self.fruit_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                            self.choosing = False
                            self.parent.is_current_task_event = False
                            self.parent.drawing_path_card = True
                        elif button.id == 'seasonal fruit':
                            # print('redraw seasonal fruit')
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                            utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            old_fruit = self.parent.seasonal_fruit
                            self.parent.seasonal_fruit = self.card_drawn.card_name
                            self.parent.deck_fruit.cards.append(Cards('fruit', old_fruit, False))
                            random.shuffle(self.parent.deck_fruit.cards)
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
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
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
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                    self.selected_cell = None
                            else:
                                self.select_frame = self.parent.cant_selecting_tile
                        else:
                            if button.id == self.selected_cell:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                    self.selected_cell = None
                            elif button.id == self.selected_cell_2:
                                self.select_frame = self.parent.selecting_tile
                                if button.clicked:
                                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                    self.selected_cell_2 = None
                            else:
                                self.select_frame = self.parent.cant_selecting_tile

                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    if button.hovered:
                        for option in self.remove_button_option_surface_list:
                            if self.selected_cell or self.selected_cell_2:
                                if button.hover_cursor is not None:
                                    self.cursor = button.hover_cursor
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                    else:
                        for option in self.remove_button_option_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                    if button.clicked:
                        if self.selected_cell or self.selected_cell_2:
                            if button.id == 'remove':
                                utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                utils.sound_play(sound=sfx.dirt, volume=self.game.sfx_volume)
                                if self.selected_cell:
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
                                if self.selected_cell_2:
                                    if not self.parent.game_board.board[self.selected_cell].temp:
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
                                    self.parent.game_board.board[self.selected_cell].temp = False
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
                            self.played_event = True
                # self.played_event = True

            elif self.parent.current_event == 'event_swap':
                # print('event_swap')
                if len(self.parent.drawn_cards_path) >= 2 and Deck.not_all_duplicate(self.parent.drawn_cards_path):

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
                                        utils.sound_play(sound=sfx.dirt, volume=self.game.sfx_volume)
                                        utils.sound_play(sound=sfx.dig, volume=self.game.sfx_volume)
                                        Cell.swap_path(self.parent.game_board.board[button.id], self.parent.game_board.board[self.selected_cell])
                                        self.selected_cell = None
                                        self.played_event = True
                                elif button.id == self.selected_cell:
                                    self.select_frame = self.parent.selecting_tile
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)
                                        self.selected_cell = None
                                else:
                                    self.select_frame = self.parent.cant_selecting_tile
                else:
                    # print("No swap possible")
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
            
            if self.parent.current_event == 'event_keep':
                utils.blit(dest=canvas, source=self.choice_keep_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                if self.card_path2_image:
                    scaled_card_path1 = pygame.transform.scale_by(surface=self.card_path1_image, factor=2*self.card_path1_image_scale)
                    scaled_card_path2 = pygame.transform.scale_by(surface=self.card_path2_image, factor=2*self.card_path2_image_scale)
                    utils.blit(dest=canvas, source=scaled_card_path1, pos=(constants.canvas_width/2 - 105, constants.canvas_height/2), pos_anchor='center')
                    utils.blit(dest=canvas, source=scaled_card_path2, pos=(constants.canvas_width/2 + 105, constants.canvas_height/2), pos_anchor='center')

            elif self.parent.current_event == 'event_point':
                utils.blit(dest=canvas, source=self.choice_point_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                for i, option in enumerate(self.point_button_option_surface_list):
                    scaled_point_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
                    utils.blit(
                        dest=canvas,
                        source=scaled_point_button,
                        pos=(constants.canvas_width/2, constants.canvas_height/2 - 75 + i*150 - 30),
                        pos_anchor=posanchors.center
                    )
                    scaled_point_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
                    utils.blit(
                        dest=canvas,
                        source=scaled_point_button,
                        pos=(constants.canvas_width/2, constants.canvas_height/2 - 75 + i*150 + 30),
                        pos_anchor=posanchors.center
                    )

            elif self.parent.current_event == 'event_redraw':
                utils.blit(dest=canvas, source=self.choice_redraw_title, pos=(constants.canvas_width/2, 160), pos_anchor=posanchors.center)
                for i, option in enumerate(self.redraw_button_option_surface_list):
                    if option['id'] == 'dummy':
                        continue
                    scaled_redraw_button = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    if option["id"] == "do nothing":
                        utils.blit(dest=canvas, source=scaled_redraw_button, pos=(constants.canvas_width/2, 265 + i*75), pos_anchor=posanchors.center)
                    else:
                        utils.blit(dest=canvas, source=scaled_redraw_button, pos=(constants.canvas_width/2 + 35, 265 + i*75), pos_anchor=posanchors.center)
                        self.scaled_fruit_image = pygame.transform.scale_by(surface=option['surface_fruit'], factor=option['scale_fruit'])
                        self.glow_fruit_image = utils.effect_outline(surface=self.scaled_fruit_image, distance=2, color=colors.white)
                        utils.blit(dest=canvas, source=self.glow_fruit_image, pos=(570 - (i//2)*30, 265 + i*75), pos_anchor='center')
                        
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

        if self.selected_cell:
            utils.blit(dest=canvas, source=self.selected_tile, pos=(self.parent.grid_start_x + ((self.selected_cell % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell // 8) * self.parent.cell_size)), pos_anchor='topleft')
        if self.selected_cell_2:
            utils.blit(dest=canvas, source=self.selected_tile, pos=(self.parent.grid_start_x + ((self.selected_cell_2 % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.selected_cell_2 // 8) * self.parent.cell_size)), pos_anchor='topleft')

        if self.parent.current_event == 'event_remove':
            for i, option in enumerate(self.remove_button_option_surface_list):
                if self.selected_cell or self.selected_cell_2:
                    scaled_remove_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
                else:
                    scaled_remove_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
                utils.blit(dest=canvas, source=scaled_remove_button, pos=(constants.canvas_width/2, 690), pos_anchor=posanchors.center)


        if self.selecting_path:
            utils.blit(
                dest=canvas,
                source=self.parent.up_key_hint,
                pos=(self.parent.box_width, constants.canvas_height - self.box_height - 32),
                pos_anchor='topleft'                            
            )
            utils.blit(
                dest=canvas,
                source=self.parent.down_key_hint,
                pos=(self.parent.box_width + 28, constants.canvas_height - self.box_height - 32),
                pos_anchor='topleft'
            )

            utils.draw_rect(dest=canvas,
                                    size=(self.box_width, self.box_height),
                                    pos=(self.parent.box_width - 4, constants.canvas_height - self.box_height),
                                    pos_anchor='topleft',
                                    color=(*colors.white, 166), # 75% transparency
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

        if self.fruit_drawn_image:
            scaled_fruit_drawn = pygame.transform.scale_by(surface=self.fruit_drawn_image, factor=self.fruit_drawn_image_props['scale'])
            scaled_fruit_drawn = utils.effect_outline(surface=scaled_fruit_drawn, distance=4, color=colors.white)
            utils.blit(
                dest=canvas,
                source=scaled_fruit_drawn,
                pos=(self.fruit_drawn_image_props['x'], self.fruit_drawn_image_props['y']),
                pos_anchor='center'
            )
