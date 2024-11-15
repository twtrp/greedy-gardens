from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Play_StartState import Play_StartState
from src.states.Play_DrawPathState import Play_DrawPathState
from src.states.Play_DrawEventState import Play_DrawEventState
from src.states.Play_PlacePathState import Play_PlacePathState
from src.states.Play_PlayEventState import Play_PlayEventState
from src.states.Play_NextDayState import Play_NextDayState
from src.classes.Deck import Deck
from src.classes.GameBoard import GameBoard
from src.classes.Cell import Cell
import tween

class PlayState(BaseState):
    def __init__(self, game, parent, stack, seed):
        BaseState.__init__(self, game, parent, stack, seed)

        self.game.canvas.fill((0, 0, 0))
        self.seed = seed
        print("seed="+seed)

        # config of gui
        self.box_width = 272

        # create deck
        self.deck_fruit = Deck('fruit', seed)
        self.deck_path = Deck('path', seed)
        self.deck_event = Deck('event', seed)

        # drawn card
        self.drawn_cards_fruit = []
        self.drawn_cards_path = []
        self.drawn_cards_event = []
 
        # value
        self.day1_score = 0
        self.day2_score = 1
        self.day3_score = 2
        self.day4_score = 3
        self.seasonal_score = 4
        self.total_score = self.day1_score + self.day2_score + self.day3_score + self.day4_score + self.seasonal_score
        self.fruit_deck_remaining = Deck.remaining_cards(self.deck_fruit)
        self.path_deck_remaining = Deck.remaining_cards(self.deck_path)
        self.event_deck_remaining = Deck.remaining_cards(self.deck_event)

        self.day1_fruit = None
        self.day2_fruit = None
        self.day3_fruit = None
        self.day4_fruit = None
        self.seasonal_fruit = None
        
        self.magic_fruit1_event = None
        self.magic_fruit2_event = None
        self.magic_fruit3_event = None

        self.current_path = None
        self.current_event = None
        
        # define board
        self.game_board = GameBoard(seed)
        #function and example for use in gen map and place path
        #self.game_board.set_path(index, path_type)
        #self.game_board.add_fruit(index, fruit_type, value)
        #self.game_board.set_home(index)
        #self.game_board.set_magic_fruit(index,num)

        # stack
        self.substate_stack = []

        #state
        self.started = False
        self.drawing = False
        self.placing = False
        self.eventing = False
        self.is_strike = False
        self.is_3_strike = False
        # self.day1 = True
        # self.day2 = False
        # self.day3 = False
        # self.day4 = False
        self.day = 4
        self.current_day = 1
        self.strikes = 0

        self.ready = False
        self.load_assets()
        self.ready = True

        self.finished_boot_up = False
        
        # utils.music_load(music_channel=self.game.music_channel, name='menu_intro.ogg')
        # utils.music_queue(music_channel=self.game.music_channel, name='menu_loop.ogg', loops=-1)
        # self.game.music_channel.play()

        # self.tween_list = []
        # if not self.finished_boot_up:
        #     self.bootup_tween_chain(skip=self.game.settings['skip_bootup'])
        # else:
        #     self.bootup_tween_chain(skip=True)

    #Main methods

    def load_assets(self):
        
        #test grid
        self.cell_size = 80
        total_grid_width = self.cell_size * 8
        total_grid_height = self.cell_size * 8
        available_width = constants.canvas_width - (self.box_width * 2)
        self.grid_start_x = self.box_width + (available_width - total_grid_width) // 2
        self.grid_start_y = 8 + (constants.canvas_height - total_grid_height) // 2
        
        # Create hit boxes for each cell
        self.grid_hitboxes = []
        index=0
        for row in range(8):
            for col in range(8):
                cell_x = self.grid_start_x + (col * self.cell_size)
                cell_y = self.grid_start_y + (row * self.cell_size)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                self.grid_hitboxes.append(rect)
                self.game_board.board.append(Cell(index))
                index += 1
        #/test grid
        
        # Load background
        self.landscape_list = [
            {
                'image': utils.get_image(dir=dir.play_bg, name='grass_pattern.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='water_low.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='water_high.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='trees_bridges.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='fence.png', mode='colorkey'),
            },
        ]

        # color of score
        day1_color = colors.mono_150
        day2_color = colors.mono_150
        day3_color = colors.mono_150
        day4_color = colors.mono_150

        # left gui
        self.left_box_title = utils.get_text(text='Score', font=fonts.lf2, size='small', color=colors.white)

        self.score_list = [
            {'text': 'Day 1', 'color': day1_color, 'amount': self.day1_score},
            {'text': 'Day 2', 'color': day2_color, 'amount': self.day2_score},
            {'text': 'Day 3', 'color': day3_color, 'amount': self.day3_score},
            {'text': 'Day 4', 'color': day4_color, 'amount': self.day4_score},
            {'text': 'Seasonal', 'color': colors.yellow_light, 'amount': self.seasonal_score},
            {'text': 'Total', 'color': colors.white, 'amount': self.total_score},
        ]

        self.score_title_list = []
        for score in self.score_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=score['color'])
            self.score_title_list.append(text)

        self.score_amount_list = []
        for score in self.score_list:
            amount = utils.get_text(text=str(score['amount']), font=fonts.lf2, size='smaller', color=score['color'])
            self.score_amount_list.append(amount)

        self.left_box_strike = utils.get_text(text='Event Strikes', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_task = utils.get_text(text='Current task', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_path_text = utils.get_text(text='Place drawn path', font=fonts.lf2, size='tiny', color=colors.white)

        self.blank_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_blank')
        self.live_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_live')

        # right gui
        self.right_box_title = utils.get_text(text='Cards', font=fonts.lf2, size='small', color=colors.white)

        self.deck_list = [
            {'text': 'Fruit',},
            {'text': 'Path',},
            {'text': 'Event',},
        ]

        self.deck_title_list = []
        for score in self.deck_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=colors.white)
            self.deck_title_list.append(text)

        self.right_remaining = utils.get_text(text='Remaining', font=fonts.lf2, size='smaller', color=colors.white)
        self.right_magic_fruits = utils.get_text(text='Magic Fruits', font=fonts.lf2, size='small', color=colors.white)

        self.card_fruit_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite='card_fruit_back')
        self.card_path_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite='card_path_back')
        self.card_event_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite='card_event_back')

        # dirt path
        self.dirt_sprites_1 = []
        self.dirt_sprites_2 = []
        self.dirt_sprites_3 = []
        self.dirt_sprites_4 = []
        self.dirt_sprites_5 = []
        self.dirt_sprites_6 = []
        self.dirt_sprites_7 = []
        self.dirt_sprites_8 = []
        self.dirt_sprites_9 = []
        for _ in self.grid_hitboxes:
            self.dirt_sprites_1.append(self.random_dirt())  
            self.dirt_sprites_2.append(self.random_dirt())
            self.dirt_sprites_3.append(self.random_dirt())
            self.dirt_sprites_4.append(self.random_dirt())
            self.dirt_sprites_5.append(self.random_dirt())
            self.dirt_sprites_6.append(self.random_dirt())
            self.dirt_sprites_7.append(self.random_dirt())
            self.dirt_sprites_8.append(self.random_dirt())
            self.dirt_sprites_9.append(self.random_dirt())
        for i, rect in enumerate(self.grid_hitboxes):
            self.dirt_sprite_1 = self.dirt_sprites_1[i]
            self.dirt_sprite_2 = self.dirt_sprites_2[i]
            self.dirt_sprite_3 = self.dirt_sprites_3[i]
            self.dirt_sprite_4 = self.dirt_sprites_4[i]
            self.dirt_sprite_5 = self.dirt_sprites_5[i]
            self.dirt_sprite_6 = self.dirt_sprites_6[i]
            self.dirt_sprite_7 = self.dirt_sprites_7[i]
            self.dirt_sprite_8 = self.dirt_sprites_8[i]
            self.dirt_sprite_9 = self.dirt_sprites_9[i]

        # grass path
        self.grass_light_path_N = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_N')
        self.grass_light_path_W = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_W')
        self.grass_light_path_E = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_E')
        self.grass_light_path_S = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_S')
        self.grass_light_path_NW = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NW')
        self.grass_light_path_NE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NE')
        self.grass_light_path_NS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NS')
        self.grass_light_path_WE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WE')
        self.grass_light_path_WS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WS')
        self.grass_light_path_ES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_ES')
        self.grass_light_path_NWE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NWE')
        self.grass_light_path_NWS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NWS')
        self.grass_light_path_NES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NES')
        self.grass_light_path_WES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WES')
        self.grass_light_path_NWES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NWES')
        self.grass_light_path_none = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_none')
        
        self.grass_dark_path_N = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_N')
        self.grass_dark_path_W = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_W')
        self.grass_dark_path_E = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_E')
        self.grass_dark_path_S = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_S')
        self.grass_dark_path_NW = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NW')
        self.grass_dark_path_NE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NE')
        self.grass_dark_path_NS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NS')
        self.grass_dark_path_WE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WE')
        self.grass_dark_path_WS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WS')
        self.grass_dark_path_ES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_ES')
        self.grass_dark_path_NWE = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NWE')
        self.grass_dark_path_NWS = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NWS')
        self.grass_dark_path_NES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NES')
        self.grass_dark_path_WES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WES')
        self.grass_dark_path_NWES = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NWES')
        self.grass_dark_path_none = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_none')

        # magic fruit
        self.magic_fruit1_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite='magic_fruit_1')
        self.scaled_magic_fruit1_image = pygame.transform.scale_by(surface=self.magic_fruit1_image, factor=2)
        self.magic_fruit2_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite='magic_fruit_2')
        self.scaled_magic_fruit2_image = pygame.transform.scale_by(surface=self.magic_fruit2_image, factor=2)
        self.magic_fruit3_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite='magic_fruit_3')
        self.scaled_magic_fruit3_image = pygame.transform.scale_by(surface=self.magic_fruit3_image, factor=2)

    def update(self, dt, events):
        if self.ready:

            # Update substates
            if self.substate_stack:
                self.substate_stack[-1].update(dt=dt, events=events)

            # Update tweens
            tween.update(passed_time=dt)

        # State change and loop
        if not self.started:
            Play_StartState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.started = True
        elif self.drawing:
            Play_DrawPathState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.drawing = False
        elif self.placing:
            Play_PlacePathState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.placing = False
        elif self.is_strike:
            Play_DrawEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.is_strike = False
        elif self.eventing:
            Play_PlayEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.eventing = False
        elif self.is_3_strike:
            Play_NextDayState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
            self.is_3_strike = False
        

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                        self.exit_state()
                        
            #test grid
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     mouse_pos = pygame.mouse.get_pos()
            #     for i, rect in enumerate(self.grid_hitboxes):
            #         if rect.collidepoint(mouse_pos):
            #             print(f"Hit box {i} clicked!")
            #             clicked_cell = self.game_board.board[i]
            #             clicked_cell.show_detail()
            #/test grid

        # Update deck remaining
        self.fruit_deck_remaining = Deck.remaining_cards(self.deck_fruit)
        self.path_deck_remaining = Deck.remaining_cards(self.deck_path)
        self.event_deck_remaining = Deck.remaining_cards(self.deck_event)

        # Update day/score color and amount
        ## check color of score
        day_colors = {
            "day1_color": colors.mono_150,
            "day2_color": colors.mono_150,
            "day3_color": colors.mono_150,
            "day4_color": colors.mono_150
        }

        for i in range(1,self.day + 1):
            if i < self.current_day:
                day_colors[f"day{i}_color"] = colors.white
            elif i == self.current_day:
                day_colors[f"day{i}_color"] = colors.yellow_light
            else:
                day_colors[f"day{i}_color"] = colors.mono_150

        self.score_list = [
            {'text': 'Day 1', 'color': day_colors['day1_color'], 'amount': self.day1_score},
            {'text': 'Day 2', 'color': day_colors['day2_color'], 'amount': self.day2_score},
            {'text': 'Day 3', 'color': day_colors['day3_color'], 'amount': self.day3_score},
            {'text': 'Day 4', 'color': day_colors['day4_color'], 'amount': self.day4_score},
            {'text': 'Seasonal', 'color': colors.yellow_light, 'amount': self.seasonal_score},
            {'text': 'Total', 'color': colors.white, 'amount': self.total_score},
        ]

        self.score_title_list = []
        for score in self.score_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=score['color'])
            self.score_title_list.append(text)

        self.score_amount_list = []
        for score in self.score_list:
            amount = utils.get_text(text=str(score['amount']), font=fonts.lf2, size='smaller', color=score['color'])
            self.score_amount_list.append(amount)

    def render(self, canvas):
        
        
            
        if self.ready:
            
            for layer in self.landscape_list:
                utils.blit(dest=canvas, source=layer['image'], pos=(0, 0))
                
            #test grid
            # for rect in self.grid_hitboxes:
            #     pygame.draw.rect(canvas, (255, 0, 0), rect, 2)
            #/test grid

            # Build background

            ## Render landscape to menu_bg
                
            # Render gui

            # Render left white box
            utils.draw_rect(dest=canvas,
                                size=(self.box_width, constants.canvas_height),
                                pos=(0, 0),
                                pos_anchor='topleft',
                                color=(*colors.white, 191), # 75% transparency
                                inner_border_width=4,
                                outer_border_width=0,
                                outer_border_color=colors.black)
            
            # Render text in left white box
            utils.blit(dest=canvas, source=self.left_box_title, pos=(self.box_width/2, 40), pos_anchor='center')
            for i, score in enumerate(self.score_title_list):
                utils.blit(dest=canvas, source=score, pos=(60, 80 + i*45), pos_anchor='topleft')
            utils.blit(dest=canvas, source=self.left_box_strike, pos=(self.box_width/2, 390), pos_anchor='center')
            utils.blit(dest=canvas, source=self.left_box_task, pos=(self.box_width/2, 510), pos_anchor='center')
            utils.blit(dest=canvas, source=self.left_box_path_text, pos=(self.box_width/2, 550), pos_anchor='center')

            # Render image in left white box
            scaled_live_strike = pygame.transform.scale_by(surface=self.live_strike_image, factor=0.625)
            for i in range(self.strikes):
                    utils.blit(dest=canvas, source=scaled_live_strike, pos=(40 + i*64, 420), pos_anchor='topleft')
            scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)
            for i in range(3 - self.strikes):
                    utils.blit(dest=canvas, source=scaled_blank_strike, pos=(40 + i*64 + self.strikes*64, 420), pos_anchor='topleft')
                ## Render current task image
            if self.current_path:
                self.current_path_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite=f"card_{self.current_path}")
                scaled_current_path_image = pygame.transform.scale_by(surface=self.current_path_image, factor=0.875)
                utils.blit(dest=canvas, source=scaled_current_path_image, pos=(self.box_width/2, 640), pos_anchor='center')

                ## Render Day's Fruit
            if self.day1_fruit:
                if self.current_day == 1:
                    self.day1_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day1_fruit)
                else:
                    self.day1_fruit_image = utils.effect_grayscale(utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day1_fruit))
                self.scaled_day1_fruit_image = pygame.transform.scale_by(surface=self.day1_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=self.scaled_day1_fruit_image, pos=(40, 95), pos_anchor='center')
            if self.day2_fruit:
                if self.current_day == 2:
                    self.day2_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day2_fruit)
                else:
                    self.day2_fruit_image = utils.effect_grayscale(utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day2_fruit))
                self.scaled_day2_fruit_image = pygame.transform.scale_by(surface=self.day2_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=self.scaled_day2_fruit_image, pos=(40, 140), pos_anchor='center')
            if self.day3_fruit:
                if self.current_day == 3:
                    self.day3_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day3_fruit)
                else:
                    self.day3_fruit_image = utils.effect_grayscale(utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day3_fruit))
                self.scaled_day3_fruit_image = pygame.transform.scale_by(surface=self.day3_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=self.scaled_day3_fruit_image, pos=(40, 185), pos_anchor='center')
            if self.day4_fruit:
                if self.current_day == 4:
                    self.day4_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day4_fruit)
                else:
                    self.day4_fruit_image = utils.effect_grayscale(utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day4_fruit))
                self.scaled_day4_fruit_image = pygame.transform.scale_by(surface=self.day4_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=self.scaled_day4_fruit_image, pos=(40, 230), pos_anchor='center')
            if self.seasonal_fruit:
                self.seasonal_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.seasonal_fruit)
                scaled_seasonal_fruit_image = pygame.transform.scale_by(surface=self.seasonal_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_seasonal_fruit_image, pos=(40, 275), pos_anchor='center')

            # Render value in left white box
            for i, score in enumerate(self.score_amount_list):
                utils.blit(dest=canvas, source=score, pos=(240, 80 + i*45), pos_anchor='topright')
            
            # Render right white box
            utils.draw_rect(dest=canvas,
                                size=(self.box_width, constants.canvas_height),
                                pos=(constants.canvas_width - self.box_width, 0),
                                pos_anchor='topleft',
                                color=(*colors.white, 191), # 75% transparency
                                inner_border_width=4,
                                outer_border_width=0,
                                outer_border_color=colors.black)
            
            # Render text in right white box
            utils.blit(dest=canvas, source=self.right_box_title, pos=(constants.canvas_width - self.box_width/2, 40), pos_anchor='center')
            for i, deck in enumerate(self.deck_title_list):
                utils.blit(dest=canvas, source=deck, pos=(1150, 85 + i*125), pos_anchor='topleft')
                utils.blit(dest=canvas, source=self.right_remaining, pos=(1150, 110 + i*125), pos_anchor='topleft')
            utils.blit(dest=canvas, source=self.right_magic_fruits, pos=(constants.canvas_width - self.box_width/2, 475), pos_anchor='center')

            # Render image in right white box
            scaled_card_fruit_back = pygame.transform.scale_by(surface=self.card_fruit_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_fruit_back, pos=(1079, 125), pos_anchor='center')
            scaled_card_path_back = pygame.transform.scale_by(surface=self.card_path_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_path_back, pos=(1079, 250), pos_anchor='center')
            scaled_card_event_back = pygame.transform.scale_by(surface=self.card_event_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_event_back, pos=(1079, 375), pos_anchor='center')

                ## Render Magic Fruit Event
            if self.magic_fruit1_event:
                self.magic_fruit1_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit1_event}")
                utils.blit(dest=canvas, source=self.magic_fruit1_event_image, pos=(1040, 530), pos_anchor='topleft')
                utils.blit(dest=canvas, source=self.scaled_magic_fruit1_image, pos=(1072, 510), pos_anchor='topleft')
            if self.magic_fruit2_event:
                self.magic_fruit2_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit2_event}")
                utils.blit(dest=canvas, source=self.magic_fruit2_event_image, pos=(1100, 550), pos_anchor='topleft')
                utils.blit(dest=canvas, source=self.scaled_magic_fruit2_image, pos=(1132, 530), pos_anchor='topleft')
            if self.magic_fruit3_event:
                self.magic_fruit3_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit3_event}")
                utils.blit(dest=canvas, source=self.magic_fruit3_event_image, pos=(1160, 570), pos_anchor='topleft')
                utils.blit(dest=canvas, source=self.scaled_magic_fruit3_image, pos=(1192, 550), pos_anchor='topleft')

            # Render value in right white box
            self.fruit_deck_remaining_amount = utils.get_text(text=str(self.fruit_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.fruit_deck_remaining_amount, pos=(1150, 135), pos_anchor='topleft')
            self.path_deck_remaining_amount = utils.get_text(text=str(self.path_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.path_deck_remaining_amount, pos=(1150, 260), pos_anchor='topleft')
            self.event_deck_remaining_amount = utils.get_text(text=str(self.event_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.event_deck_remaining_amount, pos=(1150, 385), pos_anchor='topleft')

            # Render path on board

            ## Render path on placed tile
            for i, rect in enumerate(self.grid_hitboxes):
                if ((i // 8) + (i % 2)) % 2 == 0:
                    if self.game_board.board[i].temp:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                    else:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_S, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i-1)//8] and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else: 
                                utils.blit(dest=canvas, source=self.grass_light_path_E, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i+1)//8] and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_W, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i <= 55 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_N, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        if (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                else:
                    if self.game_board.board[i].temp:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                    else:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_S, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i-1)//8] and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:    
                                utils.blit(dest=canvas, source=self.grass_dark_path_E, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i+1)//8] and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_W, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i <= 55 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_N, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        if (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')

            if not self.substate_stack:

                # ## Render menu options
                # for i, option in enumerate(self.title_button_option_surface_list):
                #     processed_option = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                #     processed_option.set_alpha(option['alpha'])
                #     utils.blit(dest=canvas, source=processed_option, pos=(constants.canvas_width/2, 340 + i*80), pos_anchor=posanchors.center)

                pass

            else:
                self.substate_stack[-1].render(canvas=canvas)          
                
    def random_dirt(self):
        return utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite=f"dirt_{random.randint(1, 9)}")
    

    #Class methods
  
    # def bootup_tween_chain(self, skip=False):
    #     if not skip:
    #         delay = 0
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='alpha',
    #                                         end_value=255,
    #                                         time=2,
    #                                         ease_type=tweencurves.easeOutCubic,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='scale',
    #                                         end_value=1,
    #                                         time=3,
    #                                         ease_type=tweencurves.easeOutCubic,
    #                                         delay=delay))

    #         delay = 1.75
    #         self.tween_list.append(tween.to(container=self.overlay_props,
    #                                         key='alpha',
    #                                         end_value=0,
    #                                         time=2,
    #                                         ease_type=tweencurves.easeOutQuad,
    #                                         delay=delay))
    #         for layer in self.landscape_list:
    #             self.tween_list.append(tween.to(container=layer,
    #                                             key='y_offset',
    #                                             end_value=0,
    #                                             time=3.25,
    #                                             ease_type=tweencurves.easeOutQuint,
    #                                             delay=delay))
                
    #         self.tween_list.append(tween.to(container=self.winds_props,
    #                                         key='y_offset',
    #                                         end_value=0,
    #                                         time=3.25,
    #                                         ease_type=tweencurves.easeOutQuint,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='y_offset',
    #                                         end_value=-500,
    #                                         time=3.25,
    #                                         ease_type=tweencurves.easeOutQuint,
    #                                         delay=delay).on_complete(self.finish_bootup))
            
    #         delay = 4
    #         self.tween_list.append(tween.to(container=self.game_logo_props,
    #                                         key='scale',
    #                                         end_value=1,
    #                                         time=0.75,
    #                                         ease_type=tweencurves.easeOutElastic,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.game_logo_props,
    #                                         key='alpha',
    #                                         end_value=255,
    #                                         time=0.1,
    #                                         ease_type=tweencurves.easeOutCirc,
    #                                         delay=delay))
            
    #         for option in self.title_button_option_surface_list:
    #             delay += 0.125
    #             self.tween_list.append(tween.to(container=option,
    #                                             key='scale',
    #                                             end_value=1,
    #                                             time=0.5,
    #                                             ease_type=tweencurves.easeOutElastic,
    #                                             delay=delay))
    #             self.tween_list.append(tween.to(container=option,
    #                                             key='alpha',
    #                                             end_value=255,
    #                                             time=0.1,
    #                                             ease_type=tweencurves.easeOutCirc,
    #                                             delay=delay))
                
    #     else:
    #         self.finish_bootup()


    # def finish_bootup(self):
    #     self.finished_boot_up = True

    #     # Clear intro assets
    #     del self.overlay
    #     del self.overlay_props

    #     # Set props to final values
    #     for layer in self.landscape_list:
    #         layer['y_offset'] = 0
    #         self.winds_props['y_offset'] = 0
    #         self.game_logo_props['scale'] = 1
    #         self.game_logo_props['alpha'] = 255
    #         for option in self.title_button_option_surface_list:
    #             option['scale'] = 1
    #             option['alpha'] = 255

    #     # Convert surfaces to static
    #     self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
    #     for option in self.title_button_option_surface_list:
    #         option['surface'] = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
        
    #     # Initiate substate
    #     Play_StartState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
