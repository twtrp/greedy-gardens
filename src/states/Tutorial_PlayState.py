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
from src.classes.Module_Text import Module_Text
from src.classes.Module_ClickToContinue import Module_ClickToContinue
import tween
import math

class Tutorial_PlayState(PlayState):
    def __init__(self, game, parent, stack, seed):
        PlayState.__init__(self, game, parent, stack, seed)
    
    #Main methods

    def load_assets(self):
        PlayState.load_assets(self)
        
        utils.music_load(music_channel=self.game.music_channel, name=music.play_3)
        
        self.current_step = 0
        self.show_day_title_in_tutorial = False
        self.block_gameplay_input = True  # Block spacebar/right-click during tutorial steps
        
        # Delay tracking for current step
        self.step_delay_timer = 0  # Accumulated time in milliseconds
        self.step_delay_target = 0  # Target delay for current step in milliseconds
        self.step_modules_visible = False

        self.tutorial_steps = {
            # Format: [delay_ms, module1, module2, ...] or just [module1, module2, ...] for no delay
            0: [
                2000,
                Module_Text(
                    content=[
                        utils.get_text(
                            text="Welcome to the farm!",
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                        utils.get_multicolor_text(
                            texts=[
                                ('You will spend', colors.white),
                                (' 4 days ', colors.yellow_light),
                                ('here collecting fruits.', colors.white)
                            ],
                            font=fonts.wacky_pixels,
                            size='tiny',
                        )
                    ],
                    textbox=True,
                    align='center',
                    pos=(constants.canvas_width // 2, constants.canvas_height // 2),
                    pos_anchor=posanchors.center,
                    fade_duration=800,
                ),
                1300,
                Module_ClickToContinue(tween_list=self.tween_list, tutorial_state=self)
            ],
            1: [
                Module_Text(
                    content=[
                        utils.get_text(
                            text="dummy",
                            font=fonts.wacky_pixels,
                            size='smaller',
                            color=colors.white
                        ),
                    ]
                )
            ]
        }
        
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
        """Parse step data and separate delays from modules"""
        step_data = self.tutorial_steps[self.current_step]
        modules_with_delays = []
        
        for item in step_data:
            if isinstance(item, (int, float)):
                modules_with_delays.append(('delay', item))
            else:
                modules_with_delays.append(('module', item))
        
        return modules_with_delays

    def _update_inject(self, dt, events):
        # Check if current step exists
        if self.current_step not in self.tutorial_steps:
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
            else:
                self.visible_modules.append(item_value)
                self.current_queue_index += 1
        
        # Update all visible modules
        for module in self.visible_modules:
            module.update(dt, events)

    def _render_inject(self, canvas):
        if hasattr(self, 'visible_modules'):
            for module in self.visible_modules:
                module.render(canvas)


    #Class methods

    def day_title_tween_chain(self):
        """Override to conditionally show day title animation in tutorial"""
        if self.show_day_title_in_tutorial:
            # Play the normal animation
            PlayState.day_title_tween_chain(self)
        else:
            # Skip animation
            self.shown_day_title = True
            self.day_title_text = None
            self.day_title_text_props = None
