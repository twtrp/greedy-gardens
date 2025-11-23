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
import tween
import math

class Play_TutorialState(PlayState):
    def __init__(self, game, parent, stack, seed):
        PlayState.__init__(self, game, parent, stack, seed)
    
    #Classes
    class Module_Text:
        def __init__(
                self,
                content: list,
                align: str = 'center',
                textbox: bool = True
            ):
            if align not in ['left', 'right', 'center']:
                raise ValueError(f"align must be 'left', 'right', or 'center', got '{align}'")
            self.content = content
            self.align = align
            self.textbox = textbox


    #Main methods

    def load_assets(self):
        PlayState.load_assets(self)
        
        self.tutorial_step = 0  # Track which tutorial step we're on
        self.step_delay_timer = 0  # Timer to manage delays between steps
        self.step_delay = 0.5  # Delay in seconds between steps
        self.show_day_title_in_tutorial = False  # Control day title animation

        self.tutorial_steps = {
            0: [
                self.Module_Text(
                    content=[
                        utils.get_text(
                            text="Welcome to the farm!.",
                            font=fonts.wacky_pixels,
                            size='small',
                            color=colors.white
                        ),
                        utils.get_text(
                            text="You will spend 4 days here collecting fruits.",
                            font=fonts.wacky_pixels,
                            size='small',
                            color=colors.white
                        )
                    ]
                )
            ]
        }

    def update(self, dt, events):
        PlayState.update(self, dt, events)

        if self.ready:
            if not self.in_tutorial:
                for event in events:
                    pass

    def render(self, canvas):
        PlayState.render(self, canvas)

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
