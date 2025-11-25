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
import tween
import math

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

        self.tutorial_steps = [
            # Format for each step: [delay_ms, module1, module2, delay_ms, module3, ...]
            [
                1500,
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text="Welcome to the farm!",
                            font=fonts.wacky_pixels,
                            size='smaller',
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
                Module_ClickToContinue(tween_list=self.tween_list, tutorial_state=self)
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
                        )
                    ],
                ),
                1000,
                Module_ClickToContinue(tween_list=self.tween_list, tutorial_state=self)
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_multicolor_text(
                            texts=[
                                ('This is your', colors.white),
                                (' shed.', colors.yellow_light)
                            ],
                            font=fonts.wacky_pixels,
                            size='small',
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
                    pos=(682, 232),
                    pos_anchor=posanchors.midbottom,
                ),
                Module_AllowInput(
                    allow_draw_card=2,
                    tutorial_state=self,
                    auto_advance=True
                ),
                Module_Arrow(
                    pos=(682, 302)
                ),
                1000,
                Module_ClickToContinue(tween_list=self.tween_list, tutorial_state=self)
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
                1000,
                Module_ClickToContinue(tween_list=self.tween_list, tutorial_state=self)
            ],
            [
                lambda: setattr(self, 'show_day_title_in_tutorial', True),
                lambda: setattr(self, 'transitioning', True),
                self.day_title_tween_chain,
            ]
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
        # Developer mode: skip tutorial step with ] key
        if debug.debug_developer_mode:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHTBRACKET:
                    self._skip_to_next_step()
                    return
        
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
        
        # Update all visible modules
        for module in self.visible_modules:
            module.update(dt, events)
    
    def _skip_to_next_step(self):
        """Execute all remaining functions in current step, then advance to next step"""
        if not hasattr(self, 'module_queue'):
            self.current_step += 1
            return
        
        # Execute all remaining functions in the current step
        for i in range(self.current_queue_index, len(self.module_queue)):
            item_type, item_value = self.module_queue[i]
            if item_type == 'function':
                item_value()
        
        # Advance to next step
        self.current_step += 1
        print(f"Skipped to tutorial step {self.current_step}")
    
    def _get_active_allow_input_module(self):
        """Get the currently active Module_AllowInput if one exists, or return default blocking module"""
        # If current step is out of bounds, allow all inputs (tutorial finished)
        if self.current_step >= len(self.tutorial_steps):
            return None
        
        if hasattr(self, 'visible_modules'):
            for module in self.visible_modules:
                if isinstance(module, Module_AllowInput):
                    return module
        
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
