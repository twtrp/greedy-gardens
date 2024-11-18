from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Play_StartState import Play_StartState
from src.states.Play_DrawPathState import Play_DrawPathState
from src.states.Play_DrawEventState import Play_DrawEventState
from src.states.Play_PlacePathState import Play_PlacePathState
from src.states.Play_PlayEventState import Play_PlayEventState
from src.states.Play_PlayMagicEventState import Play_PlayMagicEventState
from src.states.Play_NextDayState import Play_NextDayState
from src.states.Play_EndDayState import Play_EndDayState
from src.states.Play_ResultState import Play_ResultStage
from src.classes.Deck import Deck
from src.classes.GameBoard import GameBoard
from src.classes.Cell import Cell
from src.classes.Button import Button
from src.classes.TimerManager import TimerManager
from src.classes.Wind import Wind
import tween

class PlayState(BaseState):
    def __init__(self, game, parent, stack, seed):
        BaseState.__init__(self, game, parent, stack, seed)

        self.ready = False

        if seed == '':
            self.set_seed = False
            self.seed = random.randint(0, 99999999)
        else:
            self.seed = seed

        print(self.seed)

        self.game.canvas.fill((0, 0, 0))

        # config of gui
        self.box_width = 272

        # create deck
        self.deck_fruit = Deck('fruit', self.seed)
        self.deck_path = Deck('path', self.seed)
        self.deck_event = Deck('event', self.seed)

        # drawn card
        self.drawn_cards_fruit = []
        self.drawn_cards_path = []
        self.drawn_cards_event = []
 
        # value
        self.day1_score = 0
        self.day2_score = 0
        self.day3_score = 0
        self.day4_score = 0
        self.seasonal_score = 0
        self.final_day1_score = 0
        self.final_day2_score = 0
        self.final_day3_score = 0
        self.final_day4_score = 0
        self.final_seasonal_score = 0
        self.total_score = 0
        self.fruit_deck_remaining = Deck.remaining_cards(self.deck_fruit)
        self.path_deck_remaining = Deck.remaining_cards(self.deck_path)
        self.event_deck_remaining = Deck.remaining_cards(self.deck_event)

        self.revealed_path = []
        self.revealed_event = []
        self.day1_fruit = None
        self.day2_fruit = None
        self.day3_fruit = None
        self.day4_fruit = None
        self.seasonal_fruit = None
        
        self.magic_fruit1_event = None
        self.magic_fruit2_event = None
        self.magic_fruit3_event = None
        self.magicing_number = 0

        self.current_path = None
        self.current_event = None
        
        # define board
        self.game_board = GameBoard(self.seed)

        # stack
        self.substate_stack = []

        #state
        self.started = False
        self.drawing = False
        self.placing = False
        self.eventing = False
        self.is_strike = False
        self.is_3_strike = False
        self.magic_eventing = False
        self.playing_magic_event = False
        # self.day1 = True
        # self.day2 = False
        # self.day3 = False
        # self.day4 = False
        self.day = 4
        self.current_day = 1
        self.strikes = 0
        self.is_striking = False

        self.load_assets()

        self.tween_list = []
        self.mask_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.mask_circle_radius = 0

        self.ready = True
        utils.sound_play(sound=sfx.woop_out, volume=self.game.sfx_volume)

        self.transitioning = True
        self.freeze_frame = None


    #Main methods

    def load_assets(self):
        
        self.button_list = []
        
        self.setup_start_state=False
        self.play_event_state=False
        #test grid
        self.cell_size = 80
        total_grid_width = self.cell_size * 8
        total_grid_height = self.cell_size * 8
        available_width = constants.canvas_width - (self.box_width * 2)
        self.grid_start_x = self.box_width + (available_width - total_grid_width) // 2
        self.grid_start_y = 8 + (constants.canvas_height - total_grid_height) // 2
        
        # Create hit boxes for each cell
        self.grid_hitboxes = []
        self.grid_buttons = []
        index=0
        for row in range(8):
            for col in range(8):
                cell_x = self.grid_start_x + (col * self.cell_size)
                cell_y = self.grid_start_y + (row * self.cell_size)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                self.grid_hitboxes.append(rect)
                self.grid_buttons.append(Button(
                    game=self.game,
                    id=index,
                    width=self.cell_size,
                    height=self.cell_size,
                    pos=(cell_x, cell_y),
                    pos_anchor='topleft'
                ))
                self.game_board.board.append(Cell(index))
                index += 1
        #/test grid
        
        # Load background
        
        self.landscape_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.light_grass_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.light_grass).values())
        self.light_grass_textured_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.light_grass_textured).values())
        self.light_grass_flowers_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.light_grass_flowers).values())
        self.dark_grass_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.dark_grass).values())
        self.dark_grass_textured_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.dark_grass_textured).values())
        self.dark_grass_flowers_sprites = list(utils.get_sprite_sheet(sprite_sheet=spritesheets.dark_grass_flowers).values())
        
        self.plain_grass_frequency = math.ceil(2 / len(self.light_grass_sprites))
        self.textured_grass_frequency = math.ceil(3 / len(self.light_grass_textured_sprites))
        self.flowers_frequency = math.ceil(4 / len(self.light_grass_flowers_sprites))

        self.light_grass_choices = (self.plain_grass_frequency * self.light_grass_sprites
                                    + self.textured_grass_frequency * self.light_grass_textured_sprites
                                    + self.flowers_frequency * self.light_grass_flowers_sprites)
        self.dark_grass_choices = (self.plain_grass_frequency * self.dark_grass_sprites
                                    + self.textured_grass_frequency * self.dark_grass_textured_sprites
                                    + self.flowers_frequency * self.dark_grass_flowers_sprites)

        random.seed(None)

        for i in [1008, 0]:
            for j in [0, 384]:
                for x in range(i, i + 272, 16):
                    for y in range(j, j + 336, 16):
                        utils.blit(dest=self.landscape_surface, source=random.choice(self.light_grass_choices), pos=(x, y))

        self.plain_grass_frequency = math.ceil(200 / len(self.light_grass_sprites))
        self.textured_grass_frequency = math.ceil(45 / len(self.light_grass_textured_sprites))
        self.flowers_frequency = math.ceil(8 / len(self.light_grass_flowers_sprites))

        self.light_grass_choices = (self.plain_grass_frequency * self.light_grass_sprites
                                    + self.textured_grass_frequency * self.light_grass_textured_sprites
                                    + self.flowers_frequency * self.light_grass_flowers_sprites)
        self.dark_grass_choices = (self.plain_grass_frequency * self.dark_grass_sprites
                                    + self.textured_grass_frequency * self.dark_grass_textured_sprites
                                    + self.flowers_frequency * self.dark_grass_flowers_sprites)

        for x in range(304, 976, 16):
            for y in range(32, 704, 16):
                cell_x = x//80
                cell_y = (y+32)//80
                if (cell_x + cell_y) % 2 == 0:
                    utils.blit(dest=self.landscape_surface, source=random.choice(self.dark_grass_choices), pos=(x, y))
                else:
                    utils.blit(dest=self.landscape_surface, source=random.choice(self.light_grass_choices), pos=(x, y))

        random.seed(self.seed)

        self.landscape_list = [
            # {
            #     'image': utils.get_image(dir=dir.play_bg, name='grass_pattern.png', mode='colorkey'),
            # },
            # {
            #     'image': utils.get_image(dir=dir.play_bg, name='water_low.png', mode='colorkey'),
            # },
            # {
            #     'image': utils.get_image(dir=dir.play_bg, name='water_high.png', mode='colorkey'),
            # },
            {
                'image': utils.get_image(dir=dir.play_bg, name='trees_bridges.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='fence.png', mode='colorkey'),
            },
        ]

        self.water_low_image = utils.get_image(dir=dir.play_bg, name='water_low.png', mode='colorkey')
        self.water_high_image = utils.get_image(dir=dir.play_bg, name='water_high.png', mode='colorkey')

        self.water_is_high = True
        self.water_timer = pygame.USEREVENT + 1
        self.timer_manager = TimerManager()
        self.timer_manager.StartTimer(self.water_timer, 1500)

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
            {'text': 'Total', 'color': colors.green_light, 'amount': self.total_score},
        ]

        self.score_title_list = []
        for score in self.score_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='tiny', color=score['color'])
            self.score_title_list.append(text)

        self.score_amount_list = []
        for score in self.score_list:
            amount = utils.get_text(text=str(score['amount']), font=fonts.lf2, size='small', color=score['color'])
            self.score_amount_list.append(amount)

        self.left_box_strike = utils.get_text(text='Event Strikes', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_task = utils.get_text(text='Current task', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_path_text = utils.get_text(text='Place drawn path', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_event_text = utils.get_text(text='Play drawn event', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_magic_event_text = utils.get_text(text='Play magic fruit event', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_draw_text = utils.get_text(text='Draw a card', font=fonts.lf2, size='tiny', color=colors.white)

        self.blank_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_blank')
        self.live_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_live')
        self.scaled_live_strike = pygame.transform.scale_by(surface=self.live_strike_image, factor=0.625)
        self.scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)

        # right gui
        self.right_box_title = utils.get_text(text='Cards', font=fonts.lf2, size='small', color=colors.white)

        self.deck_list = [
            {'text': 'Fruit',},
            {'text': 'Path',},
            {'text': 'Event',},
        ]

        self.deck_title_list = []
        for score in self.deck_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='tiny', color=colors.white)
            self.deck_title_list.append(text)

        self.right_remaining = utils.get_text(text='Remaining', font=fonts.lf2, size='tiny', color=colors.white)
        self.right_magic_fruits = utils.get_text(text='Magic Fruits', font=fonts.lf2, size='small', color=colors.white)

        self.next_text = utils.get_text(text='Next', font=fonts.lf2, size='tiny', color=colors.white)
        self.event_text = utils.get_text(text='event', font=fonts.lf2, size='tiny', color=colors.white)
        self.path_text = utils.get_text(text='path', font=fonts.lf2, size='tiny', color=colors.white)

        # dirt path
        self.dirt_sprite_1 = []
        self.dirt_sprite_2 = []
        self.dirt_sprite_3 = []
        self.dirt_sprite_4 = []
        self.dirt_sprite_5 = []
        self.dirt_sprite_6 = []
        self.dirt_sprite_7 = []
        self.dirt_sprite_8 = []
        self.dirt_sprite_9 = []
        for _ in self.grid_hitboxes:
            self.dirt_sprite_1.append(self.random_dirt())  
            self.dirt_sprite_2.append(self.random_dirt())
            self.dirt_sprite_3.append(self.random_dirt())
            self.dirt_sprite_4.append(self.random_dirt())
            self.dirt_sprite_5.append(self.random_dirt())
            self.dirt_sprite_6.append(self.random_dirt())
            self.dirt_sprite_7.append(self.random_dirt())
            self.dirt_sprite_8.append(self.random_dirt())
            self.dirt_sprite_9.append(self.random_dirt())

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
        self.magic_fruit1_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_1')
        self.magic_fruit2_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_2')
        self.magic_fruit3_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_3')
        self.magic_fruit_shadow = utils.get_sprite(sprite_sheet=spritesheets.magic_fruit_shadow, target_sprite='magic_fruit_shadow', mode='alpha')

        self.home = utils.get_sprite(sprite_sheet=spritesheets.home, target_sprite='home', mode='alpha')
        
        self.endDayState=False

        # path
        self.path_WE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE')
        self.path_NS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS')
        self.path_NW_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW')
        self.path_NE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE')
        self.path_WS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS')
        self.path_ES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES')
        self.path_NWE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NWE')
        self.path_NWS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NWS')
        self.path_NES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NES')
        self.path_WES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WES')
        self.path_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_strike')

        self.event_free_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_free')
        self.event_keep_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_keep')
        self.event_merge_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_merge')
        self.event_point_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_point')
        self.event_redraw_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_redraw')
        self.event_remove_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_remove')
        self.event_reveal_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_reveal')
        self.event_swap_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_swap')

        # fruits
        self.fruit_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.fruit_16x16)
        self.big_fruit_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.fruit_32x32)
        self.fruit_shadow = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='fruit_shadow', mode="alpha")
        
        
        # gui
        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile', mode='alpha')
        self.cant_selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='cant_selecting_tile', mode='alpha')
        self.selected_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selected_tile')
        self.small_selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='small_selecting_tile')
        self.path_WE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE')
        self.path_NS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS')
        self.path_NW_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW')
        self.path_NE_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE')
        self.path_WS_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS')
        self.path_ES_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES')
        
        # cards
        self.card_fruit_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite='card_fruit_back')
        self.card_path_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite='card_path_back')
        self.card_event_back_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite='card_event_back')
        self.cards_fruit_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.cards_fruit)
        self.cards_path_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.cards_path)
        self.cards_event_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.cards_event)
        self.pop_up_revealed_event_card = None
        for i in range(3):
            self.button_list.append(Button(
                game=self.game,
                id=f'revealed_event_{i+1}',
                surface=self.card_fruit_back_image,
                pos=(1025+i*70, 555+i*10),
                pos_anchor='topleft',
                hover_cursor=cursors.hand,
            ))
        self.button_list.append(Button(
            game=self.game,
            id='event_card',
            surface=self.card_fruit_back_image,
            pos=(self.box_width/2, 640),
            pos_anchor='center',
            hover_cursor=cursors.hand,))
        #fix
        self.end_game=False

        # wind
        self.wind_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.wind_entities_list = []
        self.wind_spawn_rate_per_second = 0.5
        self.wind_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.wind, mode='alpha')
        for wind_sprite in self.wind_sprites:
            self.wind_sprites[wind_sprite] = pygame.transform.scale_by(self.wind_sprites[wind_sprite], (2, 1))

        # music
        self.songs = [
            music.play_1,
            music.play_2,
            music.play_3,
            music.play_4,
            music.play_5,
            music.play_6,
            music.play_7,
            music.play_8,
        ]
        random.seed(None)
        random.shuffle(self.songs)
        random.seed(self.seed)

        utils.music_load(music_channel=self.game.music_channel, name=self.songs[0])
        self.music_end_event = pygame.USEREVENT + 2
        pygame.mixer.music.set_endevent(self.music_end_event)
        self.current_song = 0
        self.game.music_channel.play()

        # pause
        self.paused = False
        self.pause_background = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.pause_background.fill((*colors.black, 200))
        self.pause_title = utils.get_text(text='Paused', font=fonts.lf2, size='huge', color=colors.mono_205)
        self.pause_options = [
            {
                'id': 'resume',
                'text': 'Resume',
            },
            {
                'id': 'quit',
                'text': 'Exit to menu',
            }
        ]
        self.pause_options_surface_list = []
        self.pause_options_button_list = []
        for i, option in enumerate(self.pause_options):
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.pause_options_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1,
            })
            self.pause_options_button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=300,
                height=80,
                pos=(constants.canvas_width/2, constants.canvas_height/2 + i*80),
                pos_anchor='center'
            ))
    

    def update(self, dt, events):
        tween.update(passed_time=dt)
        if self.ready:

            if self.paused:
                for button in self.pause_options_button_list:
                    button.update(dt=dt, events=events)
                    if button.hovered:
                        self.cursor = button.hover_cursor
                        for option in self.pause_options_surface_list:
                            if button.id == option['id']:
                                option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                    else:
                        for option in self.pause_options_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                    if button.clicked:
                        if button.id == 'resume':
                            utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                            self.paused = False
                        elif button.id == 'quit':
                            self.transitioning = True
                            self.game.music_channel.fadeout(1500)
                            utils.sound_play(sound=sfx.woop_in, volume=self.game.sfx_volume)
                            self.freeze_frame = self.game.canvas.copy()
                            def on_complete():
                                utils.music_load(music_channel=self.game.music_channel, name=music.menu_intro)
                                utils.music_queue(music_channel=self.game.music_channel, name=music.menu_loop, loops=-1)
                                self.game.music_channel.play()
                                self.timer_manager.StopTimer(self.water_timer)
                                self.tween_list.clear()
                                self.game.state_stack.clear()
                            self.tween_list.append(tween.to(
                                container=self,
                                key='mask_circle_radius',
                                end_value=0,
                                time=1,
                                ease_type=tweencurves.easeOutQuint
                            ).on_complete(on_complete))

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                            self.paused = not self.paused
                            
                utils.set_cursor(cursor=self.cursor)
                self.cursor = cursors.normal

            else: 
                # Update substates
                if self.substate_stack:
                    self.substate_stack[-1].update(dt=dt, events=events)

                # Update winds
                for wind in self.wind_entities_list:
                    if wind.active:
                        wind.update(dt=dt, events=[])
                    else:
                        self.wind_entities_list.remove(wind)

                spawn_rate = self.wind_spawn_rate_per_second * dt
                spawns = int(spawn_rate)
                spawn_chance = spawn_rate - spawns
                for _ in range(spawns):
                    self.wind_entities_list.append(Wind(surface=self.wind_surface, sprites=self.wind_sprites))

                if random.random() <= spawn_chance:
                    self.wind_entities_list.append(Wind(surface=self.wind_surface, sprites=self.wind_sprites))

                # update buttons
                for button in self.grid_buttons:
                    button.update(dt=dt, events=events)

                for button in self.button_list:
                    button.update(dt=dt, events=events)

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
                elif self.magic_eventing:
                    Play_PlayMagicEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.magic_eventing = False
                elif self.is_strike and not self.magic_eventing:
                    Play_DrawEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.is_strike = False
                elif self.eventing:
                    self.play_event_state = True
                    Play_PlayEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.eventing = False
                elif self.endDayState and not self.end_game:
                    Play_NextDayState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.endDayState = False
                elif self.is_3_strike and self.current_day <= self.day:
                    Play_EndDayState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.is_3_strike = False 
                    print("endgame status: ", self.end_game)
                elif self.end_game:
                    Play_ResultStage(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.end_game = False

                if not self.transitioning:
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                                self.paused = not self.paused
                        elif event.type == self.water_timer:
                            self.water_is_high = not self.water_is_high
                        elif event.type == self.music_end_event:
                            self.current_song += 1
                            if self.current_song >= len(self.songs):
                                self.current_song = 0
                            utils.music_load(music_channel=self.game.music_channel, name=self.songs[self.current_song])
                            self.game.music_channel.play()        

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
                
                if self.current_day < 2:
                    self.final_day1_score = self.day1_score + (self.game_board.board_eval(today_fruit=self.day1_fruit) if self.day1_fruit is not None else 0)
                if self.current_day < 3:
                    self.final_day2_score = self.day2_score + (self.game_board.board_eval(today_fruit=self.day2_fruit) if self.day2_fruit is not None else 0)
                if self.current_day < 4:
                    self.final_day3_score = self.day3_score + (self.game_board.board_eval(today_fruit=self.day3_fruit) if self.day3_fruit is not None else 0)
                if self.current_day < 5:
                    self.final_day4_score = self.day4_score + (self.game_board.board_eval(today_fruit=self.day4_fruit) if self.day4_fruit is not None else 0)
                self.final_seasonal_score = self.seasonal_score + (self.game_board.board_eval(today_fruit=self.seasonal_fruit) if self.seasonal_fruit is not None else 0)
                self.total_score = self.final_day1_score + self.final_day2_score + self.final_day3_score + self.final_day4_score + self.final_seasonal_score
                

                self.score_list = [
                    {'text': 'Day 1', 'color': day_colors['day1_color'], 'amount': self.final_day1_score},
                    {'text': 'Day 2', 'color': day_colors['day2_color'], 'amount': self.final_day2_score},
                    {'text': 'Day 3', 'color': day_colors['day3_color'], 'amount': self.final_day3_score},
                    {'text': 'Day 4', 'color': day_colors['day4_color'], 'amount': self.final_day4_score},
                    {'text': 'Seasonal', 'color': colors.yellow_light, 'amount': self.final_seasonal_score},
                    {'text': 'Total', 'color': colors.green_light, 'amount': self.total_score},
                ]

                self.score_title_list = []
                for score in self.score_list:
                    text = utils.get_text(text=score['text'], font=fonts.lf2, size='tiny', color=score['color'])
                    self.score_title_list.append(text)

                self.score_amount_list = []
                for score in self.score_list:
                    amount = utils.get_text(text=str(score['amount']), font=fonts.lf2, size='small', color=score['color'])
                    self.score_amount_list.append(amount)

                # hover function 
                if self.setup_start_state==True:
                    top_card = None
                    self.pop_up_revealed_event_card = 0
                    for button in reversed(self.button_list):
                        if button.hovered:
                            if button.id == 'revealed_event_3':
                                top_card = 3
                                self.pop_up_revealed_event_card = 3
                                break
                            elif button.id == 'revealed_event_2'and top_card != 3:
                                top_card = 2
                                self.pop_up_revealed_event_card = 2
                                break
                            elif button.id == 'revealed_event_1' and top_card != 2:
                                top_card = 1
                                self.pop_up_revealed_event_card = 1
                                break
                    if self.play_event_state == True:
                        for button in self.button_list:
                            if button.hovered:
                                if button.id == 'event_card':
                                    self.pop_up_revealed_event_card = 4
                                    break
                

    def render(self, canvas):


        if self.ready:

            # Render graphics
            utils.blit(dest=canvas, source=self.landscape_surface)

            if self.water_is_high:
                utils.blit(dest=canvas, source=self.water_high_image)
            else:
                utils.blit(dest=canvas, source=self.water_low_image)
            
            for layer in self.landscape_list:
                utils.blit(dest=canvas, source=layer['image'], pos=(0, 0))
                
            utils.draw_rect(dest=canvas,
                                size=(self.box_width, constants.canvas_height),
                                pos=(0, 0),
                                pos_anchor='topleft',
                                color=(*colors.white, 175), # 75% transparency
                                inner_border_width=4,
                                outer_border_width=0,
                                outer_border_color=colors.black)
            
            # Render board

            ## Render path on placed tile
            for i, rect in enumerate(self.grid_hitboxes):
                if ((i // 8) + (i % 2)) % 2 == 0:
                    if self.game_board.board[i].temp:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.grass_light_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                    elif self.game_board.board[i].home:
                            #home render
                            #render dirt and grass
                            #1*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #2*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #3*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_light_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #4*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #5*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            
                            #1*2
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            #5*2
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            
                            #1*3
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_light_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            #5*3
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_light_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')   
                            
                            #1*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            #3*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            #5*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')  
                            
                            #1*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #2*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #3*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_light_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #4*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #5*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                        
                            utils.blit(dest=canvas, source=self.home, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                    else:
                        #path 2 directions
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_S, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i-1)//8] and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else: 
                                utils.blit(dest=canvas, source=self.grass_light_path_E, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i+1)//8] and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_W, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i <= 55 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_light_path_N, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        
                        #path 3 directions
                        if (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_light_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                else:
                    if self.game_board.board[i].temp:
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        utils.blit(dest=canvas, source=self.grass_dark_path_none, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                    elif self.game_board.board[i].home:
                            #render dirt and grass
                            #1*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #2*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #3*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_dark_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #4*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            #5*1
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            
                            #1*2
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            #5*2
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                            
                            #1*3
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_dark_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            #5*3
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')

                            if i >= 8 and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_dark_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')   
                            
                            #1*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            #3*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')
                            #5*4
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+48), pos_anchor='topleft')  
                            
                            #1*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #2*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #3*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                    utils.blit(dest=canvas, source=self.grass_dark_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #4*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+48, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            #5*5
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                        
                            utils.blit(dest=canvas, source=self.home, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+16, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
                    else:
                        
                        if self.game_board.board[i].north:
                            utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_S, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                        if self.game_board.board[i].west:
                            utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i-1)//8] and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:    
                                utils.blit(dest=canvas, source=self.grass_dark_path_E, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].east:
                            utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            if self.game_board.board[i//8] == self.game_board.board[(i+1)//8] and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_W, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 64, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        if self.game_board.board[i].south:
                            utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            if i <= 55 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                                utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            else:
                                utils.blit(dest=canvas, source=self.grass_dark_path_N, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 64), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        if (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NWS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].west):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NW, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].north and 
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].east):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].west and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_WS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                        elif (self.game_board.board[i].east and
                            self.game_board.board[i].south):
                            utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            utils.blit(dest=canvas, source=self.grass_dark_path_ES, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')

                ## Render Magic Fruit
                if self.game_board.board[i].magic_fruit == 1:
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit1_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')
                if self.game_board.board[i].magic_fruit == 2:
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit2_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')
                if self.game_board.board[i].magic_fruit == 3:
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit3_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')

                ## Render Fruits
                if self.game_board.board[i].fruit:
                    for pos, fruit in enumerate(self.game_board.board[i].fruit):
                        if fruit != None:
                            fruit_image = self.big_fruit_sprites[fruit]
                            if pos == 0:
                                utils.blit(dest=canvas, source=self.fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                                utils.blit(dest=canvas, source=fruit_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                            if pos == 1:
                                utils.blit(dest=canvas, source=self.fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                                utils.blit(dest=canvas, source=fruit_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                            if pos == 2:
                                utils.blit(dest=canvas, source=self.fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                                utils.blit(dest=canvas, source=fruit_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            if pos == 3:
                                utils.blit(dest=canvas, source=self.fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                                utils.blit(dest=canvas, source=fruit_image, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')


            # Render wind
            self.wind_surface.fill((0, 0, 0, 0))
            for wind in self.wind_entities_list:
                wind.render()
            utils.blit(dest=canvas, source=self.wind_surface)
            

            # Render gui

            ## Render text in left white box
            utils.blit(dest=canvas, source=self.left_box_title, pos=(self.box_width/2, 35), pos_anchor='center')
            for i, score in enumerate(self.score_title_list):
                utils.blit(dest=canvas, source=score, pos=(70, 83 + i*45), pos_anchor='midleft')
            utils.blit(dest=canvas, source=self.left_box_strike, pos=(self.box_width/2, 370), pos_anchor='center')
            utils.blit(dest=canvas, source=self.left_box_task, pos=(self.box_width/2, 500), pos_anchor='center')

            ## Render value in left white box
            for i, score in enumerate(self.score_amount_list):
                utils.blit(dest=canvas, source=score, pos=(240, 80 + i*45), pos_anchor='midright')

            ## Render strike in left white box
            for i in range(self.strikes):
                    utils.blit(dest=canvas, source=self.scaled_live_strike, pos=(40 + i*64, 400), pos_anchor='topleft')
            for i in range(3 - self.strikes):
                    utils.blit(dest=canvas, source=self.scaled_blank_strike, pos=(40 + i*64 + self.strikes*64, 400), pos_anchor='topleft')
            ## Render current task image
            if self.current_path:
                self.current_path_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite=f"card_{self.current_path}")
                utils.blit(dest=canvas, source=self.current_path_image, pos=(self.box_width/2, 640), pos_anchor='center')
                utils.blit(dest=canvas, source=self.left_box_path_text, pos=(self.box_width/2, 535), pos_anchor='center')
            elif self.current_event and self.playing_magic_event:
                self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                utils.blit(dest=canvas, source=self.current_event_image, pos=(self.box_width/2, 640), pos_anchor='center')
                utils.blit(dest=canvas, source=self.left_box_magic_event_text, pos=(self.box_width/2, 535), pos_anchor='center')
            elif self.current_event:
                self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                utils.blit(dest=canvas, source=self.current_event_image, pos=(self.box_width/2, 640), pos_anchor='center')
                utils.blit(dest=canvas, source=self.left_box_event_text, pos=(self.box_width/2, 535), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.left_box_draw_text, pos=(self.box_width/2, 535), pos_anchor='center')

            ## Render Day's Fruit
            if self.day1_fruit:
                if self.current_day == 1:
                    self.day1_fruit_image = self.big_fruit_sprites['big_'+self.day1_fruit]
                else:
                    self.day1_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day1_fruit])
                utils.blit(dest=canvas, source=self.day1_fruit_image, pos=(45, 83), pos_anchor='center')
            if self.day2_fruit:
                if self.current_day == 2:
                    self.day2_fruit_image = self.big_fruit_sprites['big_'+self.day2_fruit]
                else:
                    self.day2_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day2_fruit])
                utils.blit(dest=canvas, source=self.day2_fruit_image, pos=(45, 128), pos_anchor='center')
            if self.day3_fruit:
                if self.current_day == 3:
                    self.day3_fruit_image = self.big_fruit_sprites['big_'+self.day3_fruit]
                else:
                    self.day3_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day3_fruit])
                utils.blit(dest=canvas, source=self.day3_fruit_image, pos=(45, 173), pos_anchor='center')
            if self.day4_fruit:
                if self.current_day == 4:
                    self.day4_fruit_image = self.big_fruit_sprites['big_'+self.day4_fruit]
                else:
                    self.day4_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day4_fruit])
                utils.blit(dest=canvas, source=self.day4_fruit_image, pos=(45, 218), pos_anchor='center')
            if self.seasonal_fruit:
                self.seasonal_fruit_image = self.big_fruit_sprites['big_'+self.seasonal_fruit]
                utils.blit(dest=canvas, source=self.seasonal_fruit_image, pos=(45, 263), pos_anchor='center')

            
            ## Render right white box
            utils.draw_rect(dest=canvas,
                                size=(self.box_width, constants.canvas_height),
                                pos=(constants.canvas_width - self.box_width, 0),
                                pos_anchor='topleft',
                                color=(*colors.white, 175), # 75% transparency
                                inner_border_width=4,
                                outer_border_width=0,
                                outer_border_color=colors.black)
            
            ## Render text in right white box
            utils.blit(dest=canvas, source=self.right_box_title, pos=(constants.canvas_width - self.box_width/2, 35), pos_anchor='center')
            for i, deck in enumerate(self.deck_title_list):
                utils.blit(dest=canvas, source=deck, pos=(1145, 85 + i*135), pos_anchor='topleft')
                utils.blit(dest=canvas, source=self.right_remaining, pos=(1145, 110 + i*135), pos_anchor='topleft')

            ## Render value in right white box
            self.fruit_deck_remaining_amount = utils.get_text(text=str(self.fruit_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
            utils.blit(dest=canvas, source=self.fruit_deck_remaining_amount, pos=(1145, 135), pos_anchor='topleft')
            self.path_deck_remaining_amount = utils.get_text(text=str(self.path_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
            utils.blit(dest=canvas, source=self.path_deck_remaining_amount, pos=(1145, 270), pos_anchor='topleft')
            self.event_deck_remaining_amount = utils.get_text(text=str(self.event_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
            utils.blit(dest=canvas, source=self.event_deck_remaining_amount, pos=(1145, 405), pos_anchor='topleft')

            ## Render image in right white box
            utils.blit(dest=canvas, source=self.card_fruit_back_image, pos=(1130, 65), pos_anchor='topright')
            utils.blit(dest=canvas, source=self.card_path_back_image, pos=(1130, 200), pos_anchor='topright')
            utils.blit(dest=canvas, source=self.card_event_back_image, pos=(1130, 335), pos_anchor='topright')

            ## Render Magic Fruit Event cards
            utils.blit(dest=canvas, source=self.right_magic_fruits, pos=(constants.canvas_width - self.box_width/2, 500), pos_anchor='center')
            if self.magic_fruit1_event:
                self.magic_fruit1_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit1_event}")
                utils.blit(dest=canvas, source=self.magic_fruit1_event_image, pos=(1025, 555), pos_anchor='topleft')
                utils.blit(
                    dest=canvas,
                    source=self.magic_fruit1_image,
                    pos=(1025 + 48, 555 - 26),
                    pos_anchor='midtop'
                )
            if self.magic_fruit2_event:
                self.magic_fruit2_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit2_event}")
                utils.blit(dest=canvas, source=self.magic_fruit2_event_image, pos=(1095, 565), pos_anchor='topleft')
                utils.blit(
                    dest=canvas,
                    source=self.magic_fruit2_image,
                    pos=(1095 + 48, 565 - 26),
                    pos_anchor='midtop'
                )
            if self.magic_fruit3_event:
                self.magic_fruit3_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit3_event}")
                utils.blit(dest=canvas, source=self.magic_fruit3_event_image, pos=(1165, 575), pos_anchor='topleft')
                utils.blit(
                    dest=canvas,
                    source=self.magic_fruit3_image,
                    pos=(1165 + 48, 575 - 26),
                    pos_anchor='midtop'
                )
                        

            # Render Revealed card
            if len(self.revealed_path) > 0:
                utils.draw_rect(dest=canvas,
                                    size=(64, len(self.revealed_path)*60),
                                    pos=(constants.canvas_width - self.box_width + 4, constants.canvas_height),
                                    pos_anchor='bottomright',
                                    color=(*colors.white, 175), # 75% transparency
                                    inner_border_width=4,
                                    outer_border_width=0,
                                    outer_border_color=colors.black)
                
                for i, card in enumerate(self.revealed_path):
                    utils.blit(dest=canvas, source=getattr(self, f'{card.card_name}_image'), pos=(constants.canvas_width - self.box_width - 4, constants.canvas_height - 6 - i*58), pos_anchor='bottomright')
                    if card.strike:
                        utils.blit(dest=canvas, source=self.path_strike_image, pos=(constants.canvas_width - self.box_width - 4, constants.canvas_height - 6 - i*58), pos_anchor='bottomright')
                utils.blit(dest=canvas, source=self.next_text, pos=(constants.canvas_width - self.box_width - 28, constants.canvas_height - 6 - i*58 - 94), pos_anchor='center')
                utils.blit(dest=canvas, source=self.path_text, pos=(constants.canvas_width - self.box_width - 28, constants.canvas_height - 6 - i*58 - 74), pos_anchor='center')
            
            if len(self.revealed_event) > 0:
                utils.draw_rect(dest=canvas,
                                    size=(64, len(self.revealed_event)*60),
                                    pos=(constants.canvas_width - self.box_width + 4, 0),
                                    pos_anchor='topright',
                                    color=(*colors.white, 175), # 75% transparency
                                    inner_border_width=4,
                                    outer_border_width=0,
                                    outer_border_color=colors.black)
                
                for i, card in enumerate(self.revealed_event):
                    utils.blit(dest=canvas, source=getattr(self, f'{card.card_name}_image'), pos=(constants.canvas_width - self.box_width - 4, 6 + i*58), pos_anchor='topright')
                utils.blit(dest=canvas, source=self.next_text, pos=(constants.canvas_width - self.box_width - 28, 6 + i*58 + 72), pos_anchor='center')
                utils.blit(dest=canvas, source=self.event_text, pos=(constants.canvas_width - self.box_width - 28, 6 + i*58 + 92), pos_anchor='center')

            if not self.substate_stack:
                pass

            else:
                self.substate_stack[-1].render(canvas=canvas)       
            
            #hover function
            if self.setup_start_state and not self.end_game:
                # for button in self.button_list:
                #     button.render(canvas=canvas)
                if self.pop_up_revealed_event_card == 3:
                    self.magic_fruit3_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit3_event}")
                    scaled_image = pygame.transform.scale_by(surface=self.magic_fruit3_event_image, factor=3)
                    utils.blit(dest=canvas, source=scaled_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
                elif self.pop_up_revealed_event_card == 2:
                    self.magic_fruit2_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit2_event}")
                    scaled_image = pygame.transform.scale_by(surface=self.magic_fruit2_event_image, factor=3)
                    utils.blit(dest=canvas, source=scaled_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
                elif self.pop_up_revealed_event_card == 1:
                    self.magic_fruit1_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit1_event}")
                    scaled_image = pygame.transform.scale_by(surface=self.magic_fruit1_event_image, factor=3)
                    utils.blit(dest=canvas, source=scaled_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
                if self.play_event_state == True:
                    if self.pop_up_revealed_event_card == 4:
                        #self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                        scaled_image = pygame.transform.scale_by(surface=self.current_event_image, factor=3)
                        utils.blit(dest=canvas, source=scaled_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')

        # pause menu
        if self.paused:
            utils.blit(dest=canvas, source=self.pause_background)
            utils.blit(dest=canvas, source=self.pause_title, pos=(constants.canvas_width/2, 200), pos_anchor='center')
            for i, option in enumerate(self.pause_options_surface_list):
                scaled_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                utils.blit(
                    dest=canvas,
                    source=scaled_surface,
                    pos=(constants.canvas_width/2, constants.canvas_height/2 + i*80),
                    pos_anchor='center'
                )

        if self.transitioning:
            # transition mask 
            if self.freeze_frame is not None:
                utils.blit(dest=canvas, source=self.freeze_frame)
            self.mask_surface.fill(color=colors.black)
            pygame.draw.circle(
                surface=self.mask_surface,
                color=(*colors.black, 0),
                center=(constants.canvas_width/2, constants.canvas_height/2),
                radius=self.mask_circle_radius
            )
            utils.blit(dest=canvas, source=self.mask_surface)

                
    def random_dirt(self):
        return utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite=f"dirt_{random.randint(1, 9)}")