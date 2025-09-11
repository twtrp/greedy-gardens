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
from src.classes.SettingsManager import SettingsManager
import tween
import math

class PlayState(BaseState):
    def __init__(self, game, parent, stack, seed):
        BaseState.__init__(self, game, parent, stack, seed)

        self.ready = False

        if seed == '':
            self.set_seed = False
            self.seed = random.randint(0, 999999)
        else:
            self.set_seed = True
            self.seed = int(seed)

        print('Seed:',self.seed)

        self.game.canvas.fill((0, 0, 0))

        # config of gui
        self.box_width = 272
        self.revealed_event_button_width = 52
        self.revealed_event_button_height = 58
        self.revealed_event_button_y_base = 4    
        self.revealed_event_button_y_spacing = 58

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
        
        # Penalty flags to prevent score recalculation after penalty applied
        self.day1_penalty_applied = False
        self.day2_penalty_applied = False
        self.day3_penalty_applied = False
        self.day4_penalty_applied = False
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
        self.magic_fruit_queue = []  # Queue for multiple magic fruits: [(magic_number, cell_pos), ...]

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
        self.drawing_path_card = False
        self.drawing_event_card = False
        # self.day1 = True
        # self.day2 = False
        # self.day3 = False
        # self.day4 = False
        self.day = 4
        self.current_day = 1
        self.strikes = 0
        self.is_striking = False
        self.current_turn = 0

        # Developer mode
        self.developer_mode = True  # Set to True to enable, False to disable
        
        # Developer mode alert system
        self.dev_alert_text = ""
        self.dev_alert_timer = 0.0
        self.dev_alert_duration = 2.0  # Show alert for 2 seconds

        self.tween_list = []
        self.mask_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.mask_circle_radius = 0

        # HUD transition properties
        self.hud_left_alpha = 0.0
        self.hud_right_alpha = 0.0
        self.hud_transition_complete = False

        # Score animation properties
        self.previous_scores = [0, 0, 0, 0, 0, 0]  # Track previous scores to detect changes
        self.score_scales = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  # Scale for each score (Day1, Day2, Day3, Day4, Seasonal, Total)
        
        # Deck count animation properties
        self.previous_deck_counts = [0, 0, 0]  # Track previous deck counts (fruit, path, event)
        self.deck_scales = [1.0, 1.0, 1.0]  # Scale for each deck count
        
        # Current task text animation properties
        self.previous_task_state = ""  # Track previous task state to detect changes
        self.task_text_scale = 1.0  # Scale for current task text
        
        # Strike animation properties
        self.previous_strikes = 0  # Track previous strikes to detect changes
        self.strike_scales = [1.0, 1.0, 1.0]  # Scale for each strike (up to 3 strikes)
        
        # Current task card animation properties
        self.previous_current_path = None  # Track previous current path to detect changes
        self.previous_current_event = None  # Track previous current event to detect changes
        self.current_task_card_scale = 1.0  # Scale for current task card
        
        # Day fruit animation properties
        self.previous_day1_fruit = None  # Track previous day 1 fruit
        self.previous_day2_fruit = None  # Track previous day 2 fruit
        self.previous_day3_fruit = None  # Track previous day 3 fruit
        self.previous_day4_fruit = None  # Track previous day 4 fruit
        self.previous_seasonal_fruit = None  # Track previous seasonal fruit
        self.day_fruit_scales = [1.0, 1.0, 1.0, 1.0, 1.0]  # Scale for each day fruit (Day1, Day2, Day3, Day4, Seasonal)

        self.transitioning = True
        self.freeze_frame = None

        self.shown_day_title = False
        self.music_started = False

        self.is_current_task_event = False
        self.is_choosing = False

        self.paused = False
        self.in_tutorial = False
        self._tutorial_just_exited = False

        self.load_assets()

        self.ready = True
        utils.sound_play(sound=sfx.woop_out, volume=self.game.sfx_volume)

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
                    pos_anchor='topleft',
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
        self.flowers_frequency = math.ceil(12 / len(self.light_grass_flowers_sprites))

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
            {
                'image': utils.get_image(dir=dir.play_bg, name='trees_bridges.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='fence.png', mode='colorkey'),
            },
        ]

        # self.trees_bridges = utils.get_image(dir=dir.play_bg, name='trees_bridges.png', mode='colorkey')
        # fence = utils.get_image(dir=dir.play_bg, name='fence.png', mode='colorkey')

        # utils.blit(dest=self.landscape_surface, source=trees_bridges, pos=(0, 0))
        # utils.blit(dest=self.landscape_surface, source=fence, pos=(0, 0))

        light_fruit_hole = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='fruit_hole_light_green')
        dark_fruit_hole = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='fruit_hole_dark_green')

        # Fruit holes
        for i, rect in enumerate(self.grid_hitboxes):
            if ((i % 16) // 8) == 0:
                if i % 2 == 0:
                    fruit_hole = light_fruit_hole
                else:
                    fruit_hole = dark_fruit_hole
            else:
                if i % 2 == 0:
                    fruit_hole = dark_fruit_hole
                else:
                    fruit_hole = light_fruit_hole
            if self.game_board.board[i].fruit:
                for pos, fruit in enumerate(self.game_board.board[i].fruit):
                    if fruit != None:
                        if pos == 0:
                            utils.blit(dest=self.landscape_surface, source=fruit_hole, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                        if pos == 1:
                            utils.blit(dest=self.landscape_surface, source=fruit_hole, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 0), pos_anchor='topleft')
                        if pos == 2:
                            utils.blit(dest=self.landscape_surface, source=fruit_hole, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 0, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                        if pos == 3:
                            utils.blit(dest=self.landscape_surface, source=fruit_hole, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')

        self.water_low_image = utils.get_image(dir=dir.play_bg, name='water_low.png', mode='colorkey')
        self.water_high_image = utils.get_image(dir=dir.play_bg, name='water_high.png', mode='colorkey')

        self.water_is_high = True
        self.water_timer = pygame.USEREVENT + 1
        self.timer_manager = TimerManager()
        self.timer_manager.StartTimer(self.water_timer, 1000)

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
        self.left_box_task = utils.get_text(text='Current Task', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_path_text = utils.get_text(text='Place drawn path', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_event_text = utils.get_text(text='Play drawn event', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_magic_event_text = utils.get_text(text='Play magic fruit event', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_draw_path_text = utils.get_text(text='Draw path card', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_draw_event_text = utils.get_text(text='Draw event card', font=fonts.lf2, size='tiny', color=colors.white)
        self.left_box_none_text = utils.get_text(text='Draw seasonal fruit', font=fonts.lf2, size='tiny', color=colors.white)

        self.blank_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_blank')
        self.live_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_live')
        self.scaled_live_strike = pygame.transform.scale_by(surface=self.live_strike_image, factor=0.625)
        self.scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)

        # Event Control Hints
        self.event_free_control_hint = utils.get_text(
            text='Scroll              or press            to choose the path type.',
            font=fonts.lf2, size='tiny', color=colors.white
        )
        self.event_move_control_hint = utils.get_text(
            text='Select a path to move, then select a blank tile to move it to.',
            font=fonts.lf2, size='tiny', color=colors.white
        )
        self.event_merge_control_hint = utils.get_text(
            text='Select 2 paths. Path 1 will be removed and merged with path 2.',
            font=fonts.lf2, size='tiny', color=colors.white
        )
        self.event_remove_control_hint = utils.get_text(
            text='Select 1 or 2 paths. Click Delete button to confirm.',
            font=fonts.lf2, size='tiny', color=colors.white
        )
        self.event_swap_control_hint = utils.get_text(
            text='Select 2 paths to swap their positions.',
            font=fonts.lf2, size='tiny', color=colors.white
        )

        # Event cancelled popup
        self.event_cancelled_popup = utils.get_text(
            text='Impossible event cancelled!',
            font=fonts.lf2, size='tiny', color=colors.red_light
        )
        self.event_cancelled_popup_props = None

        self.mouse_up_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='scroll_up')
        self.mouse_down_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='scroll_down')
        self.mouse_up_sprite = pygame.transform.scale_by(surface=self.mouse_up_sprite, factor=2)
        self.mouse_down_sprite = pygame.transform.scale_by(surface=self.mouse_down_sprite, factor=2)
        self.mouse_hint_surface = pygame.Surface((self.mouse_up_sprite.get_width() + self.mouse_down_sprite.get_width() + 8, self.mouse_up_sprite.get_height()), pygame.SRCALPHA)
        utils.blit(
            dest=self.mouse_hint_surface,
            source=self.mouse_up_sprite,
            pos=(0, 0),
            pos_anchor=posanchors.topleft
        )
        utils.blit(
            dest=self.mouse_hint_surface,
            source=self.mouse_down_sprite,
            pos=(self.mouse_up_sprite.get_width() + 8, 0),
            pos_anchor=posanchors.topleft
        )

        self.key_up_sprite = utils.get_sprite(sprite_sheet=spritesheets.keyboard_keys, target_sprite='up')
        self.key_down_sprite = utils.get_sprite(sprite_sheet=spritesheets.keyboard_keys, target_sprite='down')
        self.key_up_sprite = pygame.transform.scale_by(surface=self.key_up_sprite, factor=2)
        self.key_down_sprite = pygame.transform.scale_by(surface=self.key_down_sprite, factor=2)
        self.key_hint_surface = pygame.Surface((self.key_up_sprite.get_width() + self.key_down_sprite.get_width() + 8, self.key_up_sprite.get_height()), pygame.SRCALPHA)
        utils.blit(
            dest=self.key_hint_surface,
            source=self.key_up_sprite,
            pos=(0, 0),
            pos_anchor=posanchors.topleft
        )
        utils.blit(
            dest=self.key_hint_surface,
            source=self.key_down_sprite,
            pos=(self.key_up_sprite.get_width() + 8, 0),
            pos_anchor=posanchors.topleft
        )

        # Draw card hint
        self.press_text = utils.get_text(text="Press", font=fonts.lf2, size='tiny', color=colors.mono_175)
        self.right_click_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='right_click')
        self.right_click_sprite = pygame.transform.scale_by(surface=self.right_click_sprite, factor=2)
        self.slash_text = utils.get_text(text="/", font=fonts.minecraftia, size='tiny', color=colors.mono_175, long_shadow=False)
        self.spacebar_sprite = utils.get_sprite(sprite_sheet=spritesheets.keyboard_keys_long, target_sprite='spacebar')
        self.spacebar_sprite = pygame.transform.scale_by(surface=self.spacebar_sprite, factor=2)
        combined_width = self.right_click_sprite.get_width() + self.slash_text.get_width() + self.spacebar_sprite.get_width() + 2
        combined_height = max(self.right_click_sprite.get_height(), self.slash_text.get_height(), self.spacebar_sprite.get_height()) + self.press_text.get_height() + 10
        self.draw_card_hint = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        utils.blit(
            dest=self.draw_card_hint,
            source=self.press_text,
            pos=(combined_width//2, 10),
            pos_anchor=posanchors.midtop
        )
        utils.blit(
            dest=self.draw_card_hint,
            source=self.right_click_sprite,
            pos=(0, combined_height//2 + 20),
            pos_anchor=posanchors.midleft
        )
        utils.blit(
            dest=self.draw_card_hint,
            source=self.slash_text,
            pos=(self.right_click_sprite.get_width() + 2, combined_height//2 + 20),
            pos_anchor=posanchors.midleft
        )
        utils.blit(
            dest=self.draw_card_hint,
            source=self.spacebar_sprite,
            pos=(self.right_click_sprite.get_width() + self.slash_text.get_width() + 2, combined_height//2 + 20),
            pos_anchor=posanchors.midleft
        )
        
        self.draw_card_hint_scale_min = 1.0
        self.draw_card_hint_scale_max = 1.25

        self.draw_card_hint_scale = 1.0
        self.draw_card_hint_animation_time = 0.0
        self.draw_card_hint_animation_cycle_duration = 2

        self.right_box_title = utils.get_text(text='Turn 1', font=fonts.lf2, size='small', color=colors.white)

        self.deck_list = [
            {'text': 'Fruit cards',},
            {'text': 'Path cards',},
            {'text': 'Event cards',},
        ]

        self.deck_title_list = []
        for score in self.deck_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='tiny', color=colors.white)
            self.deck_title_list.append(text)

        self.right_remaining = utils.get_text(text='remaining', font=fonts.lf2, size='tiny', color=colors.white)
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

        # grass path #@note
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

        self.grass_light_path_NWE_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NWE_home')
        self.grass_light_path_NWS_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NWS_home')
        self.grass_light_path_NES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NES_home')
        self.grass_light_path_WES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WES_home')
        self.grass_light_path_ES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_ES_home')
        self.grass_light_path_WE_home_N = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WE_home_N')
        self.grass_light_path_WS_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WS_home')
        self.grass_light_path_NS_home_W = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NS_home_W')
        self.grass_light_path_NS_home_E = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NS_home_E')
        self.grass_light_path_NE_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NE_home')
        self.grass_light_path_WE_home_S = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_WE_home_S')
        self.grass_light_path_NW_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_light_path_NW_home')

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

        self.grass_dark_path_NWE_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NWE_home')
        self.grass_dark_path_NWS_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NWS_home')
        self.grass_dark_path_NES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NES_home')
        self.grass_dark_path_WES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WES_home')
        self.grass_dark_path_ES_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_ES_home')
        self.grass_dark_path_WE_home_N = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WE_home_N')
        self.grass_dark_path_WS_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WS_home')
        self.grass_dark_path_NS_home_W = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NS_home_W')
        self.grass_dark_path_NS_home_E = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NS_home_E')
        self.grass_dark_path_NE_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NE_home')
        self.grass_dark_path_WE_home_S = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_WE_home_S')
        self.grass_dark_path_NW_home = utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite='grass_dark_path_NW_home')

        # magic fruit
        self.magic_fruit1_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_1')
        self.magic_fruit2_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_2')
        self.magic_fruit3_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_3')
        self.magic_fruit1_image_small = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_1_small')
        self.magic_fruit2_image_small = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_2_small')
        self.magic_fruit3_image_small = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_3_small')
        self.magic_fruit_shadow = utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_shadow_small', mode="alpha")

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
        self.event_move_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_move')
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
        
        self.button_list.append(Button(
            game=self.game,
            id='magic_fruit_1',
            surface=self.card_fruit_back_image,
            pos=(1073, 619),
            pos_anchor='center',
            hover_cursor=cursors.hand,
        ))
        self.button_list.append(Button(
            game=self.game,
            id='magic_fruit_2',
            surface=self.card_fruit_back_image,
            pos=(1143, 629),
            pos_anchor='center',
            hover_cursor=cursors.hand,
        ))
        self.button_list.append(Button(
            game=self.game,
            id='magic_fruit_3',
            surface=self.card_fruit_back_image,
            pos=(1213, 639),
            pos_anchor='center',
            hover_cursor=cursors.hand,
        ))
        self.button_list.append(Button(
            game=self.game,
            id='event_card',
            surface=self.card_fruit_back_image,
            pos=(self.box_width/2, 630),
            pos_anchor='center',
            hover_cursor=cursors.hand,))
        #fix
        self.end_game=False

        # wind
        self.wind_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.wind_entities_list = []
        self.wind_spawn_rate_per_second = 2
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
            music.play_9,
            music.play_10,
            music.play_11,
            music.play_12,
            music.play_13,
        ]
        random.seed(None)
        random.shuffle(self.songs)
        random.seed(self.seed)

        utils.music_load(music_channel=self.game.music_channel, name=self.songs[0])
        self.music_end_event = pygame.USEREVENT + 2
        pygame.mixer.music.set_endevent(self.music_end_event)
        self.current_song = 0

        self.pause_background = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.pause_background.fill((*colors.white, 200))
        self.pause_title = utils.get_text(text='Paused', font=fonts.lf2, size='huge', color=colors.mono_205)
        
        self.settings_manager = SettingsManager()
        self.current_settings_index = self.settings_manager.load_all_settings_index()
        self.setting_index = 0
        
        # Load arrow graphics
        self.arrow_left = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='arrow_left')
        self.arrow_right = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='arrow_right')
        
        self.pause_settings_surface_list = []
        for i, setting in enumerate(self.settings_manager.settings_list):
            if setting['id'] != 'skip_bootup':
                text_string = setting['label'] + ':  ' + setting['value_label'][self.current_settings_index[i]]
                text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
                self.pause_settings_surface_list.append({
                    'id': setting['id'],
                    'surface': text,
                    'left_arrow_scale': 0,
                    'right_arrow_scale': 0,
                    'settings_list_index': i
                })
        
        self.pause_options = [
            {
                'id': 'resume',
                'text': 'Resume',
            },
            {
                'id': 'how_to_play',
                'text': 'How to Play',
            },
            {
                'id': 'quit',
                'text': 'Exit to menu',
            }
        ]
        self.pause_options_surface_list = []
        self.pause_options_button_list = []
        
        for i, option in enumerate(self.pause_settings_surface_list):
            self.pause_options_button_list.append(Button(
                game=self.game,
                id=option['id'],
                group='setting',
                width=500,
                height=50,
                pos=(constants.canvas_width/2, 370 + i*50),
                pos_anchor='center',
                hover_cursor=None,
                enable_click=False
            ))
            self.pause_options_button_list.append(Button(
                game=self.game,
                id=option['id']+'_left',
                group='arrow',
                width=48,
                height=50,
                pos=(constants.canvas_width/2 - 180, 370 + i*50),
                pos_anchor='center'
            ))
            self.pause_options_button_list.append(Button(
                game=self.game,
                id=option['id']+'_right',
                group='arrow',
                width=48,
                height=50,
                pos=(constants.canvas_width/2 + 180, 370 + i*50),
                pos_anchor='center'
            ))
        
        for i, option in enumerate(self.pause_options):
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.pause_options_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1,
            })
            if i == 0:  # Resume
                y_offset = 225
            elif i == 1:  # How to Play - directly below Resume
                y_offset = 295  # Just below Resume
            else:  # Exit to menu - after settings panel (moved down)
                y_offset = 370 + 5*50 + 30  # Moved down from 295 to 370
            self.pause_options_button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=300,
                height=70,
                pos=(constants.canvas_width/2, y_offset),
                pos_anchor='center'
            ))

        # Tutorial assets
        self.tutorial_button_option_surface_list = []
        self.tutorial_button_list = []
        self.tutorial_button_option_surface_list.append({
            'id': 'back',
            'surface':  utils.get_text(text='Back', font=fonts.lf2, size='medium', color=colors.white),
            'scale': 1.0
        })
        self.tutorial_button_list.append(Button(
            game=self.game,
            id='back',
            width=300,
            height=80,
            pos=(constants.canvas_width/2, 680),
            pos_anchor=posanchors.center
        ))

        self.tutorial_coords_list = [
            (50, 40),
            (50, 210),
            (50, 420),
            (650, 40),
            (650, 210),
            (650, 380),
            (650, 550),
        ]

        self.tutorial_surface_list = [
            [
                utils.get_text(
                    text="Welcome to Greedy Gardens!",
                    font=fonts.minecraftia, size='small', color=colors.green_light, long_shadow=False
                ),
                utils.get_text(
                    text="You're a fruit picker working on a 4-day contract.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Your job is to collect fruits by building paths",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="to connect fruits to the Farmhouse.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="Be greedy, but not too much!",
                    font=fonts.minecraftia, size='small', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="You must score more fruits than the previous day, or",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="you will earn zero points for that day.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Scoring too high can make the next day harder.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Aim for the highest total score by the end of day 4.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about fruits",
                    font=fonts.minecraftia, size='small', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="Each day you can only score a specific fruit.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="You only know today's, tomorrow's, and seasonal fruit.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Fruits connected to Farmhouse are scored when day ends.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Seasonal fruits are bonus points scored when game ends.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about paths",
                    font=fonts.minecraftia, size='small', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="You can place paths based on the path cards you draw.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Some cards path cards gives you a strike.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="After 3 strikes, the day ends.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about events",
                    font=fonts.minecraftia, size='small', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="Strikes from path cards will trigger events.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Events can either help or ruin your plans.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Each game has 16 event cards: 8 types with 2 of each.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about magic fruits",
                    font=fonts.minecraftia, size='small', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="There are 3 magic fruits on the board.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Collecting a magic fruit will trigger an event assigned to it,",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="as well as scoring 1 bonus point for that day.",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="Controls",
                    font=fonts.minecraftia, size='small', color=colors.green_light, long_shadow=False
                ),
                utils.get_text(
                    text="         Action                /                 Draw card                /           Pause menu",
                    font=fonts.minecraftia, size='tiny', color=colors.white, long_shadow=False
                ),
            ]
        ]

        #Control button icons
        self.left_click_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='left_click')
        self.left_click_sprite = pygame.transform.scale_by(surface=self.left_click_sprite, factor=2)
        self.left_click_sprite_coords = (650, 586)
        self.right_click_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='right_click')
        self.right_click_sprite = pygame.transform.scale_by(surface=self.right_click_sprite, factor=2)
        self.right_click_sprite_coords = (778, 586)
        self.spacebar_sprite = utils.get_sprite(sprite_sheet=spritesheets.keyboard_keys_long, target_sprite='spacebar')
        self.spacebar_sprite = pygame.transform.scale_by(surface=self.spacebar_sprite, factor=2)
        self.spacebar_sprite_coords = (826, 592)
        self.middle_click_sprite = utils.get_sprite(sprite_sheet=spritesheets.mouse, target_sprite='middle_click')
        self.middle_click_sprite = pygame.transform.scale_by(surface=self.middle_click_sprite, factor=2)
        self.middle_click_sprite_coords = (1022, 586)
        self.esc_sprite = utils.get_sprite(sprite_sheet=spritesheets.keyboard_keys_long, target_sprite='esc')
        self.esc_sprite = pygame.transform.scale_by(surface=self.esc_sprite, factor=2)
        self.esc_sprite_coords = (1070, 592)

        self.tutorial_fruit_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_orange'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_blueberry'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_grape'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_strawberry'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_peach'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_coconut'),
        ]
        for i, surface in enumerate(self.tutorial_fruit_sprites):
            self.tutorial_fruit_sprites[i] = utils.effect_outline(surface=surface, distance=2, color=colors.mono_35)

        self.tutorial_path_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES'),
        ]
        for i, surface in enumerate(self.tutorial_path_sprites):
            self.tutorial_path_sprites[i] = pygame.transform.smoothscale_by(surface=surface, factor=0.75)
            self.tutorial_path_sprites[i] = utils.effect_outline(surface=self.tutorial_path_sprites[i], distance=2, color=colors.mono_35)

        self.tutorial_event_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_free'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_move'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_merge'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_point'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_redraw'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_remove'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_reveal'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_swap'),
        ]
        for i, surface in enumerate(self.tutorial_event_sprites):
            self.tutorial_event_sprites[i] = pygame.transform.smoothscale_by(surface=surface, factor=0.75)
            self.tutorial_event_sprites[i] = utils.effect_outline(surface=self.tutorial_event_sprites[i], distance=2, color=colors.mono_35)

        self.tutorial_magic_fruit_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_1'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_2'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_3'),
        ]
        for i, surface in enumerate(self.tutorial_magic_fruit_sprites):
            self.tutorial_magic_fruit_sprites[i] = utils.effect_outline(surface=surface, distance=2, color=colors.mono_35)


        # Day title
        self.day_title_text = None
        self.day_title_text_props = None
        
        # Initialize cursor
        self.cursor = cursors.normal
    
    def process_next_magic_fruit_in_queue(self):
        """Process the next magic fruit in the queue if any exist. Returns True if a magic fruit was started."""
        if len(self.magic_fruit_queue) > 1:
            # Remove the completed magic fruit from queue
            self.magic_fruit_queue.pop(0)
            
            # Start the next magic fruit event
            next_magic_number, next_cell_pos = self.magic_fruit_queue[0]
            
            # Play the magic fruit sound for each subsequent magic fruit
            utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
            
            # Set up the next magic fruit event
            if next_magic_number == 1:
                self.current_event = self.magic_fruit1_event
            elif next_magic_number == 2:
                self.current_event = self.magic_fruit2_event
            elif next_magic_number == 3:
                self.current_event = self.magic_fruit3_event
            
            # Remove the magic fruit from the board (safely)
            self.game_board.board[next_cell_pos].magic_fruit = 0
            if next_cell_pos in self.game_board.magic_fruit_index:
                self.game_board.magic_fruit_index.remove(next_cell_pos)
            self.magicing_number = next_magic_number
            
            # Update score
            current_score = getattr(self, f'day{self.current_day}_score')
            new_score = current_score + 1
            setattr(self, f'day{self.current_day}_score', new_score)
            setattr(self, f'magic_fruit{next_magic_number}_event', None)
            
            return True
        else:
            # Clear the queue as we're done
            self.magic_fruit_queue = []
            return False

    def update(self, dt, events):
        if not self.paused or self.transitioning:
            tween.update(passed_time=dt)

        if self.ready:

            if not self.transitioning and not self.music_started:
                self.music_started = True
                self.game.music_channel.play()

            if self.paused:
                if not self.in_tutorial:
                    for button in self.pause_options_button_list:
                        button.update(dt=dt, events=events)
                        if button.hovered:
                            if button.hover_cursor is not None:
                                self.cursor = button.hover_cursor
                            
                            for i, option in enumerate(self.pause_settings_surface_list):
                                if button.id == option['id']:
                                    self.setting_index = option['settings_list_index']
                                    option['left_arrow_scale'] = min(option['left_arrow_scale'] + 10*dt, 1.0)
                                    option['right_arrow_scale'] = min(option['right_arrow_scale'] + 10*dt, 1.0)
                            
                            for option in self.pause_options_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)

                        else:
                            for option in self.pause_settings_surface_list:
                                if button.id == option['id']:
                                    option['left_arrow_scale'] = max(option['left_arrow_scale'] - 10*dt, 0)
                                    option['right_arrow_scale'] = max(option['right_arrow_scale'] - 10*dt, 0)
                            
                            for option in self.pause_options_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

                        
                        if button.clicked:
                            # Handle settings arrow clicks
                            if button.id.endswith('_left') or button.id.endswith('_right'):
                                if button.id.endswith('_left'):
                                    self.current_settings_index[self.setting_index] = (self.current_settings_index[self.setting_index] - 1) % len(self.settings_manager.settings_list[self.setting_index]['value'])
                                    self.settings_manager.save_setting(self.current_settings_index)
                                    left_arrow_scale = 0.25
                                    right_arrow_scale = 1
                                elif button.id.endswith('_right'):
                                    self.current_settings_index[self.setting_index] = (self.current_settings_index[self.setting_index] + 1) % len(self.settings_manager.settings_list[self.setting_index]['value'])
                                    self.settings_manager.save_setting(self.current_settings_index)
                                    left_arrow_scale = 1
                                    right_arrow_scale = 0.25
                                
                                # Update the setting surface text
                                text_string = self.settings_manager.settings_list[self.setting_index]['label']+':  '+self.settings_manager.settings_list[self.setting_index]['value_label'][self.current_settings_index[self.setting_index]]
                                text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
                                
                                # Find and update the correct settings surface
                                setting_id = self.settings_manager.settings_list[self.setting_index]['id']
                                for i, setting_surface in enumerate(self.pause_settings_surface_list):
                                    if setting_surface['id'] == setting_id:
                                        self.pause_settings_surface_list[i] = {
                                            'id': setting_id,
                                            'surface': text,
                                            'left_arrow_scale': left_arrow_scale,
                                            'right_arrow_scale': right_arrow_scale,
                                            'settings_list_index': self.setting_index
                                        }
                                        break
                                
                                utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume)
                                self.game.apply_settings(self.setting_index)
                            
                            # Handle regular pause menu buttons
                            elif button.id == 'resume':
                                utils.sound_play(sound=sfx.resume, volume=self.game.sfx_volume)
                                self.paused = False
                            elif button.id == 'how_to_play':
                                utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                                self.in_tutorial = True
                            elif button.id == 'quit' and not self.transitioning:
                                self.transitioning = True
                                self.game.music_channel.fadeout(1500)
                                utils.sound_play(sound=sfx.woop_in, volume=self.game.sfx_volume)
                                self.freeze_frame = self.game.canvas.copy()
                                def on_complete():
                                    # utils.music_load(music_channel=self.game.music_channel, name=music.menu_intro)
                                    utils.music_load(music_channel=self.game.music_channel, name=music.menu_loop)
                                    utils.music_queue(music_channel=self.game.music_channel, name=music.menu_loop, loops=-1)
                                    self.game.start_menu_music()
                                    self.timer_manager.StopTimer(self.water_timer)
                                    
                                    # Clean up rightclick animation system
                                    if hasattr(self, 'draw_card_animation_growing'):
                                        delattr(self, 'draw_card_animation_growing')
                                    
                                    self.tween_list.clear()
                                    self.game.state_stack.clear()
                                self.tween_list.append(tween.to(
                                    container=self,
                                    key='mask_circle_radius',
                                    end_value=0,
                                    time=1,
                                    ease_type=tweencurves.easeOutQuint
                                ).on_complete(on_complete))
                            break

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if not self.in_tutorial:
                                utils.sound_play(sound=sfx.resume, volume=self.game.sfx_volume)
                                self.paused = not self.paused
                            else:
                                utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                                self.in_tutorial = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 2:
                            if not self.in_tutorial:
                                utils.sound_play(sound=sfx.resume, volume=self.game.sfx_volume)
                                self.paused = not self.paused
                            else:
                                utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                                self.in_tutorial = False

                    if not self.transitioning:
                        if event.type == self.music_end_event:
                            self.current_song += 1
                            if self.current_song >= len(self.songs):
                                self.current_song = 0
                            utils.music_load(music_channel=self.game.music_channel, name=self.songs[self.current_song])
                            self.game.music_channel.play()

                if self.in_tutorial:
                    for button in self.tutorial_button_list:
                        button.update(dt=dt, events=events)
                        
                        if button.hovered:
                            self.cursor = button.hover_cursor
                            for option in self.tutorial_button_option_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                                    if button.clicked:
                                        utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                                        self.in_tutorial = False
                        else:
                            for option in self.tutorial_button_option_surface_list:
                                if button.id == option['id']:
                                    option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

                if not self.transitioning:
                    utils.set_cursor(cursor=self.cursor)
                else:
                    utils.set_cursor(cursor=cursors.normal)
                self.cursor = cursors.normal


            else: 
                # Update substates
                if self.substate_stack:
                    self.substate_stack[-1].update(dt=dt, events=events)

                # Handle tutorial exit flag
                if self._tutorial_just_exited:
                    self._tutorial_just_exited = False
                    self.in_tutorial = False
                    # Don't resume game - return to pause menu instead

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

                if not self.in_tutorial and not self.paused:
                    # Update rightclick hint animation (tick-based, stops when paused)
                    self.draw_card_hint_animation_time += dt
                    # Use sine wave for smooth breathing animation between min and max values
                    cycle_progress = (self.draw_card_hint_animation_time % self.draw_card_hint_animation_cycle_duration) / self.draw_card_hint_animation_cycle_duration
                    # Calculate the center point and amplitude
                    center_scale = (self.draw_card_hint_scale_min + self.draw_card_hint_scale_max) / 2
                    amplitude = (self.draw_card_hint_scale_max - self.draw_card_hint_scale_min) / 2
                    self.draw_card_hint_scale = center_scale + amplitude * math.sin(cycle_progress * 2 * math.pi)

                if not self.transitioning:
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
                    self.current_turn += 1
                    Play_DrawPathState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.drawing = False
                elif self.placing:
                    Play_PlacePathState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.placing = False
                elif self.magic_eventing:
                    # Set magicing_number from queue before creating magic event state
                    if self.magic_fruit_queue:
                        next_magic_number, _ = self.magic_fruit_queue[0]
                        self.magicing_number = next_magic_number
                    self.play_event_state = True
                    Play_PlayMagicEventState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.magic_eventing = False
                elif self.is_strike and not self.magic_eventing:
                    self.current_turn += 1
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
                    # print("endgame status: ", self.end_game)
                elif self.end_game:
                    Play_ResultStage(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.end_game = False

                if not self.transitioning:
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE and not self.in_tutorial:
                                if self.paused:
                                    utils.sound_play(sound=sfx.resume, volume=self.game.sfx_volume)
                                else:
                                    utils.sound_play(sound=sfx.pause, volume=self.game.sfx_volume)
                                self.paused = not self.paused
                            
                            # Developer mode controls
                            elif self.developer_mode:
                                self._handle_developer_keys(event)
                        elif event.type == pygame.MOUSEBUTTONDOWN and not self.in_tutorial:
                            if event.button == 2:
                                if self.paused:
                                    utils.sound_play(sound=sfx.resume, volume=self.game.sfx_volume)
                                else:
                                    utils.sound_play(sound=sfx.pause, volume=self.game.sfx_volume)
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
                
                # Update developer mode alert
                if self.dev_alert_timer > 0:
                    self.dev_alert_timer -= dt
                
                # Check for deck count changes and trigger animations
                current_deck_counts = [self.fruit_deck_remaining, self.path_deck_remaining, self.event_deck_remaining]
                self.check_deck_count_changes(current_deck_counts)
                
                # Check for task text changes and trigger animations
                current_task_state = ""
                if self.current_path:
                    current_task_state = f"path_{self.current_path}"
                elif self.drawing_path_card:
                    current_task_state = "draw_path"
                elif self.current_event and self.playing_magic_event:
                    current_task_state = f"magic_event_{self.current_event}"
                elif self.current_event and not self.playing_magic_event:
                    current_task_state = f"event_{self.current_event}"
                elif self.drawing_event_card:
                    current_task_state = "draw_event"
                else:
                    current_task_state = "none"
                self.check_task_text_changes(current_task_state)
                
                # Check for strike changes and trigger animations
                self.check_strike_changes()
                
                # Check for current task card changes and trigger animations
                self.check_current_task_card_changes()
                
                # Check for day fruit changes and trigger animations
                self.check_day_fruit_changes()

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
                
                #Score calculation
                if self.current_day < 2 and not self.day1_penalty_applied:
                    self.final_day1_score = self.day1_score + (self.game_board.board_eval(today_fruit=self.day1_fruit) if self.day1_fruit is not None else 0)
                if self.current_day < 3 and not self.day2_penalty_applied:
                    self.final_day2_score = self.day2_score + (self.game_board.board_eval(today_fruit=self.day2_fruit) if self.day2_fruit is not None else 0)
                if self.current_day < 4 and not self.day3_penalty_applied:
                    self.final_day3_score = self.day3_score + (self.game_board.board_eval(today_fruit=self.day3_fruit) if self.day3_fruit is not None else 0)
                if self.current_day < 5 and not self.day4_penalty_applied:
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

                # Check for score changes and trigger animations
                current_scores = [score['amount'] for score in self.score_list]
                self.check_score_changes(current_scores)

                self.score_title_list = []
                for score in self.score_list:
                    text = utils.get_text(text=score['text'], font=fonts.lf2, size='tiny', color=score['color'])
                    self.score_title_list.append(text)

                self.score_amount_list = []
                for score in self.score_list:
                    amount = utils.get_text(text=str(score['amount']), font=fonts.lf2, size='small', color=score['color'])
                    self.score_amount_list.append(amount)

                # Update turn display
                self.right_box_title = utils.get_text(text=f'Turn {max(1, self.current_turn)}', font=fonts.lf2, size='small', color=colors.white)

                # hover function 
                if self.setup_start_state==True and not self.transitioning:
                    top_card = None
                    self.pop_up_revealed_event_card = 0
                    for button in reversed(self.button_list): 
                        if button.hovered:
                            if button.id == 'magic_fruit_3' and self.magic_fruit3_event != None:
                                self.pop_up_revealed_event_card = 3
                                break
                            elif button.id == 'magic_fruit_2' and self.magic_fruit2_event != None:
                                self.pop_up_revealed_event_card = 2
                                break
                            elif button.id == 'magic_fruit_1' and self.magic_fruit1_event != None:
                                self.pop_up_revealed_event_card = 1
                                break
                            elif button.id.startswith('revealed_event_individual_'):
                                # Extract the index from the button id
                                index = int(button.id.split('_')[-1])
                                # Set popup to show this individual revealed event card (using negative values to distinguish from magic fruits)
                                self.pop_up_revealed_event_card = -(index + 1) # -1, -2, -3, -4 for individual revealed events
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
                    elif self.game_board.board[i].home: #@note
                            #home render
                            #render dirt and grass

                            # #2*2
                            # utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_ES_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # #3*2
                            # utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_NWE_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # #4*2
                            # utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_WS_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 16), pos_anchor='topleft')
                            # #2*3
                            # utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_NWS_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            # #3*3
                            # utils.blit(dest=canvas, source=self.dirt_sprite_5[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            # #4*3
                            # utils.blit(dest=canvas, source=self.dirt_sprite_6[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_NES_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48 + 8, self.grid_start_y + ((i // 8) * self.cell_size) + 32), pos_anchor='topleft')
                            # #2*4
                            # utils.blit(dest=canvas, source=self.dirt_sprite_7[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_NE_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 16, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            # #3*4
                            # utils.blit(dest=canvas, source=self.dirt_sprite_8[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_WES_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size) + 48 + 8), pos_anchor='topleft')
                            # #4*4
                            # utils.blit(dest=canvas, source=self.dirt_sprite_9[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')
                            # utils.blit(dest=canvas, source=self.grass_light_path_NW_home, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 48, self.grid_start_y + ((i // 8) * self.cell_size) + 48), pos_anchor='topleft')

                            # #3*1
                            # utils.blit(dest=canvas, source=self.dirt_sprite_1[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            # if i >= 8 and self.game_board.board[i-8].south == True and self.game_board.board[i-8].temp == False:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            # else:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_S, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 32, self.grid_start_y + ((i // 8) * self.cell_size)), pos_anchor='topleft')
                            # #1*3
                            # utils.blit(dest=canvas, source=self.dirt_sprite_2[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # if i >= 8 and self.game_board.board[i-1].east == True and self.game_board.board[i-1].temp == False:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # else:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_E, pos=(self.grid_start_x + ((i % 8) * self.cell_size), self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # #5*3
                            # utils.blit(dest=canvas, source=self.dirt_sprite_3[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # if i >= 8 and self.game_board.board[i+1].west == True and self.game_board.board[i+1].temp == False:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_WE, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # else:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_W, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+64, self.grid_start_y + ((i // 8) * self.cell_size)+32), pos_anchor='topleft')
                            # #3*5
                            # utils.blit(dest=canvas, source=self.dirt_sprite_4[i], pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            # if i >= 8 and self.game_board.board[i+8].north == True and self.game_board.board[i+8].temp == False:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_NS, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')
                            # else:
                            #     utils.blit(dest=canvas, source=self.grass_light_path_N, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+32, self.grid_start_y + ((i // 8) * self.cell_size)+64), pos_anchor='topleft')


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
                        
                            utils.blit(dest=canvas, source=self.home, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+17, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
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
                    elif self.game_board.board[i].home: #@note
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
                        
                            utils.blit(dest=canvas, source=self.home, pos=(self.grid_start_x + ((i % 8) * self.cell_size)+17, self.grid_start_y + ((i // 8) * self.cell_size)+16), pos_anchor='topleft')
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
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 42), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit1_image_small, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')
                if self.game_board.board[i].magic_fruit == 2:
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 42), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit2_image_small, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')
                if self.game_board.board[i].magic_fruit == 3:
                    utils.blit(dest=canvas, source=self.magic_fruit_shadow, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 42), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.magic_fruit3_image_small, pos=(self.grid_start_x + ((i % 8) * self.cell_size) + 40, self.grid_start_y + ((i // 8) * self.cell_size) + 40), pos_anchor='center')

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

            # Render dim
            # print(self.is_choosing)
            if self.is_choosing:
                utils.draw_rect(
                    dest=canvas,
                    size=(constants.canvas_width, constants.canvas_height),
                    pos=(0, 0),
                    pos_anchor='topleft',
                    color=(*colors.mono_50, 90)
                )
            
            # Render gui

            if self.current_day < 5:
                    
                ## Render Day title
                if self.day_title_text and self.day_title_text_props:
                    self.day_title_text.set_alpha(self.day_title_text_props['alpha'])
                    utils.blit(
                        dest=canvas,
                        source=self.day_title_text,
                        pos=(constants.canvas_width/2, self.day_title_text_props['y']),
                        pos_anchor='center'
                    )

                ## Render event cancelled popup
                if self.event_cancelled_popup_props:
                    self.event_cancelled_popup.set_alpha(self.event_cancelled_popup_props['alpha'])
                    utils.blit(
                        dest=canvas,
                        source=self.event_cancelled_popup,
                        pos=(constants.canvas_width//2, self.event_cancelled_popup_props['y']),
                        pos_anchor=posanchors.midtop
                    )
                
                ## Render left white box (with alpha transition)
                if self.hud_left_alpha > 0:
                    # Create a temporary surface for the left HUD
                    left_hud_surface = pygame.Surface((self.box_width + 4, constants.canvas_height), pygame.SRCALPHA)
                    
                    # Draw the left box content to the temporary surface
                    alpha_value = int(135 * self.hud_left_alpha)  # Scale alpha from 0-150
                    utils.draw_rect(
                        dest=left_hud_surface,
                        size=(self.box_width, constants.canvas_height),
                        pos=(-4, 0),
                        pos_anchor='topleft',
                        color=(*colors.white, alpha_value),
                        outer_border_width=4,
                        outer_border_color=(*colors.white, 200),
                    )
                    
                    # Render text in left white box to temporary surface
                    utils.blit(dest=left_hud_surface, source=self.left_box_title, pos=(self.box_width/2, 35), pos_anchor='center')
                    for i, score in enumerate(self.score_title_list):
                        utils.blit(dest=left_hud_surface, source=score, pos=(70, 83 + i*45), pos_anchor='midleft')
                    utils.blit(dest=left_hud_surface, source=self.left_box_strike, pos=(self.box_width/2, 365
                    ), pos_anchor='center')
                    utils.blit(dest=left_hud_surface, source=self.left_box_task, pos=(self.box_width/2, 500), pos_anchor='center')

                    ## Render rightclick hint (hide only when a card is being rendered at position 630)
                    card_being_rendered = (self.current_path or 
                                         (self.current_event and self.playing_magic_event and self.is_current_task_event) or
                                         (self.current_event and not self.playing_magic_event))
                    if not card_being_rendered:
                        # Use fixed scale during end day state, animated scale otherwise
                        scale_factor = 1.0 if self.is_choosing else self.draw_card_hint_scale
                        scaled_draw_card_hint = pygame.transform.scale_by(surface=self.draw_card_hint, factor=scale_factor)
                        utils.blit(dest=left_hud_surface, source=scaled_draw_card_hint, pos=(self.box_width/2, 620), pos_anchor='center')   

                    ## Render value in left white box to temporary surface
                    for i, score in enumerate(self.score_amount_list):
                        # Apply scale animation to score numbers
                        if self.score_scales[i] != 1.0:
                            scaled_score = pygame.transform.scale_by(surface=score, factor=self.score_scales[i])
                            # Use center anchor to make scaling appear centered
                            # Calculate the center position based on the original midright position
                            original_width = score.get_width()
                            center_x = 240 - (original_width / 2)
                            utils.blit(dest=left_hud_surface, source=scaled_score, pos=(center_x, 80 + i*45), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=score, pos=(240, 80 + i*45), pos_anchor='midright')

                    ## Render strike in left white box to temporary surface
                    for i in range(self.strikes):
                        # Apply scale animation to strike
                        if self.strike_scales[i] != 1.0:
                            scaled_strike = pygame.transform.scale_by(surface=self.scaled_live_strike, factor=self.strike_scales[i])
                            # Use center anchor to make scaling appear centered
                            original_size = self.scaled_live_strike.get_size()
                            center_x = 40 + i*64 + original_size[0] // 2
                            center_y = 395 + original_size[1] // 2
                            utils.blit(dest=left_hud_surface, source=scaled_strike, pos=(center_x, center_y), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.scaled_live_strike, pos=(40 + i*64, 395), pos_anchor='topleft')
                    for i in range(3 - self.strikes):
                        utils.blit(dest=left_hud_surface, source=self.scaled_blank_strike, pos=(40 + i*64 + self.strikes*64, 395), pos_anchor='topleft')

                    ## Render current task image to temporary surface
                    if self.current_path:
                        self.current_path_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite=f"card_{self.current_path}")
                        # Apply scale animation to current task card
                        if self.current_task_card_scale != 1.0:
                            scaled_card = pygame.transform.scale_by(surface=self.current_path_image, factor=self.current_task_card_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_card, pos=(self.box_width/2, 630), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.current_path_image, pos=(self.box_width/2, 630), pos_anchor='center')
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_path_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_path_text, pos=(self.box_width/2, 535), pos_anchor='center')
                    elif self.drawing_path_card:
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_draw_path_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_draw_path_text, pos=(self.box_width/2, 535), pos_anchor='center')
                    elif self.current_event and self.playing_magic_event:
                        if self.is_current_task_event:
                            self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                            # Apply scale animation to current task card
                            if self.current_task_card_scale != 1.0:
                                scaled_card = pygame.transform.scale_by(surface=self.current_event_image, factor=self.current_task_card_scale)
                                utils.blit(dest=left_hud_surface, source=scaled_card, pos=(self.box_width/2, 630), pos_anchor='center')
                            else:
                                utils.blit(dest=left_hud_surface, source=self.current_event_image, pos=(self.box_width/2, 630), pos_anchor='center')
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_magic_event_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_magic_event_text, pos=(self.box_width/2, 535), pos_anchor='center')
                    elif self.current_event and not self.playing_magic_event:
                        self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                        # Apply scale animation to current task card
                        if self.current_task_card_scale != 1.0:
                            scaled_card = pygame.transform.scale_by(surface=self.current_event_image, factor=self.current_task_card_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_card, pos=(self.box_width/2, 630), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.current_event_image, pos=(self.box_width/2, 630), pos_anchor='center')
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_event_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_event_text, pos=(self.box_width/2, 535), pos_anchor='center')
                    elif self.drawing_event_card:
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_draw_event_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_draw_event_text, pos=(self.box_width/2, 535), pos_anchor='center')
                    else:
                        # Apply scale animation to task text
                        if self.task_text_scale != 1.0:
                            scaled_task_text = pygame.transform.scale_by(surface=self.left_box_none_text, factor=self.task_text_scale)
                            utils.blit(dest=left_hud_surface, source=scaled_task_text, pos=(self.box_width/2, 535), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.left_box_none_text, pos=(self.box_width/2, 535), pos_anchor='center')

                    ## Render Day's Fruit to temporary surface
                    if self.day1_fruit:
                        if self.current_day == 1:
                            self.day1_fruit_image = self.big_fruit_sprites['big_'+self.day1_fruit]
                        else:
                            self.day1_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day1_fruit])
                        self.day1_fruit_image = utils.effect_outline(surface=self.day1_fruit_image, distance=2, color=colors.mono_35)
                        # Apply scale animation to day 1 fruit
                        if self.day_fruit_scales[0] != 1.0:
                            scaled_fruit = pygame.transform.scale_by(surface=self.day1_fruit_image, factor=self.day_fruit_scales[0])
                            utils.blit(dest=left_hud_surface, source=scaled_fruit, pos=(45, 83), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.day1_fruit_image, pos=(45, 83), pos_anchor='center')
                    if self.day2_fruit:
                        if self.current_day == 2:
                            self.day2_fruit_image = self.big_fruit_sprites['big_'+self.day2_fruit]
                        else:
                            self.day2_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day2_fruit])
                        self.day2_fruit_image = utils.effect_outline(surface=self.day2_fruit_image, distance=2, color=colors.mono_35)
                        # Apply scale animation to day 2 fruit
                        if self.day_fruit_scales[1] != 1.0:
                            scaled_fruit = pygame.transform.scale_by(surface=self.day2_fruit_image, factor=self.day_fruit_scales[1])
                            utils.blit(dest=left_hud_surface, source=scaled_fruit, pos=(45, 128), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.day2_fruit_image, pos=(45, 128), pos_anchor='center')
                    if self.day3_fruit:
                        if self.current_day == 3:
                            self.day3_fruit_image = self.big_fruit_sprites['big_'+self.day3_fruit]
                        else:
                            self.day3_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day3_fruit])
                        self.day3_fruit_image = utils.effect_outline(surface=self.day3_fruit_image, distance=2, color=colors.mono_35)
                        # Apply scale animation to day 3 fruit
                        if self.day_fruit_scales[2] != 1.0:
                            scaled_fruit = pygame.transform.scale_by(surface=self.day3_fruit_image, factor=self.day_fruit_scales[2])
                            utils.blit(dest=left_hud_surface, source=scaled_fruit, pos=(45, 173), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.day3_fruit_image, pos=(45, 173), pos_anchor='center')
                    if self.day4_fruit:
                        if self.current_day == 4:
                            self.day4_fruit_image = self.big_fruit_sprites['big_'+self.day4_fruit]
                        else:
                            self.day4_fruit_image = utils.effect_grayscale(self.big_fruit_sprites['big_'+self.day4_fruit])
                        self.day4_fruit_image = utils.effect_outline(surface=self.day4_fruit_image, distance=2, color=colors.mono_35)
                        # Apply scale animation to day 4 fruit
                        if self.day_fruit_scales[3] != 1.0:
                            scaled_fruit = pygame.transform.scale_by(surface=self.day4_fruit_image, factor=self.day_fruit_scales[3])
                            utils.blit(dest=left_hud_surface, source=scaled_fruit, pos=(45, 218), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.day4_fruit_image, pos=(45, 218), pos_anchor='center')

                    ## Render seasonal fruit in left white box to temporary surface
                    if self.seasonal_fruit is not None:
                        self.seasonal_fruit_image = self.big_fruit_sprites['big_'+self.seasonal_fruit]
                        self.seasonal_fruit_image = utils.effect_outline(surface=self.seasonal_fruit_image, distance=2, color=colors.mono_35)
                        # Apply scale animation to seasonal fruit
                        if self.day_fruit_scales[4] != 1.0:
                            scaled_fruit = pygame.transform.scale_by(surface=self.seasonal_fruit_image, factor=self.day_fruit_scales[4])
                            utils.blit(dest=left_hud_surface, source=scaled_fruit, pos=(45, 263), pos_anchor='center')
                        else:
                            utils.blit(dest=left_hud_surface, source=self.seasonal_fruit_image, pos=(45, 263), pos_anchor='center')
                    
                    # Apply alpha transition to the entire HUD surface and render it
                    left_hud_surface.set_alpha(int(255 * self.hud_left_alpha))
                    utils.blit(dest=canvas, source=left_hud_surface, pos=(0, 0), pos_anchor='topleft')

                ## Render right white box (with alpha transition)
                if self.hud_right_alpha > 0:
                    # Create a temporary surface for the right HUD
                    right_hud_surface = pygame.Surface((self.box_width + 4, constants.canvas_height), pygame.SRCALPHA)
                    
                    # Draw the right box content to the temporary surface
                    alpha_value = int(135 * self.hud_right_alpha)  # Scale alpha from 0-150
                    utils.draw_rect(
                        dest=right_hud_surface,
                        size=(self.box_width, constants.canvas_height),
                        pos=(4, 0),
                        pos_anchor='topleft',
                        color=(*colors.white, alpha_value),
                        outer_border_width=4,
                        outer_border_color=(*colors.white, 200),
                    )
                    
                    ## Render text in right white box to temporary surface
                    utils.blit(dest=right_hud_surface, source=self.right_box_title, pos=(self.box_width/2, 35), pos_anchor='center')
                    for i, deck in enumerate(self.deck_title_list):
                        # Adjust positions for the surface coordinates (subtract canvas_width - box_width offset)
                        surface_x = 1140 - (constants.canvas_width - self.box_width)
                        utils.blit(dest=right_hud_surface, source=deck, pos=(surface_x, 85 + i*135), pos_anchor='topleft')
                        utils.blit(dest=right_hud_surface, source=self.right_remaining, pos=(surface_x, 110 + i*135), pos_anchor='topleft')

                    ## Render value in right white box to temporary surface
                    # Fruit deck count
                    self.fruit_deck_remaining_amount = utils.get_text(text=str(self.fruit_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
                    if self.deck_scales[0] != 1.0:
                        scaled_fruit_count = pygame.transform.scale_by(surface=self.fruit_deck_remaining_amount, factor=self.deck_scales[0])
                        # Adjust position to keep the topleft anchor consistent during scaling
                        original_width = self.fruit_deck_remaining_amount.get_width()
                        original_height = self.fruit_deck_remaining_amount.get_height()
                        scaled_width = scaled_fruit_count.get_width()
                        scaled_height = scaled_fruit_count.get_height()
                        # Calculate offset to keep the same visual position
                        offset_x = (scaled_width - original_width) / 2
                        offset_y = (scaled_height - original_height) / 2
                        utils.blit(dest=right_hud_surface, source=scaled_fruit_count, pos=(surface_x - offset_x, 135 - offset_y), pos_anchor='topleft')
                    else:
                        utils.blit(dest=right_hud_surface, source=self.fruit_deck_remaining_amount, pos=(surface_x, 135), pos_anchor='topleft')
                    
                    # Path deck count
                    self.path_deck_remaining_amount = utils.get_text(text=str(self.path_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
                    if self.deck_scales[1] != 1.0:
                        scaled_path_count = pygame.transform.scale_by(surface=self.path_deck_remaining_amount, factor=self.deck_scales[1])
                        # Adjust position to keep the topleft anchor consistent during scaling
                        original_width = self.path_deck_remaining_amount.get_width()
                        original_height = self.path_deck_remaining_amount.get_height()
                        scaled_width = scaled_path_count.get_width()
                        scaled_height = scaled_path_count.get_height()
                        # Calculate offset to keep the same visual position
                        offset_x = (scaled_width - original_width) / 2
                        offset_y = (scaled_height - original_height) / 2
                        utils.blit(dest=right_hud_surface, source=scaled_path_count, pos=(surface_x - offset_x, 270 - offset_y), pos_anchor='topleft')
                    else:
                        utils.blit(dest=right_hud_surface, source=self.path_deck_remaining_amount, pos=(surface_x, 270), pos_anchor='topleft')
                    
                    # Event deck count
                    self.event_deck_remaining_amount = utils.get_text(text=str(self.event_deck_remaining), font=fonts.lf2, size='small', color=colors.white)
                    if self.deck_scales[2] != 1.0:
                        scaled_event_count = pygame.transform.scale_by(surface=self.event_deck_remaining_amount, factor=self.deck_scales[2])
                        # Adjust position to keep the topleft anchor consistent during scaling
                        original_width = self.event_deck_remaining_amount.get_width()
                        original_height = self.event_deck_remaining_amount.get_height()
                        scaled_width = scaled_event_count.get_width()
                        scaled_height = scaled_event_count.get_height()
                        # Calculate offset to keep the same visual position
                        offset_x = (scaled_width - original_width) / 2
                        offset_y = (scaled_height - original_height) / 2
                        utils.blit(dest=right_hud_surface, source=scaled_event_count, pos=(surface_x - offset_x, 405 - offset_y), pos_anchor='topleft')
                    else:
                        utils.blit(dest=right_hud_surface, source=self.event_deck_remaining_amount, pos=(surface_x, 405), pos_anchor='topleft')

                    ## Render card backs in right white box to temporary surface
                    card_x = 1080 - (constants.canvas_width - self.box_width)
                    utils.blit(dest=right_hud_surface, source=self.card_fruit_back_image, pos=(card_x, 130), pos_anchor='center')
                    utils.blit(dest=right_hud_surface, source=self.card_path_back_image, pos=(card_x, 265), pos_anchor='center')
                    utils.blit(dest=right_hud_surface, source=self.card_event_back_image, pos=(card_x, 400), pos_anchor='center')

                    ## Render Magic Fruit Event cards to temporary surface
                    if self.magic_fruit1_event or self.magic_fruit2_event or self.magic_fruit3_event:
                        utils.blit(dest=right_hud_surface, source=self.right_magic_fruits, pos=(self.box_width/2, 500), pos_anchor='center')
                    if self.magic_fruit1_event:
                        self.magic_fruit1_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit1_event}")
                        magic1_x = 1073 - (constants.canvas_width - self.box_width)
                        utils.blit(dest=right_hud_surface, source=self.magic_fruit1_event_image, pos=(magic1_x, 619), pos_anchor='center')
                        utils.blit(
                            dest=right_hud_surface,
                            source=self.magic_fruit1_image,
                            pos=(magic1_x, 619 - 74),
                            pos_anchor='center'
                        )
                    if self.magic_fruit2_event:
                        self.magic_fruit2_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit2_event}")
                        magic2_x = 1143 - (constants.canvas_width - self.box_width)
                        utils.blit(dest=right_hud_surface, source=self.magic_fruit2_event_image, pos=(magic2_x, 629), pos_anchor='center')
                        utils.blit(
                            dest=right_hud_surface,
                            source=self.magic_fruit2_image,
                            pos=(magic2_x, 629 - 74),
                            pos_anchor='center'
                        )
                    if self.magic_fruit3_event:
                        self.magic_fruit3_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.magic_fruit3_event}")
                        magic3_x = 1213 - (constants.canvas_width - self.box_width)
                        utils.blit(dest=right_hud_surface, source=self.magic_fruit3_event_image, pos=(magic3_x, 639), pos_anchor='center')
                        utils.blit(
                            dest=right_hud_surface,
                            source=self.magic_fruit3_image,
                            pos=(magic3_x, 639 - 74),
                            pos_anchor='center'
                        )
                    
                    # Apply alpha transition to the entire HUD surface and render it
                    right_hud_surface.set_alpha(int(255 * self.hud_right_alpha))
                    utils.blit(dest=canvas, source=right_hud_surface, pos=(constants.canvas_width - self.box_width, 0), pos_anchor='topleft')
                            

            if not self.substate_stack:
                pass

            else:
                self.substate_stack[-1].render(canvas=canvas)  

            
            if self.current_day < 5:
                # Render Revealed card
                if len(self.revealed_path) > 0:
                    utils.draw_rect(
                        dest=canvas,
                        size=(60, len(self.revealed_path)*60),
                        pos=(constants.canvas_width - self.box_width + 4, constants.canvas_height),
                        pos_anchor='bottomright',
                        color=(*colors.white, 150),
                        inner_border_width=4,
                        inner_border_color=colors.mono_240,
                    )
                    
                    for i, card in enumerate(self.revealed_path):
                        utils.blit(dest=canvas, source=getattr(self, f'{card.card_name}_image'), pos=(constants.canvas_width - self.box_width - 2, constants.canvas_height - 6 - i*58), pos_anchor='bottomright')
                        if card.strike:
                            utils.blit(dest=canvas, source=self.path_strike_image, pos=(constants.canvas_width - self.box_width - 4, constants.canvas_height - 6 - i*58), pos_anchor='bottomright')
                    utils.blit(dest=canvas, source=self.next_text, pos=(constants.canvas_width - self.box_width - 28, constants.canvas_height - 6 - i*58 - 94), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.path_text, pos=(constants.canvas_width - self.box_width - 28, constants.canvas_height - 6 - i*58 - 74), pos_anchor='center')
                
                if len(self.revealed_event) > 0:
                    box_height = len(self.revealed_event) * 58 + 8
                    utils.draw_rect(
                        dest=canvas,
                        size=(60, box_height),
                        pos=(constants.canvas_width - self.box_width + 4, 0),
                        pos_anchor='topright',
                        color=(*colors.white, 150),
                        inner_border_width=4,
                        inner_border_color=colors.mono_240,
                    )
                    
                    for i, card in enumerate(self.revealed_event):
                        utils.blit(dest=canvas, source=getattr(self, f'{card.card_name}_image'), pos=(constants.canvas_width - self.box_width - 2, 10 + i*58), pos_anchor=posanchors.topright)
                    utils.blit(dest=canvas, source=self.next_text, pos=(constants.canvas_width - self.box_width - 28, 8 + i*58 + 72), pos_anchor='center')
                    utils.blit(dest=canvas, source=self.event_text, pos=(constants.canvas_width - self.box_width - 28, 8 + i*58 + 92), pos_anchor='center')
                
                #hover function
                if self.setup_start_state and not self.end_game:
                    # for button in self.button_list:
                    #     button.render(canvas=canvas)
                    if self.pop_up_revealed_event_card == 3 and self.magic_fruit3_event != None: 
                        mask_surface = pygame.Surface((constants.canvas_width, constants.canvas_height), pygame.SRCALPHA)
                        mask_surface.fill((*colors.black, 90))
                        # Cutout for magic fruit 3 at original button position
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 0),
                            rect=(1165 + 2, 575 + 2, 96 - 4, 128 - 4)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1165 + 40, 575 + 2, 18, 2)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1165 + 42, 575 + 4, 12, 2)
                        )
                        utils.blit(dest=canvas, source=mask_surface) 
                        self.magic_fruit3_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event_big, target_sprite=f"card_{self.magic_fruit3_event.replace('event_', 'event_big_')}")
                        utils.blit(dest=canvas, source=self.magic_fruit3_event_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
                    elif self.pop_up_revealed_event_card == 2 and self.magic_fruit2_event != None:
                        mask_surface = pygame.Surface((constants.canvas_width, constants.canvas_height), pygame.SRCALPHA)
                        mask_surface.fill((*colors.black, 90))
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 0),
                            rect=(1095 + 2, 565 + 2, 96 - 4, 128 - 4)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1095 + 40, 565 + 2, 18, 2)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1095 + 42, 565 + 4, 12, 2)
                        )
                        # Only shadow magic fruit 3 if it exists
                        if self.magic_fruit3_event != None:
                            pygame.draw.rect(
                                surface=mask_surface,
                                color=(*colors.black, 90),
                                rect=(1165, 575, 96 - 4, 128 - 4)
                            )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 0),
                            rect=(1165, 575, 2, 2)
                        )
                        utils.blit(dest=canvas, source=mask_surface)
                        self.magic_fruit2_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event_big, target_sprite=f"card_{self.magic_fruit2_event.replace('event_', 'event_big_')}")
                        utils.blit(dest=canvas, source=self.magic_fruit2_event_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
                    elif self.pop_up_revealed_event_card == 1 and self.magic_fruit1_event != None:
                        mask_surface = pygame.Surface((constants.canvas_width, constants.canvas_height), pygame.SRCALPHA)
                        mask_surface.fill((*colors.black, 90))
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 0),
                            rect=(1025 + 2, 555 + 2, 96 - 4, 128 - 4)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1025 + 40, 555 + 2, 18, 2)
                        )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 90),
                            rect=(1025 + 42, 555 + 4, 12, 2)
                        )
                        # Only shadow magic fruit 2 if it exists
                        if self.magic_fruit2_event != None:
                            pygame.draw.rect(
                                surface=mask_surface,
                                color=(*colors.black, 90),
                                rect=(1095, 565, 96 - 4, 128 - 4)
                            )
                        # Only shadow magic fruit 3 if it exists  
                        if self.magic_fruit3_event != None:
                            pygame.draw.rect(
                                surface=mask_surface,
                                color=(*colors.black, 90),
                                rect=(1165, 575, 96 - 4, 128 - 4)
                            )
                        pygame.draw.rect(
                            surface=mask_surface,
                            color=(*colors.black, 0),
                            rect=(1095, 565, 2, 2)
                        )
                        utils.blit(dest=canvas, source=mask_surface)
                        self.magic_fruit1_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event_big, target_sprite=f"card_{self.magic_fruit1_event.replace('event_', 'event_big_')}")
                        utils.blit(dest=canvas, source=self.magic_fruit1_event_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')

                    # Handle individual revealed event card hover (negative values)
                    elif self.pop_up_revealed_event_card < 0 and len(self.revealed_event) > 0:
                        index = -self.pop_up_revealed_event_card - 1 
                        if index < len(self.revealed_event):
                            mask_surface = pygame.Surface((constants.canvas_width, constants.canvas_height), pygame.SRCALPHA)
                            mask_surface.fill((*colors.black, 90))
                            
                            button_x = constants.canvas_width - self.box_width - self.revealed_event_button_width
                            button_y = self.revealed_event_button_y_base + index * self.revealed_event_button_y_spacing
                            
                            pygame.draw.rect(
                                surface=mask_surface,
                                color=(*colors.black, 0),
                                rect=(button_x, button_y, self.revealed_event_button_width, self.revealed_event_button_height)
                            )
                            utils.blit(dest=canvas, source=mask_surface)
                            card = self.revealed_event[index]
                            card_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event_big, target_sprite=f"card_{card.card_name.replace('event_', 'event_big_')}")
                            utils.blit(dest=canvas, source=card_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor=posanchors.center)
                    if self.play_event_state == True and self.is_current_task_event:
                        if self.pop_up_revealed_event_card == 4:
                            mask_surface = pygame.Surface((constants.canvas_width, constants.canvas_height), pygame.SRCALPHA)
                            mask_surface.fill((*colors.black, 90))
                            pygame.draw.rect(
                                surface=mask_surface,
                                color=(*colors.black, 0),
                                rect=(88 + 2, 566 + 2, 96 - 4, 128 - 4)
                            )
                            utils.blit(dest=canvas, source=mask_surface)
                            #self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.current_event}")
                            self.current_event_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event_big, target_sprite=f"card_{self.current_event.replace('event_', 'event_big_')}")
                            utils.blit(dest=canvas, source=self.current_event_image, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor=posanchors.center)


        # pause menu
        if self.paused and not self.in_tutorial:
            utils.blit(dest=canvas, source=self.pause_background)
            utils.blit(dest=canvas, source=self.pause_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
            
            # Render settings options with arrows (between Resume and Exit)
            for i, option in enumerate(self.pause_settings_surface_list):
                y_pos = 370 + i*50  # Start at 370 (moved down from 295)
                utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2, y_pos), pos_anchor='center')
                
                # Render arrows with scaling
                scaled_left_arrow = pygame.transform.scale_by(surface=self.arrow_left, factor=option['left_arrow_scale'])
                scaled_right_arrow = pygame.transform.scale_by(surface=self.arrow_right, factor=option['right_arrow_scale'])
                utils.blit(
                    dest=canvas,
                    source=scaled_left_arrow,
                    pos=(constants.canvas_width/2 - 180, y_pos),
                    pos_anchor='center'
                )
                utils.blit(
                    dest=canvas,
                    source=scaled_right_arrow,
                    pos=(constants.canvas_width/2 + 180, y_pos),
                    pos_anchor='center'
                )
            
            # Render regular pause menu buttons (Resume, How to Play, Exit to menu)
            for i, option in enumerate(self.pause_options_surface_list):
                scaled_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                if i == 0:  # Resume button - below title
                    y_offset = 225  # Below pause title at 120
                elif i == 1:  # How to Play button - directly below Resume
                    y_offset = 295  # Just below Resume
                else:  # Exit to menu button - after settings panel (moved down)
                    y_offset = 370 + 5*50 + 30  # Moved down from 295 to 370
                utils.blit(
                    dest=canvas,
                    source=scaled_surface,
                    pos=(constants.canvas_width/2, y_offset),
                    pos_anchor='center'
                )
        elif self.paused and self.in_tutorial:
            utils.blit(dest=canvas, source=self.pause_background)

            utils.draw_rect(
                dest=canvas,
                size=(constants.canvas_width - 40, constants.canvas_height - 100),
                pos=(20, 20),
                pos_anchor=posanchors.topleft,
                color=(*colors.mono_50, 225),
                inner_border_width=3
            )

            for i, option in enumerate(self.tutorial_button_option_surface_list):
                processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 680), pos_anchor=posanchors.center)

            for i, group in enumerate(self.tutorial_surface_list):
                header_y_offset = -8
                y_increment = 0
                x, y = self.tutorial_coords_list[i]
                for text in group:
                    utils.blit(
                        dest=canvas,
                        source=text,
                        pos=(x, y + header_y_offset + y_increment),
                        pos_anchor=posanchors.topleft
                    )
                    header_y_offset = 0
                    y_increment += 40

            start_x = 280
            start_y = self.tutorial_coords_list[2][1] - 5
            x_increment = 40
            for i, surface in enumerate(self.tutorial_fruit_sprites):
                utils.blit(
                    dest=canvas, source=surface,
                    pos=(start_x + i * x_increment, start_y),
                    pos_anchor=posanchors.topleft
                )

            start_x = 880
            start_y = self.tutorial_coords_list[3][1] - 8
            x_increment = 40
            for i, surface in enumerate(self.tutorial_path_sprites):
                utils.blit(
                    dest=canvas, source=surface,
                    pos=(start_x + i * x_increment, start_y),
                    pos_anchor=posanchors.topleft
                )

            start_x = 895
            start_y = self.tutorial_coords_list[4][1] - 8
            x_increment = 40
            for i, surface in enumerate(self.tutorial_event_sprites):
                utils.blit(
                    dest=canvas, source=surface,
                    pos=(start_x + i * x_increment, start_y),
                    pos_anchor=posanchors.topleft
                )

            start_x = 965
            start_y = self.tutorial_coords_list[5][1] - 5
            x_increment = 40
            for i, surface in enumerate(self.tutorial_magic_fruit_sprites):
                utils.blit(
                    dest=canvas, source=surface,
                    pos=(start_x + i * x_increment, start_y),
                    pos_anchor=posanchors.topleft
                )

            utils.blit(
                dest=canvas, source=self.left_click_sprite,
                pos=self.left_click_sprite_coords,
                pos_anchor=posanchors.topleft
            )
            utils.blit(
                dest=canvas, source=self.right_click_sprite,
                pos=self.right_click_sprite_coords,
                pos_anchor=posanchors.topleft
            )
            utils.blit(
                dest=canvas, source=self.spacebar_sprite,
                pos=self.spacebar_sprite_coords,
                pos_anchor=posanchors.topleft
            )
            utils.blit(
                dest=canvas, source=self.middle_click_sprite,
                pos=self.middle_click_sprite_coords,
                pos_anchor=posanchors.topleft
            )
            utils.blit(
                dest=canvas, source=self.esc_sprite,
                pos=self.esc_sprite_coords,
                pos_anchor=posanchors.topleft
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
            self.pixelated_mask_surface = utils.effect_pixelate(surface=self.mask_surface, pixel_size=4)
            utils.blit(dest=canvas, source=self.pixelated_mask_surface)
        
        # Render developer mode alert
        if self.developer_mode and self.dev_alert_timer > 0:
            # Simple debug-style text
            alert_text_surface = utils.get_text(
                text=self.dev_alert_text,
                font=fonts.lf2,
                size='small',
                color=colors.white,
                long_shadow=False,
                outline=False
            )
            
            # Simple black background rectangle
            text_width = alert_text_surface.get_width()
            text_height = alert_text_surface.get_height()
            bg_rect = pygame.Rect(0, 0, text_width + 20, text_height + 10)
            bg_rect.center = (constants.canvas_width // 2, 50)  # Top of screen
            
            # Draw simple black background
            pygame.draw.rect(canvas, colors.black, bg_rect)
            
            # Draw text
            text_rect = alert_text_surface.get_rect()
            text_rect.center = bg_rect.center
            canvas.blit(alert_text_surface, text_rect)
                

    def random_dirt(self):
        return utils.get_sprite(sprite_sheet=spritesheets.tileset, target_sprite=f"dirt_{random.randint(1, 9)}")
    
    
    def day_title_tween_chain(self):
        self.shown_day_title = False
        self.day_title_text_props = {
            'y': constants.canvas_height/2 + 150,
            'alpha': 0,
        }
        self.day_title_text = utils.get_text(text=f'Day {self.current_day}', font=fonts.lf2, size='huge', color=colors.white)
        
        # Start HUD transition animation at the same time as day transition
        self.start_hud_transition()
        
        def on_complete1():
            utils.multitween(
                tween_list=self.tween_list,
                container=self.day_title_text_props,
                keys=['y', 'alpha'],
                end_values=[constants.canvas_height/2 - 150, 0],
                time=1,
                ease_type=[tweencurves.easeInExpo, tweencurves.easeInCubic],
                on_complete=on_complete2
            )
        def on_complete2():
            self.day_title_text = None
            self.day_title_text_props = None
            self.shown_day_title = True
            self.tween_list.clear()
            
        utils.multitween(
            tween_list=self.tween_list,
            container=self.day_title_text_props,
            keys=['y', 'alpha'],
            end_values=[constants.canvas_height/2, 255],
            time=1,
            ease_type=[tweencurves.easeOutExpo, tweencurves.easeOutCubic],
            on_complete=on_complete1
        )

                    
    def start_hud_transition(self):
        # Animate left HUD panel
        self.tween_list.append(tween.to(
            container=self,
            key='hud_left_alpha',
            end_value=1.0,
            time=2.0,  # 2 seconds duration to match day transition
            ease_type=tweencurves.easeInQuad
        ))
        
        # Animate right HUD panel
        self.tween_list.append(tween.to(
            container=self,
            key='hud_right_alpha',
            end_value=1.0,
            time=2.0,  # 2 seconds duration to match day transition
            ease_type=tweencurves.easeInQuad
        ).on_complete(self.on_hud_transition_complete))
    
    def on_hud_transition_complete(self):
        self.hud_transition_complete = True
    
    def animate_score(self, score_index):
        """Animate a score number with a scale-up then scale-down effect."""
        self.score_scales[score_index] = 1.5
        self.tween_list.append(tween.to(
            container=self.score_scales,
            key=score_index,
            end_value=1.0,
            time=0.3, 
            ease_type=tweencurves.easeOutQuart
        ))
    
    def check_score_changes(self, current_scores):
        """Check if any scores have changed and trigger animations."""
        for i, (current, previous) in enumerate(zip(current_scores, self.previous_scores)):
            if current != previous:
                self.animate_score(i)
        self.previous_scores = current_scores.copy()
    
    def animate_deck_count(self, deck_index):
        """Animate a deck count number with a scale-up then scale-down effect."""
        self.deck_scales[deck_index] = 1.5
        self.tween_list.append(tween.to(
            container=self.deck_scales,
            key=deck_index,
            end_value=1.0,
            time=0.3, 
            ease_type=tweencurves.easeOutQuart
        ))
    
    def check_deck_count_changes(self, current_deck_counts):
        """Check if any deck counts have changed and trigger animations."""
        for i, (current, previous) in enumerate(zip(current_deck_counts, self.previous_deck_counts)):
            if current != previous:
                self.animate_deck_count(i)
        self.previous_deck_counts = current_deck_counts.copy()
    
    def animate_task_text(self):
        """Animate task text with a scale-down effect."""
        self.task_text_scale = 1.1
        self.tween_list.append(tween.to(
            container=self,
            key='task_text_scale',
            end_value=1.0,
            time=0.3, 
            ease_type=tweencurves.easeOutQuart
        ))
    
    def check_task_text_changes(self, current_task_state):
        """Check if the task text has changed and trigger animation."""
        if current_task_state != self.previous_task_state:
            self.animate_task_text()
        self.previous_task_state = current_task_state
    
    def check_strike_changes(self):
        """Check if strikes have changed and trigger animations."""
        if self.strikes != self.previous_strikes:
            # Only animate the new strike that was added
            if self.strikes > self.previous_strikes:
                strike_index = self.strikes - 1  # Index of the new strike (0-based)
                if strike_index < len(self.strike_scales):
                    self.animate_strike(strike_index)
            self.previous_strikes = self.strikes
    
    def animate_strike(self, strike_index):
        """Animate a specific strike with a scale-up then scale-down effect."""
        self.strike_scales[strike_index] = 1.25
        self.tween_list.append(tween.to(
            container=self.strike_scales,
            key=strike_index,
            end_value=1.0,
            time=0.4,
            ease_type=tweencurves.easeOutBack
        ))
    
    def check_current_task_card_changes(self):
        """Check if current task cards have changed and trigger animations."""
        # Check if a new path card was assigned
        if self.current_path != self.previous_current_path and self.current_path is not None:
            self.animate_current_task_card()
        
        # Check if a new event card was assigned  
        if self.current_event != self.previous_current_event and self.current_event is not None:
            self.animate_current_task_card()
            
        self.previous_current_path = self.current_path
        self.previous_current_event = self.current_event
    
    def animate_current_task_card(self):
        """Animate current task card with a scale-up then scale-down effect."""
        self.current_task_card_scale = 1.15
        self.tween_list.append(tween.to(
            container=self,
            key='current_task_card_scale',
            end_value=1.0,
            time=0.3,
            ease_type=tweencurves.easeOutQuart
        ))
    
    def check_day_fruit_changes(self):
        """Check if day fruits have changed and trigger animations."""
        # Check each day fruit for changes
        if self.day1_fruit != self.previous_day1_fruit and self.day1_fruit is not None:
            self.animate_day_fruit(0)  # Day 1 fruit (index 0)
        
        if self.day2_fruit != self.previous_day2_fruit and self.day2_fruit is not None:
            self.animate_day_fruit(1)  # Day 2 fruit (index 1)
            
        if self.day3_fruit != self.previous_day3_fruit and self.day3_fruit is not None:
            self.animate_day_fruit(2)  # Day 3 fruit (index 2)
            
        if self.day4_fruit != self.previous_day4_fruit and self.day4_fruit is not None:
            self.animate_day_fruit(3)  # Day 4 fruit (index 3)
            
        if self.seasonal_fruit != self.previous_seasonal_fruit and self.seasonal_fruit is not None:
            self.animate_day_fruit(4)  # Seasonal fruit (index 4)
            
        # Update previous values
        self.previous_day1_fruit = self.day1_fruit
        self.previous_day2_fruit = self.day2_fruit
        self.previous_day3_fruit = self.day3_fruit
        self.previous_day4_fruit = self.day4_fruit
        self.previous_seasonal_fruit = self.seasonal_fruit

    def show_dev_alert(self, text):
        """Show developer mode alert with the given text"""
        self.dev_alert_text = text
        self.dev_alert_timer = self.dev_alert_duration

    def _handle_developer_keys(self, event):
        """Handle developer mode key presses"""
        mods = pygame.key.get_pressed()
        shift_pressed = mods[pygame.K_LSHIFT] or mods[pygame.K_RSHIFT]
        
        # Event cards - letters
        if event.key == pygame.K_f:  # Free
            self.deck_event.add_card_to_top('event_free')
            self.show_dev_alert("Added: Event Free")
        elif event.key == pygame.K_m:  # Merge
            self.deck_event.add_card_to_top('event_merge')
            self.show_dev_alert("Added: Event Merge")
        elif event.key == pygame.K_o:  # Move (O for mOve)
            self.deck_event.add_card_to_top('event_move')
            self.show_dev_alert("Added: Event Move")
        elif event.key == pygame.K_p:  # Point
            self.deck_event.add_card_to_top('event_point')
            self.show_dev_alert("Added: Event Point")
        elif event.key == pygame.K_r:  # Redraw
            self.deck_event.add_card_to_top('event_redraw')
            self.show_dev_alert("Added: Event Redraw")
        elif event.key == pygame.K_d:  # Delete (remove)
            self.deck_event.add_card_to_top('event_remove')
            self.show_dev_alert("Added: Event Remove")
        elif event.key == pygame.K_v:  # Reveal
            self.deck_event.add_card_to_top('event_reveal')
            self.show_dev_alert("Added: Event Reveal")
        elif event.key == pygame.K_s:  # Swap
            self.deck_event.add_card_to_top('event_swap')
            self.show_dev_alert("Added: Event Swap")
        
        # Path cards - numbers
        elif event.key == pygame.K_1:  # WS
            card_name = 'path_strike_WS' if shift_pressed else 'path_WS'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}WS")
        elif event.key == pygame.K_2:  # ES
            card_name = 'path_strike_ES' if shift_pressed else 'path_ES'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}ES")
        elif event.key == pygame.K_3:  # WE
            card_name = 'path_strike_WE' if shift_pressed else 'path_WE'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}WE")
        elif event.key == pygame.K_4:  # NS
            card_name = 'path_strike_NS' if shift_pressed else 'path_NS'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NS")
        elif event.key == pygame.K_5:  # NW
            card_name = 'path_strike_NW' if shift_pressed else 'path_NW'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NW")
        elif event.key == pygame.K_6:  # NE
            card_name = 'path_strike_NE' if shift_pressed else 'path_NE'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NE")
        elif event.key == pygame.K_7:  # WES
            card_name = 'path_strike_WES' if shift_pressed else 'path_WES'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}WES")
        elif event.key == pygame.K_8:  # NWS
            card_name = 'path_strike_NWS' if shift_pressed else 'path_NWS'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NWS")
        elif event.key == pygame.K_9:  # NES
            card_name = 'path_strike_NES' if shift_pressed else 'path_NES'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NES")
        elif event.key == pygame.K_0:  # NWE
            card_name = 'path_strike_NWE' if shift_pressed else 'path_NWE'
            self.deck_path.add_card_to_top(card_name, shift_pressed)
            self.show_dev_alert(f"Added: Path {'Strike ' if shift_pressed else ''}NWE")
        
        # Strike removal - Backspace
        elif event.key == pygame.K_BACKSPACE:
            if self.strikes > 0:
                self.strikes -= 1
                self.show_dev_alert(f"Strike Removed! ({self.strikes}/3)")
            else:
                self.show_dev_alert("No strikes to remove")
    
    def animate_day_fruit(self, fruit_index):
        """Animate a specific day fruit with a scale-up then scale-down effect."""
        self.day_fruit_scales[fruit_index] = 1.2
        self.tween_list.append(tween.to(
            container=self.day_fruit_scales,
            key=fruit_index,
            end_value=1.0,
            time=0.3,
            ease_type=tweencurves.easeOutQuart
        ))