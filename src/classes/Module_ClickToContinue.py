from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule

class Module_ClickToContinue(BaseTutorialModule):
    def __init__(
        self,
        text: str = "< Click anywhere to continue >",
        pos: tuple = (constants.canvas_width/2, 695),
        pos_anchor: str = posanchors.center,
        fade_duration: int = 0,
        tutorial_state = None,
    ):
        super().__init__(fade_duration=fade_duration)
        
        self.content = utils.get_text(
            text=text,
            font=fonts.lf2,
            size='small',
            color=colors.white
        )
        self.pos = pos
        self.pos_anchor = pos_anchor
        self.tutorial_state = tutorial_state
    
    def _update_inject(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Only left click
                if self.tutorial_state is not None and not self.tutorial_state.paused:
                    self.tutorial_state.current_step += 1

    def _render_inject(self, canvas):
        self.surface = self.content
    