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
                            text="To collect fruits, you need to connect-",
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
                    fade_duration=0
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
                    auto_advance=True,
                    tutorial_state=self
                ),
            ],
            [
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
                    auto_advance=True,
                    tutorial_state=self
                ),
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
                            text="Remember, tomorrow you need to collect more-",
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
                    auto_advance=True,
                    tutorial_state=self
                ),
            ],
            [
                Module_Textbox(
                    content=[
                        utils.get_text(
                            text='Press right click or spacebar one more time.',
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
                    auto_advance=True,
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
                            text='but for this tutorial, we will guide you through it.',
                            font=fonts.wacky_pixels,
                            size='tiny',
                            color=colors.white
                        ),
                    ],
                    bg=False,
                ),
                Module_ClickToContinue(tutorial_state=self)
            ],
            #@note
            [

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
        # Process simulated input queue first
        simulating = False
        if self.simulated_input_queue:
            simulating = True
            
            # If timer hasn't started (is 0), execute action immediately
            if self.simulated_input_timer == 0:
                action = self.simulated_input_queue.pop(0)
                
                if action[0] == 'function':
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
                elif action[0] == 'left_click':
                    item, pos = action[1], action[2]
                    # Create and directly send a mouse click event to substates
                    if self.substate_stack:
                        # Temporarily disable transitioning to allow input
                        was_transitioning = self.transitioning
                        self.transitioning = False
                        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
                        self.substate_stack[-1].update(dt=dt, events=[click_event])
                        self.transitioning = was_transitioning
                elif action[0] == 'jump_step':
                    self.current_step = action[1]
                    self.simulated_input_timer = 0  # Reset for next use
                    return  # Don't wait after jumping
                
                # Start delay timer after executing action
                self.simulated_input_timer = 0.001  # Small non-zero value to indicate delay started
            
            # Wait for delay after action
            self.simulated_input_timer += dt * 1000
            if self.simulated_input_timer >= self.simulated_input_delay:
                self.simulated_input_timer = 0  # Reset for next action
        
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
        
        # Queue functions and inputs from current step
        step_data = self.tutorial_steps[self.current_step]
        for item in step_data:
            if callable(item) and item != self.day_title_tween_chain:
                # Skip day_title_tween_chain to prevent it from playing again
                self.simulated_input_queue.append(('function', item))
            elif hasattr(item, '__class__') and item.__class__.__name__ == 'Module_AllowInput':
                # Queue draw card inputs
                if item.allow_draw_card > 0:
                    for _ in range(item.allow_draw_card):
                        self.simulated_input_queue.append(('draw_card', item))
                        print(f"  Queued draw_card input")
                # Queue left click input
                if item.allow_left_click_rect:
                    x, y, width, height = item.allow_left_click_rect
                    center_x = x + width // 2
                    center_y = y + height // 2
                    self.simulated_input_queue.append(('left_click', item, (center_x, center_y)))
                    print(f"  Queued left_click at ({center_x}, {center_y})")
        
        # Queue jump to next step
        self.simulated_input_queue.append(('jump_step', self.current_step + 1))
        self.simulated_input_timer = 0
        print(f"Queued {len(self.simulated_input_queue)} actions for step {self.current_step}, will advance to {self.current_step + 1}")
    
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
