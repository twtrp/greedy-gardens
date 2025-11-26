from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule


class Module_AllowInput(BaseTutorialModule):
    def __init__(
        self,
        allow_draw_card: int = 0,
        allow_left_click_rect: tuple = None,
        auto_advance: bool = True,
        tutorial_state = None,
    ):
        """
        Initialize input allowlist module
        
        allow_draw_card: Number of times drawing card is allowed via spacebar/right-click (0 = blocked, -1 = unlimited)
        allow_left_click_rect: Rectangle area where left click is allowed (x, y, width, height)
        auto_advance: If True, automatically advance to next step when all allowed inputs are executed
        tutorial_state: Reference to Tutorial_PlayState for auto-advancing
        """
        super().__init__(fade_duration=0)

        self.surface = None
        
        self.allow_draw_card = allow_draw_card
        self.allow_left_click_rect = allow_left_click_rect
        self.tutorial_state = tutorial_state
        self.auto_advance = auto_advance
        
        # Track usage counts
        self.draw_card_count = 0
        self.left_click_count = 0
        
        # Calculate total required inputs (skip unlimited inputs)
        self.total_required = 0
        if allow_draw_card > 0:
            self.total_required += allow_draw_card
    
    def is_draw_card_allowed(self) -> bool:
        """Check if drawing card input is allowed (spacebar or right click)"""
        if self.allow_draw_card == -1:
            return True
        return self.draw_card_count < self.allow_draw_card
    
    def is_left_click_allowed(self, pos: tuple) -> bool:
        """Check if left click at position is allowed"""
        if self.allow_left_click_rect is None:
            return False
        
        x, y, width, height = self.allow_left_click_rect
        mouse_x, mouse_y = pos
        
        return (x <= mouse_x <= x + width and y <= mouse_y <= y + height)
    
    def consume_draw_card(self):
        """Consume one draw card use"""
        if self.allow_draw_card != -1:
            self.draw_card_count += 1
            self._check_auto_advance()
    
    def consume_left_click(self):
        """Consume one left click use"""
        self.left_click_count += 1
        self._check_auto_advance()
    
    def _check_auto_advance(self):
        """Check if all required inputs have been executed and auto-advance if enabled"""
        if not self.auto_advance or self.tutorial_state is None:
            return
        
        # Only auto-advance if we have limited inputs (not unlimited)
        if self.total_required > 0:
            total_executed = self.draw_card_count + self.left_click_count
            if total_executed >= self.total_required:
                self.tutorial_state.current_step += 1
