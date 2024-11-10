from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Play_StartState import Play_StartState
from src.classes.Card import Card
from src.classes.Deck import Deck
from src.classes.GameBoard import GameBoard
import tween

class PlayState(BaseState):
    def __init__(self, game, parent, stack, seed):
        BaseState.__init__(self, game, parent, stack, seed)

        self.game.canvas.fill((0, 0, 0))
        print(seed)

        # config of gui
        self.box_width = 272

        # create deck
        self.deck_fruit = Deck('fruit')
        self.deck_path = Deck('path')
        self.deck_event = Deck('event')

        self.drawn_cards_fruit = []
        self.drawn_cards_path = []
        self.drawn_cards_event = []

        # value
        self.day1_score = 0
        self.day2_score = 1
        self.day3_score = 2
        self.day4_score = 3
        self.seasonal_score = 4
        self.fruit_deck_remaining = Deck.remaining_cards(self.deck_fruit)
        self.path_deck_remaining = Deck.remaining_cards(self.deck_path)
        self.event_deck_remaining = Deck.remaining_cards(self.deck_event)

        self.day1_fruit = None
        self.day2_fruit = None
        self.day3_fruit = None
        self.day4_fruit = None
        self.seasonal_fruit = None
        
        # define board
        self.game_board = GameBoard()
        #function and example for use in gen map and place path
        #self.game_board.set_path(index, path_type)
        #self.game_board.add_fruit(index, fruit_type, value)
        #self.game_board.set_home(index)
        #self.game_board.set_magic_fruit(index,num)

        # stack and state
        self.substate_stack = []

        self.started = False
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

        # left gui
        self.left_box_title = utils.get_text(text='Score', font=fonts.lf2, size='small', color=colors.white)

        self.score_list = [
            {'text': 'Day 1',},
            {'text': 'Day 2',},
            {'text': 'Day 3',},
            {'text': 'Day 4',},
            {'text': 'Seasonal',},
            {'text': 'Total',},
        ]

        self.score_title_list = []
        for score in self.score_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=colors.white)
            self.score_title_list.append(text)

        self.left_box_strike = utils.get_text(text='Event Strikes', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_task = utils.get_text(text='Current task', font=fonts.lf2, size='small', color=colors.white)
        self.left_box_path_text = utils.get_text(text='Place drawn path', font=fonts.lf2, size='tiny', color=colors.white)

        self.blank_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_blank')

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

    def update(self, dt, events):
        if self.ready:

            # Update substates
            if self.substate_stack:
                self.substate_stack[-1].update(dt=dt, events=events)

            # Update tweens
            tween.update(passed_time=dt)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.started:
                    # for testing
                    Play_StartState(game=self.game, parent=self, stack=self.substate_stack).enter_state()
                    self.started = True
                if event.key == pygame.K_ESCAPE:
                        self.exit_state()

        self.fruit_deck_remaining = Deck.remaining_cards(self.deck_fruit)
        self.path_deck_remaining = Deck.remaining_cards(self.deck_path)
        self.event_deck_remaining = Deck.remaining_cards(self.deck_event)

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        
        if self.ready:

            # Build background

            ## Render landscape to menu_bg
            for layer in self.landscape_list:
                utils.blit(dest=canvas, source=layer['image'], pos=(0, 0))
                
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
            scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)
            for i in range(3):
                    utils.blit(dest=canvas, source=scaled_blank_strike, pos=(40 + i*64, 420), pos_anchor='topleft')
            scaled_card_pathtest_back = pygame.transform.scale_by(surface=self.card_path_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_pathtest_back, pos=(self.box_width/2, 640), pos_anchor='center')
            ## Render Day's Fruit
            if self.day1_fruit:
                self.day1_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day1_fruit)
                scaled_day1_fruit_image = pygame.transform.scale_by(surface=self.day1_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_day1_fruit_image, pos=(40, 95), pos_anchor='center')
            if self.day2_fruit:
                self.day2_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day2_fruit)
                scaled_day2_fruit_image = pygame.transform.scale_by(surface=self.day2_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_day2_fruit_image, pos=(40, 140), pos_anchor='center')
            if self.day3_fruit:
                self.day3_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day3_fruit)
                scaled_day3_fruit_image = pygame.transform.scale_by(surface=self.day3_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_day3_fruit_image, pos=(40, 185), pos_anchor='center')
            if self.day4_fruit:
                self.day4_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.day4_fruit)
                scaled_day4_fruit_image = pygame.transform.scale_by(surface=self.day4_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_day4_fruit_image, pos=(40, 230), pos_anchor='center')
            if self.seasonal_fruit:
                self.seasonal_fruit_image = utils.get_sprite(sprite_sheet=spritesheets.fruit_16x16, target_sprite=self.seasonal_fruit)
                scaled_seasonal_fruit_image = pygame.transform.scale_by(surface=self.seasonal_fruit_image, factor=1.25)
                utils.blit(dest=canvas, source=scaled_seasonal_fruit_image, pos=(40, 275), pos_anchor='center')

            # Render value in left white box
            self.total_score = self.day1_score + self.day2_score + self.day3_score + self.day4_score + self.seasonal_score

            self.day1_score_amount = utils.get_text(text=str(self.day1_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.day1_score_amount, pos=(240, 80), pos_anchor='topright')
            self.day2_score_amount = utils.get_text(text=str(self.day2_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.day2_score_amount, pos=(240, 125), pos_anchor='topright')
            self.day3_score_amount = utils.get_text(text=str(self.day3_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.day3_score_amount, pos=(240, 170), pos_anchor='topright')
            self.day4_score_amount = utils.get_text(text=str(self.day4_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.day4_score_amount, pos=(240, 215), pos_anchor='topright')
            self.seasonal_score_amount = utils.get_text(text=str(self.seasonal_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.seasonal_score_amount, pos=(240, 260), pos_anchor='topright')
            self.total_score_amount = utils.get_text(text=str(self.total_score), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.total_score_amount, pos=(240, 305), pos_anchor='topright')
            
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
                # utils.blit(dest=canvas, source=, pos=(1150, 135 + i*125), pos_anchor='topleft') # card amount
            utils.blit(dest=canvas, source=self.right_magic_fruits, pos=(constants.canvas_width - self.box_width/2, 475), pos_anchor='center')

            # Render image in right white box
            scaled_card_fruit_back = pygame.transform.scale_by(surface=self.card_fruit_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_fruit_back, pos=(1079, 125), pos_anchor='center')
            scaled_card_path_back = pygame.transform.scale_by(surface=self.card_path_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_path_back, pos=(1079, 250), pos_anchor='center')
            scaled_card_event_back = pygame.transform.scale_by(surface=self.card_event_back_image, factor=0.875)
            utils.blit(dest=canvas, source=scaled_card_event_back, pos=(1079, 375), pos_anchor='center')

            # Render value in right white box
            self.fruit_deck_remaining_amount = utils.get_text(text=str(self.fruit_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.fruit_deck_remaining_amount, pos=(1150, 135), pos_anchor='topleft')
            self.path_deck_remaining_amount = utils.get_text(text=str(self.path_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.path_deck_remaining_amount, pos=(1150, 260), pos_anchor='topleft')
            self.event_deck_remaining_amount = utils.get_text(text=str(self.event_deck_remaining), font=fonts.lf2, size='smaller', color=colors.white)
            utils.blit(dest=canvas, source=self.event_deck_remaining_amount, pos=(1150, 385), pos_anchor='topleft')

            if not self.substate_stack:

                # ## Render menu options
                # for i, option in enumerate(self.title_button_option_surface_list):
                #     processed_option = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                #     processed_option.set_alpha(option['alpha'])
                #     utils.blit(dest=canvas, source=processed_option, pos=(constants.canvas_width/2, 340 + i*80), pos_anchor='center')

                pass

            else:
                self.substate_stack[-1].render(canvas=canvas)          
                

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