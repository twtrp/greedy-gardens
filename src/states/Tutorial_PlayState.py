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
from src.states.PlayState import PlayState
from src.classes.Module_Textbox import Module_Textbox
from src.classes.Module_ClickToContinue import Module_ClickToContinue
from src.classes.Module_AllowInput import Module_AllowInput
from src.classes.Module_Arrow import Module_Arrow
from src.classes.Module_Dim import Module_Dim
from src.classes.Module_ManipulateDeck import Module_ManipulateDeck

class Tutorial_Play_StartState(Play_StartState):
    def __init__(self, game, parent, stack):
        # Call BaseState init directly to skip Play_StartState's chicken crow
        from src.template.BaseState import BaseState
        BaseState.__init__(self, game, parent, stack)

        # Copy all the state initialization from Play_StartState
        self.card_drawn = None
        self.card_drawn_image = None
        self.card_drawn_text = None

        self.seasonal_not_drawn = True
        self.day1_not_drawn = True
        self.day2_not_drawn = True
        self.magic_fruit1_not_drawn = True
        self.magic_fruit2_not_drawn = True
        self.magic_fruit3_not_drawn = True
        self.path_card_text_shown = False

        self.previous_card_drawn = None

        def on_complete():
            self.parent.transitioning = False
            self.parent.day_title_tween_chain()
        self.parent.tween_list.append(tween.to(
            container=self.parent,
            key='mask_circle_radius',
            end_value=750,
            time=1,
            ease_type=tweencurves.easeInQuint
        ).on_complete(on_complete))

        # Skip the chicken crow sound - it will play later in day_title_tween_chain

class Tutorial_PlayState(PlayState):
    def __init__(self, game, parent, stack, seed):
        PlayState.__init__(self, game, parent, stack, seed)
    
    #Main methods

    def load_assets(self):
        PlayState.load_assets(self)
        
        utils.music_load(music_channel=self.game.music_channel, name=music.play_3)
        
        self.current_step = 0
        self.show_day_title_in_tutorial = False
        
        # Delay tracking for current step
        self.step_delay_timer = 0  # Accumulated time in milliseconds
        self.step_delay_target = 0  # Target delay for current step in milliseconds
        self.step_modules_visible = False
        
        # Simulated input queue for developer skip
        self.simulated_input_queue = []
        self.simulated_input_delay = 100  # ms between inputs
        self.simulated_input_timer = 0
        
        # Flag for \ key to trigger ] on next frame
        self.trigger_skip_next_frame = False
        
        # Auto-skip mode for \ key
        self.auto_skip_active = False
        self.auto_skip_timer = 0
        self.auto_skip_delay = 100  # Dynamic delay between ] presses
        
        # Initialize visible modules list
        self.visible_modules = []

        self.tutorial_steps = [
            # Format for each step: [delay_ms, module1, module2, delay_ms, module3, ...]
            [
                1500,
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="Welcome to the farm!",
                            font=fonts.wacky_pixels,
                            size='small',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('You will spend ', colors.white),
                                ('4 days ', colors.yellow_light),
                                ('here collecting ', colors.white),
                                ('fruits.', colors.yellow_light)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        )
                    ],
                    pos=(constants.canvas_width // 2, constants.canvas_height // 2),
                    pos_anchor=posanchors.center,
                    fade_duration=800,
                ),
                1500,
                Module_ClickToContinue(tutorial_state=self, fade_duration=300)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="You can see different fruits on the farm.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Each day, ', colors.yellow_light),
                                ('you are assigned ', colors.white),
                                ('a specific fruit ', colors.yellow_light),
                                ('to collect.', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="But there's a catch!!!",
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('You must collect ', colors.white),
                                ('more fruits than your previous day', colors.yellow_light),
                                (',', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('or you will earn ', colors.white),
                                ('ZERO ', colors.yellow_light),
                                ('points for that day!', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Arrow(
                    pos=(682, 357),
                    direction='up',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This is your', colors.white),
                                (' shed.', colors.yellow_light)
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text="To collect fruits, you need to connect",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('the fruits to your shed using', colors.white),
                                (' paths.', colors.yellow_light)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    pos=(682, 422),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="Let's start the first day!",
                            font=fonts.wacky_pixels,
                            size='small',
                            color=colors.white
                        ),
                    ],
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                lambda: setattr(self, 'show_day_title_in_tutorial', True),
                self.day_title_tween_chain,
                2500,
                Module_Dim(
                    cutouts=[(1018, 52, 1270, 478)]
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('These are the ', colors.white),
                                ('cards', colors.yellow_light),
                                (':', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text="fruit cards, path cards, and event cards.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    bg=False,
                    align='right',
                    pos=(990, 265),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(1018, 52, 1270, 478)],
                    fade_duration=0
                ),
                Module_Arrow(
                    pos=(1010, 128),
                    direction='right',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Fruit cards ', colors.yellow_light),
                                ('assign fruits to each day.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='right',
                    pos=(945, 128),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(1018, 52, 1270, 478)],
                    fade_duration=0
                ),
                Module_Arrow(
                    pos=(1010, 264),
                    direction='right',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Path cards ', colors.yellow_light),
                                ('lets you place the given path.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='right',
                    pos=(945, 264),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],   
            [
                Module_Dim(
                    cutouts=[(1018, 52, 1270, 478)],
                    fade_duration=0
                ),
                Module_Arrow(
                    pos=(1010, 400),
                    direction='right',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Event cards ', colors.yellow_light),
                                ('will be explained later...', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='right',
                    pos=(945, 400),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(41, 571, 233, 680)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Let\'s ', colors.white),
                                ('draw ', colors.yellow_light),
                                ('some cards to start the game!', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Right click ', colors.yellow_light),
                                ('or press ', colors.white),
                                ('spacebar ', colors.yellow_light),
                                ('to draw cards.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_swap',
                    tutorial_state=self
                ),
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_point',
                    tutorial_state=self
                ),
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_move',
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Keep drawing cards!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=6,
                    tutorial_state=self
                ),
            ],
            [
                Module_Dim(
                    cutouts=[(1016, 475, 1270, 709)],
                ),
                Module_Arrow(
                    pos=(1010, 592),
                    direction='right',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Magic fruits ', colors.yellow_light),
                                ('will be explained later...', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='right',
                    pos=(945, 592),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(12, 54, 255, 148)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('You collect ', colors.white),
                                ('oranges ', colors.yellow_light),
                                ('today!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text="Remember, tomorrow you need to collect more",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text="peaches than you collected oranges today.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    align='left',
                    pos=(288, 101),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(12, 236, 255, 283)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This is the ', colors.white),
                                ('seasonal fruit', colors.yellow_light),
                                ('.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text="Seasonal fruits give you bonus points at the end of the game.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    bg=False,
                    align='left',
                    pos=(288, 259),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(12, 54, 255, 283)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Notice how there are ', colors.white),
                                ('6 fruit types', colors.yellow_light),
                                (',', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('but ', colors.white),
                                ('only 5 ', colors.yellow_light),
                                ('will be collected during your 4 days here.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text="So, don't assume you can collect them all.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    align='left',
                    pos=(288, 168),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_WS',
                    tutorial_state=self
                ),
                Module_Dim(
                    cutouts=[(41, 571, 233, 680)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Now that the setup is done,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Let\'s draw our first ', colors.white),
                                ('path', colors.yellow_light),
                                ('!', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Right click or press spacebar again to dismiss.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Dim(),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Normally, you can place the path anywhere you want,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='but for this tutorial, we will guide you through 2 days.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(560, 208, 640, 288)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Let\'s aim for this tile',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='for the 2 oranges.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    pos=(600, 288),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Arrow(
                    pos=(681, 238)
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Place the path on this tile!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Left click ', colors.yellow_light),
                                ('to place.', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    pos=(680, 173),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_left_click_rect=((640, 208, 719, 287)),
                    tutorial_state=self
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_WE',
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Draw another path card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Just what we need!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Arrow(
                    pos=(601, 238)
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Place the path on this tile!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(600, 173),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_left_click_rect=((560, 208, 639, 287)),
                    tutorial_state=self
                )
            ],
            [
                Module_Dim(
                    cutouts=[(14, 54, 255, 101)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="Notice how you have 2 oranges connected now.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text="Note that yellow-colored scores are not final yet,",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('as the fruits will be collected at ', colors.white),
                                ('the end of the day', colors.yellow_light),
                                ('.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='left',
                    pos=(288, 78),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[(400, 288, 560, 368)],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Next, Let\'s aim for',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='the 3 oranges here.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    pos=(480, 368),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_NWS',
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Draw another path card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [
                Module_Arrow(
                    pos=(521, 318)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((480, 288, 559, 367)),
                    tutorial_state=self
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_strike_NE',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                500,
                Module_Dim(
                    cutouts=[(579, 415, 703, 455)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Oh! A ', colors.white),
                                ('strike', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 220),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Path cards have a chance to give you a strike.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='When you get a strike,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('you will draw an ', colors.white),
                                ('event card ', colors.yellow_light),
                                ('after placing the path.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 495),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Dismiss the card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Dim(
                    cutouts=[(16, 342, 256, 456)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Once you reach ', colors.white),
                                ('3 strikes', colors.yellow_light),
                                (', the ', colors.white),
                                ('day ends', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text="So, manage your risk carefully and",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text="make sure you can get more points the next day.",
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='Remember, you get zero points if you don\'t!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text=' ',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Don\'t be too greedy!', colors.yellow_light),
                                ('.. gardens.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    align='left',
                    pos=(288, 399),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Arrow(
                    pos=(441, 318)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((400, 288, 479, 367)),
                    tutorial_state=self
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_merge',
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Draw an event card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                500,
                Module_Dim(
                    cutouts=[(548, 236, 732, 484)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This is an ', colors.white),
                                ('event card', colors.yellow_light),
                                ('.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 220),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Strikes from path cards will trigger events.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Events can ', colors.white),
                                ('save your run', colors.yellow_light),
                                (', or ', colors.white),
                                ('make it worse', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='There\'s 8 event types. Each has 2 copies in the event deck.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ), 
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 495),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Dismiss the card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Dim(),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Time to explain',
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('magic fruits', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 128, 479, 207),
                        (480, 448, 559, 527),
                        (720, 448, 799, 527),
                        (1016, 475, 1270, 709)
                    ],
                    fade_duration=0,
                    cutout_fade_duration=300
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Magic fruits are the gold apples on the board.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='They do 2 things when collected:',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('1. ', colors.green_light),
                                ('They give you ', colors.white),
                                ('1 point on the day ', colors.yellow_light),
                                ('you collect them.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('2. ', colors.green_light),
                                ('They trigger ', colors.white),
                                ('event assigned to them', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='They are optional wild cards that can be useful.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, constants.canvas_height // 2 - 25),
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                100,
                Module_Dim(
                    cutouts=[(90, 568, 182, 692)]
                ),
                Module_Arrow(
                    pos=(200, 630),
                    direction='left',
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('You can ', colors.white),
                                ('hover ', colors.yellow_light),
                                ('over the event card', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='to read it with clearer text. Try it!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    align='left',
                    pos=(270, 630),
                    pos_anchor=posanchors.midleft,
                ),
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Looking at the board,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='taking away any path',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='hurts our plan of',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='collecting oranges.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='The best we can do',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='is to take away',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='the path farthest',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='from the shed.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg_opacity=255,
                    align='left',
                    pos=(840, constants.canvas_height // 2),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 208, 480, 288),
                        (640, 128, 720, 208)
                    ],
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Let\'s take away the farthest path,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='and merge with the closer one',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('to create a ', colors.white),
                                ('4-directional path', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    pos=(640, 488)
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Arrow(
                    pos=(441, 319)
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Select this tile first.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(440, 254),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_left_click_rect=((401, 289, 479, 367)),
                    tutorial_state=self
                )
            ],
            [
                Module_Arrow(
                    pos=(681, 239)
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Then select this tile to complete the merge.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(680, 144),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_left_click_rect=((641, 209, 719, 287)),
                    tutorial_state=self
                )
            ],
                        [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_strike_ES',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Another strike..',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_Arrow(
                    pos=(521, 238)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((480, 208, 559, 287)),
                    tutorial_state=self
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_reveal',
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Draw an event card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_strike_NS',
                    tutorial_state=self
                ),
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_NE',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=(90, 568, 182, 692),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_left_click_rect=(445, 668, 838, 719),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_left_click_rect=(357, 299, 917, 326),
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Since we are at 2/3 strikes, let\'s reveal paths',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='to see when the day is ending.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    align='center',
                    pos=(constants.canvas_width // 2, 612),
                )
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Looks like we only have 2 paths left today.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                Module_Arrow(
                    pos=(441, 318)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((400, 288, 479, 367)),
                    tutorial_state=self
                )
            ],
            [
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                )
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 208, 480, 288),
                        (640, 128, 720, 208)
                    ]
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This is the ', colors.white),
                                ('final path ', colors.yellow_light),
                                ('of today.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='We can go for the orange on top of the shed,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='But let\'s not get too greedy, as we',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='have to collect 6 peaches tomorrow.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='Might as well go for the seasonal fruits now.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                    pos=(640, 500)
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Arrow(
                    pos=(441, 238)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((400, 208, 479, 287)),
                    tutorial_state=self
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_redraw',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(539, 472, 738, 514),
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=(90, 568, 182, 692),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                   allow_left_click_rect=(445, 668, 838, 719),
                    auto_advance=False,
                    tutorial_state=self
                ), 
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Let\'s do nothing since',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='our plans are going well.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg_opacity=255,
                    align='left',
                    pos=(840, constants.canvas_height // 2),
                    pos_anchor=posanchors.midleft,
                )
            ],
            [
                1350,
                Module_AllowInput(
                    allow_left_click_rect=(0, 0, constants.canvas_width, constants.canvas_height),
                    tutorial_state=self
                )
            ],
            [
                2500,
                Module_Dim(),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('It\'s ', colors.white),
                                ('day 2', colors.yellow_light),
                                ('!', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text='5 points from the first day are locked in.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='Today, you must collect at least 6 points!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Draw next day\'s fruit!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=4,
                    tutorial_state=self
                ),
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Time to collect peaches!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_Arrow(
                    pos=(681, 398)
                ),
                Module_AllowInput(
                    allow_left_click_rect=((640, 368, 719, 447)),
                    tutorial_state=self
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_swap',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_Dim(
                    cutouts=[
                        (480, 288, 560, 368),
                        (640, 368, 720, 448)
                    ]
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Looking at the board,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='the most harmless',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='swap would be these',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='two tiles.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg_opacity=255,
                    align='left',
                    pos=(840, constants.canvas_height // 2),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=((480, 288, 559, 367)),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(521, 318)
                )
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=((640, 368, 719, 447)),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(681, 398)
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_NW',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [   
                Module_AllowInput(
                    allow_left_click_rect=(560, 448, 639, 527),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(601, 478)
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_NS',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [  
                Module_AllowInput(
                    allow_left_click_rect=(720, 368, 799, 447),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(761, 398)
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_strike_ES',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(560, 368, 639, 447),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(601, 398)
                )
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_remove',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                ),
            ],
            [
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Looking at the board,',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='let\'s remove the detached',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='path to the bottom right.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Since the ', colors.white),
                                ('magic fruit ', colors.yellow_light),
                                ('could', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='be useful, we should keep',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='the path to it.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg_opacity=255,
                    align='left',
                    pos=(840, constants.canvas_height // 2),
                    pos_anchor=posanchors.midleft,
                ),
                Module_ClickToContinue(tutorial_state=self, pos=(constants.canvas_width/2, 655))
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(720, 368, 799, 447),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(761, 398)
                ),
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(567, 677, 693, 709),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(constants.canvas_width // 2, 670)
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='path',
                    card_name='path_strike_NW',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self
                )
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Oh no! Looks like we ', colors.white),
                                ('failed ', colors.red_light),
                                ('today.', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('There\'s no way we can get ', colors.white),
                                ('3 more points, ', colors.yellow_light),
                                ('right?', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='Let\'s just prepare for strawberries tomorrow.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(640, 608)
                ),
                Module_AllowInput(
                    allow_left_click_rect=(720, 208, 799, 287),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(761, 238)
                ),
            ],
            [
                Module_ManipulateDeck(
                    deck_type='event',
                    card_name='event_free',
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                500,
                Module_Dim(
                    cutouts=[(548, 236, 732, 484)],
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                           text="Wait!",
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        )
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 220),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This event could save day 2', colors.yellow_light),
                                ('!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, 495),
                    pos_anchor=posanchors.midtop,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Dismiss the card.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 670),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                Module_Arrow(
                    pos=(200, 630),
                    direction='left',
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Let\'s read what this event does.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    align='left',
                    pos=(270, 630),
                    pos_anchor=posanchors.midleft,
                ),
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 128, 479, 207),
                        (480, 448, 559, 527),
                        (720, 448, 799, 527),
                        (1016, 475, 1270, 709)
                    ],
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Remember ', colors.white),
                                ('magic fruits', colors.yellow_light),
                                ('?', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='It\'s time to use them.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2, constants.canvas_height // 2 - 25),
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                # Module_Dim(
                #     cutouts=[
                #         (1027, 557, 1095, 681),
                #         (1095, 557, 1119, 565),
                #         (1095, 565, 1097, 567),
                #         (1097, 567, 1165, 691),
                #         (1165, 567, 1189, 575),
                #     ],
                #     fade_duration=0,
                # ),
                Module_AllowInput(
                    allow_hover_rect=(1025, 555, 1164, 690),
                    auto_advance=False,
                    tutorial_state=self,
                ),
                Module_AllowInput(
                    allow_hover_rect=(1164, 567, 1188, 574),
                    auto_advance=False,
                    tutorial_state=self,
                ),
                Module_Arrow(
                    pos=(1010, 614),
                    direction='right',
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Let\'s read what the events',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='of magic fruit 1 and 2 do.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        )
                    ],
                    align='right',
                    pos=(945, 614),
                    pos_anchor=posanchors.midright,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 128, 479, 207),
                        (1027, 557, 1095, 681),
                        (1095, 557, 1119, 565),
                        (1095, 565, 1097, 567),
                    ]
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('We need ', colors.white),
                                ('3 more points ', colors.yellow_light),
                                ('to pass today.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text='Here\'s the plan:',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='First, we place a free path to connect',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='to magic fruit 1.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('That\'s ', colors.white),
                                ('+1 point', colors.yellow_light),
                                ('from magic fruit 1.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    bg=False,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(
                    cutouts=[
                        (400, 128, 479, 207),
                        (480, 448, 559, 527),
                        (1027, 557, 1095, 681),
                        (1095, 557, 1119, 565),
                        (1095, 565, 1097, 567),
                        (1097, 567, 1165, 691),
                        (1165, 567, 1189, 575),
                    ],
                    fade_duration=0,
                ),
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('Then, we use ', colors.white),
                                ('"move" event ', colors.yellow_light),
                                ('from magic fruit 1', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='to move a path to connect to',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='magic fruit 2, like a chain!',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('+1 point ', colors.yellow_light),
                                ('from magic fruit 2.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('+1 point ', colors.yellow_light),
                                ('from magic fruit 2 event.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('That\'s ', colors.white),
                                ('+3 points ', colors.yellow_light),
                                ('in total!', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                    ],
                    bg=False,
                    pos=(constants.canvas_width // 2 + 150, constants.canvas_height // 2)
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_AllowInput(
                    allow_scroll_down=1,
                    tutorial_state=self
                ),
                Module_Arrow(
                    direction='left',
                    pos=(344, 455)
                ),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Select this free path.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Scroll mouse down ', colors.yellow_light),
                                ('or ', colors.white),
                                ('press arrow key down', colors.yellow_light),
                                ('.', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        ),
                    ],
                    pos=(414, 455),
                    pos_anchor=posanchors.midleft,
                )
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=((400, 128, 479, 207)),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(441, 158)
                )
            ],
            [
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(400, 288, 479, 367),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(441, 318)
                )
            ],
            [
                Module_AllowInput(
                    allow_left_click_rect=(480, 448, 559, 527),
                    tutorial_state=self
                ),
                Module_Arrow(
                    pos=(521, 478)
                )
            ],
            [
                Module_AllowInput(
                    allow_draw_card=1,
                    tutorial_state=self
                )
            ],
            [
                Module_AllowInput(
                    allow_hover_rect=((90, 568, 182, 692)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                    allow_hover_rect=((1017, 544, 1265, 706)),
                    auto_advance=False,
                    tutorial_state=self
                ),
                Module_AllowInput(
                   allow_left_click_rect=(445, 668, 838, 719),
                    auto_advance=False,
                    tutorial_state=self
                ), 
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Select +1 today, -1 tomorrow.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    pos=(constants.canvas_width // 2, 618),
                ),
                Module_AllowInput(
                    allow_left_click_rect=(438, 237, 837, 333),
                    tutorial_state=self
                )
            ],
            [
                1100,
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Phew.. That was clutch!',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        )
                    ],
                    pos=(constants.canvas_width // 2, 608)
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            [
                Module_Dim(),
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='You\'ve completed the tutorial!',
                            font=fonts.wacky_pixels,
                            size='medium',
                            color=colors.green_light
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.green_light
                        ),
                        utils.get_text(
                            text='Every game is different, so adapt your strategy!',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='Sometimes taking risks pays off, but know when to play safe!',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.green_light
                        ),
                        utils.get_text(
                            text='Chase your high score or challenge friends on the same seed.',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='(most fun via Discord streams!)',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.yellow_light
                        ),
                        utils.get_text(
                            text='',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.green_light
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('Quit the tutorial by pressing ', colors.white),
                                ('ESC ', colors.yellow_light),
                                ('then ', colors.white),
                                ('Exit', colors.yellow_light),
                                (',', colors.white),
                            ],
                            font=fonts.wacky_pixels,
                            size='smaller',
                        ),
                        utils.get_text(
                            text='or continue playing to practice more.',
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_text(
                            text='(Note that tutorial scores will not be saved.)',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg_opacity=255,
                ),
                1000,
                Module_ClickToContinue(tutorial_state=self)
            ],
        ]
        
        # Initialize delay for first step
        self._init_step_delay()

    def _init_step_delay(self):
        """Initialize delay timer for current step"""
        step_data = self.tutorial_steps[self.current_step]
        # Check if first element is a number (delay in milliseconds)
        if step_data and isinstance(step_data[0], (int, float)):
            self.step_delay_target = step_data[0]
            self.step_delay_timer = 0
            self.step_modules_visible = False
        else:
            # No delay, show immediately
            self.step_delay_target = 0
            self.step_delay_timer = 0
            self.step_modules_visible = True

    def _get_step_modules_with_delays(self):
        """Parse step data and separate delays, modules, and functions"""
        step_data = self.tutorial_steps[self.current_step]
        modules_with_delays = []
        
        for item in step_data:
            if isinstance(item, (int, float)):
                modules_with_delays.append(('delay', item))
            elif callable(item):
                modules_with_delays.append(('function', item))
            else:
                modules_with_delays.append(('module', item))
        
        return modules_with_delays



    def _update_inject(self, dt, events):
        # Process simulated input queue first
        simulating = False
        if self.simulated_input_queue:
            simulating = True
            
            # If timer hasn't started (is 0), execute action immediately
            if self.simulated_input_timer == 0:
                action = self.simulated_input_queue.pop(0)
                
                if action[0] == 'delay':
                    # Start delay timer with custom delay value
                    self.simulated_input_timer = 0.001
                    self.simulated_input_delay_target = action[1]
                elif action[0] == 'function':
                    action[1]()
                elif action[0] == 'draw_card':
                    # Create and directly send a spacebar event to substates
                    if self.substate_stack:
                        # Temporarily disable transitioning and enable day title to allow input
                        was_transitioning = self.transitioning
                        was_shown_day_title = self.shown_day_title
                        self.transitioning = False
                        self.shown_day_title = True
                        keydown_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
                        self.substate_stack[-1].update(dt=dt, events=[keydown_event])
                        self.transitioning = was_transitioning
                        self.shown_day_title = was_shown_day_title
                elif action[0] == 'scroll_down':
                    # Create and send a scroll down event (button 5) to substates
                    if self.substate_stack:
                        was_transitioning = self.transitioning
                        self.transitioning = False
                        scroll_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pygame.mouse.get_pos(), 'button': 5})
                        self.substate_stack[-1].update(dt=dt, events=[scroll_event])
                        self.transitioning = was_transitioning
                elif action[0] == 'left_click':
                    item, pos = action[1], action[2]
                    was_transitioning = self.transitioning
                    self.transitioning = False
                    
                    # Check if we have a substate with its own button_list (like Play_PlayEventState)
                    if self.substate_stack and hasattr(self.substate_stack[-1], 'button_list'):
                        substate_button_list = self.substate_stack[-1].button_list
                    else:
                        substate_button_list = []
                    
                    # Get active module for consuming clicks
                    active_module = self._get_active_allow_input_module()
                    if active_module and hasattr(active_module, 'allow_left_click_rects'):
                        # Set _last_clicked_rect_idx before clicking
                        for idx, rect in enumerate(active_module.allow_left_click_rects):
                            screen_rect = utils.canvas_rect_to_screen(rect, self.game)
                            screen_x1, screen_y1, screen_x2, screen_y2 = screen_rect
                            if screen_x1 <= pos[0] <= screen_x2 and screen_y1 <= pos[1] <= screen_y2:
                                active_module._last_clicked_rect_idx = idx
                                break
                    
                    # Check substate buttons FIRST (event choice buttons are here!)
                    found_button = False
                    for button in substate_button_list:
                        if button.rect.collidepoint(pos):
                            # MOVE THE ACTUAL MOUSE CURSOR to the click position
                            pygame.mouse.set_pos(pos)
                            # Create fake mouse events to properly trigger the button
                            fake_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})
                            fake_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': pos, 'button': 1})
                            if self.substate_stack:
                                self.substate_stack[-1].update(dt=dt, events=[fake_down, fake_up])
                            # DON'T consume here - the substate will consume it when it processes button.clicked
                            found_button = True
                            break
                    
                    if not found_button:
                        # Then check parent button_list
                        for button in self.button_list:
                            if button.rect.collidepoint(pos):
                                button.simulate_click()
                                if self.substate_stack:
                                    self.substate_stack[-1].update(dt=dt, events=[])
                                # Consume the click
                                if active_module and active_module.allow_left_click_rect is not None:
                                    active_module.consume_left_click()
                                found_button = True
                                break
                    
                    if not found_button:
                        # Finally check grid buttons
                        for button in self.grid_buttons:
                            if button.rect.collidepoint(pos):
                                button.simulate_click()
                                if self.substate_stack:
                                    self.substate_stack[-1].update(dt=dt, events=[])
                                # Consume the click
                                if active_module and active_module.allow_left_click_rect is not None:
                                    active_module.consume_left_click()
                                found_button = True
                                break
                    
                    self.transitioning = was_transitioning
                elif action[0] == 'jump_step':
                    self.current_step = action[1]
                    self.simulated_input_timer = 0  # Reset for next use
                    return  # Don't wait after jumping
                else:
                    # For non-delay actions, start normal delay timer
                    self.simulated_input_timer = 0.001  # Small non-zero value to indicate delay started
                    self.simulated_input_delay_target = self.simulated_input_delay
            
            # Wait for delay after action
            self.simulated_input_timer += dt * 1000
            delay_target = getattr(self, 'simulated_input_delay_target', self.simulated_input_delay)
            if self.simulated_input_timer >= delay_target:
                self.simulated_input_timer = 0  # Reset for next action
                self.simulated_input_delay_target = self.simulated_input_delay  # Reset to default
        
        # Don't process manual skip keys while simulating
        if simulating:
            return
        
        # Developer mode: skip tutorial step with ] key, \ starts auto-skip
        if debug.debug_developer_mode:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHTBRACKET:
                        self._skip_to_next_step()
                        return
                    elif event.key == pygame.K_BACKSLASH:
                        # Start/stop auto-skip mode
                        self.auto_skip_active = not self.auto_skip_active
                        self.auto_skip_timer = 0
                        if self.auto_skip_active:
                            self._calculate_auto_skip_delay()
                        return
        
        # Auto-skip mode: trigger ] with dynamic delay (only when queue is empty)
        if self.auto_skip_active and not self.simulated_input_queue:
            self.auto_skip_timer += dt * 1000
            if self.auto_skip_timer >= self.auto_skip_delay:
                self.auto_skip_timer = 0
                # Stop at last step (don't go out of bounds)
                if self.current_step < len(self.tutorial_steps) - 1:
                    self._skip_to_next_step()
                    # Calculate delay for next step
                    self._calculate_auto_skip_delay()
                else:
                    # Stop auto-skip when reaching last step
                    self.auto_skip_active = False
        
        # Check if current step exists
        if self.current_step >= len(self.tutorial_steps):
            return
        
        # Reset queue when step changes
        if not hasattr(self, 'module_queue') or getattr(self, 'previous_step', None) != self.current_step:
            self.previous_step = self.current_step
            self.module_queue = self._get_step_modules_with_delays()
            self.current_queue_index = 0
            self.queue_delay_timer = 0
            self.visible_modules = []
        
        # Process queue
        while self.current_queue_index < len(self.module_queue):
            item_type, item_value = self.module_queue[self.current_queue_index]
            
            if item_type == 'delay':
                self.queue_delay_timer += dt * 1000
                if self.queue_delay_timer >= item_value:
                    self.queue_delay_timer = 0
                    self.current_queue_index += 1
                else:
                    break
            elif item_type == 'function':
                # Execute the function and move to next item
                item_value()
                self.current_queue_index += 1
            else:
                # It's a module
                self.visible_modules.append(item_value)
                self.current_queue_index += 1
        
        # Track step before updating modules
        step_before_update = self.current_step
        
        # Update all visible modules
        for module in self.visible_modules:
            module.update(dt, events)
        
        # If step changed during module update (e.g., ClickToContinue was clicked),
        # filter out mouse button events to prevent them from being processed by the new step
        if step_before_update != self.current_step:
            # Remove MOUSEBUTTONDOWN events that caused the step change
            events.clear()
    


    def _calculate_auto_skip_delay(self):
        """Calculate delay: 100ms base + 100ms per input"""
        if self.current_step >= len(self.tutorial_steps):
            self.auto_skip_delay = 100
            return
        
        delay = 100  # Base delay
        
        # Add 100ms for each input in current step
        step_data = self.tutorial_steps[self.current_step]
        for item in step_data:
            if hasattr(item, '__class__') and item.__class__.__name__ == 'Module_AllowInput':
                if item.allow_draw_card > 0:
                    delay += item.allow_draw_card * 100
                if item.allow_scroll_down > 0:
                    delay += item.allow_scroll_down * 100
                if item.allow_left_click_rect:
                    delay += 100
        
        self.auto_skip_delay = delay
    
    def _skip_to_next_step(self):
        """Queue remaining inputs for current step, then advance to next step"""
        # Don't skip if already at or past the last step
        if self.current_step >= len(self.tutorial_steps):
            return
        
        # Clear any existing queue
        self.simulated_input_queue = []
        
        # Queue functions, delays (only 1350ms and 1100ms), and inputs from current step
        step_data = self.tutorial_steps[self.current_step]
        for item in step_data:
            if isinstance(item, (int, float)):
                # Only keep the 1350ms and 1100ms delays (end of day 1), skip all others
                if item == 1350 or item == 1100:
                    self.simulated_input_queue.append(('delay', item))
            elif callable(item) and item != self.day_title_tween_chain:
                # Skip day_title_tween_chain to prevent it from playing again
                self.simulated_input_queue.append(('function', item))
            elif hasattr(item, '__class__') and item.__class__.__name__ == 'Module_AllowInput':
                # Only queue inputs from modules that contribute to auto-advance
                if not getattr(item, 'auto_advance', False):
                    continue
                    
                # Queue draw card inputs
                if item.allow_draw_card > 0:
                    for _ in range(item.allow_draw_card):
                        self.simulated_input_queue.append(('draw_card', item))
                # Queue scroll down inputs
                if item.allow_scroll_down > 0:
                    for _ in range(item.allow_scroll_down):
                        self.simulated_input_queue.append(('scroll_down', item))
                # Queue left click input
                if item.allow_left_click_rect:
                    x1, y1, x2, y2 = item.allow_left_click_rect
                    # Calculate center in canvas coordinates
                    canvas_center_x = (x1 + x2) // 2
                    canvas_center_y = (y1 + y2) // 2
                    
                    # Convert to screen coordinates using centralized utility
                    screen_x, screen_y = utils.canvas_to_screen((canvas_center_x, canvas_center_y), self.game)
                    
                    self.simulated_input_queue.append(('left_click', item, (screen_x, screen_y)))
        
        # Queue jump to next step
        self.simulated_input_queue.append(('jump_step', self.current_step + 1))
        self.simulated_input_timer = 0
    
    def _get_active_allow_input_module(self):
        """Get the currently active Module_AllowInput if one exists, or return default blocking module"""
        # If current step is out of bounds, allow all inputs (tutorial finished)
        if self.current_step >= len(self.tutorial_steps):
            return None
        
        if hasattr(self, 'visible_modules'):
            # Collect all Module_AllowInput modules
            allow_input_modules = [m for m in self.visible_modules if isinstance(m, Module_AllowInput)]
            
            if len(allow_input_modules) == 1:
                # Cache single module
                cache_key = (self.current_step, id(allow_input_modules[0]))
                if not hasattr(self, '_cached_module') or self._cached_module_key != cache_key:
                    self._cached_module_key = cache_key
                    self._cached_module = allow_input_modules[0]
                return self._cached_module
            elif len(allow_input_modules) > 1:
                # Cache merged module by step and module ids
                cache_key = (self.current_step, tuple(id(m) for m in allow_input_modules))
                if hasattr(self, '_cached_module') and self._cached_module_key == cache_key:
                    return self._cached_module
                # Merge multiple Module_AllowInput modules
                # Keep all rects available for checking, but only count inputs
                # from modules that requested auto_advance towards the total required.
                merged = Module_AllowInput(
                    allow_draw_card=0,
                    allow_left_click_rect=None,
                    allow_hover_rect=None,
                    auto_advance=any(m.auto_advance for m in allow_input_modules),  # Auto-advance if any module requests it
                    tutorial_state=self
                )

                # Collect all allowed click rects (for input checking)
                click_rects = []
                click_rects_adv_flags = []
                for m in allow_input_modules:
                    if m.allow_left_click_rect is not None:
                        click_rects.append(m.allow_left_click_rect)
                        # This rect advances only if the originating module wanted auto_advance
                        click_rects_adv_flags.append(bool(m.auto_advance))

                if click_rects:
                    merged.allow_left_click_rect = click_rects[0]
                    merged.allow_left_click_rects = click_rects
                    merged.allow_left_click_rects_adv_flags = click_rects_adv_flags

                # Collect all allowed hover rects (for input checking)
                hover_rects = []
                hover_rects_adv_flags = []
                for m in allow_input_modules:
                    if m.allow_hover_rect is not None:
                        hover_rects.append(m.allow_hover_rect)
                        hover_rects_adv_flags.append(bool(m.auto_advance))

                if hover_rects:
                    merged.allow_hover_rect = hover_rects[0]
                    merged.allow_hover_rects = hover_rects
                    merged.allow_hover_rects_adv_flags = hover_rects_adv_flags

                # Recalculate total_required for merged module by summing only
                # inputs coming from modules that have auto_advance=True
                merged.total_required = 0
                # draw card counts from modules that auto-advance
                for m in allow_input_modules:
                    if m.auto_advance and m.allow_draw_card > 0:
                        merged.total_required += m.allow_draw_card

                # count left-click rects belonging to modules that auto-advance
                if hasattr(merged, 'allow_left_click_rects_adv_flags'):
                    merged.total_required += sum(1 for f in merged.allow_left_click_rects_adv_flags if f)

                # count hover rects belonging to modules that auto-advance
                if hasattr(merged, 'allow_hover_rects_adv_flags'):
                    merged.total_required += sum(1 for f in merged.allow_hover_rects_adv_flags if f)

                # Cache the merged module
                self._cached_module_key = cache_key
                self._cached_module = merged
                return merged
        
        # Default: block all inputs in tutorial mode
        return Module_AllowInput()

    def _render_inject(self, canvas):
        # Don't render modules if tutorial is finished
        if self.current_step >= len(self.tutorial_steps):
            return
        
        if hasattr(self, 'visible_modules'):
            for module in self.visible_modules:
                module.render(canvas)


    #Class methods

    def _create_start_state(self):
        """Override to use Tutorial_Play_StartState instead of Play_StartState"""
        Tutorial_Play_StartState(game=self.game, parent=self, stack=self.substate_stack).enter_state()

    def day_title_tween_chain(self):
        """Override to conditionally show day title animation in tutorial"""
        if self.show_day_title_in_tutorial:
            # Play the normal animation with sound
            utils.sound_play(sound=sfx.chicken_crowing, volume=self.game.sfx_volume)
            PlayState.day_title_tween_chain(self)
        else:
            # Skip animation
            self.shown_day_title = True
            self.day_title_text = None
            self.day_title_text_props = None
