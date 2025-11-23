from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule
import tween

class Module_ClickToContinue(BaseTutorialModule):
    def __init__(
        self,
        text: str = "< Click anywhere to continue >",
        pos: tuple = (constants.canvas_width/2, 695),
        pos_anchor: str = posanchors.center,
        fade_duration: int = 0,
        tween_list: list = None,
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
        self.tween_list = tween_list
        self.tutorial_state = tutorial_state
        
        # Scale animation
        self.scale = 1.25
        self.tween_started = False
    
    def _update_inject(self, dt, events):
        if not self.tween_started and self.tween_list is not None:
            self.tween_started = True
            self.tween_list.append(tween.to(
                container=self,
                key='scale',
                end_value=1.0,
                time=0.5,
                ease_type=tweencurves.easeOutQuart
            ))
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.tutorial_state is not None:
                    self.tutorial_state.current_step += 1
                    print(self.tutorial_state.current_step)

    def _render_inject(self, canvas):
        # Apply scale to content
        scaled_content = pygame.transform.scale_by(surface=self.content, factor=self.scale)
        self.surface = scaled_content
    