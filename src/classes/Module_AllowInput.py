from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule


class Module_AllowInput(BaseTutorialModule):
    def __init__(
        self,
        allow_draw_card: int = 0,
        allow_left_click_rect: tuple = None,
        allow_hover_rect: tuple = None,
        allow_scroll_down: int = 0,
        allow_scroll_up: int = 0,
        auto_advance: bool = True,
        tutorial_state = None,
    ):
        """
        Initialize input allowlist module
        
        allow_draw_card: Number of times drawing card is allowed via spacebar/right-click (0 = blocked, -1 = unlimited)
        allow_left_click_rect: Rectangle area where left click is allowed (x1, y1, x2, y2)
        allow_hover_rect: Rectangle area where hovering is allowed (x1, y1, x2, y2)
        allow_scroll_down: Number of times scrolling down is allowed via 's' or down arrow (0 = blocked, -1 = unlimited)
        allow_scroll_up: Number of times scrolling up is allowed via 'w' or up arrow (0 = blocked, -1 = unlimited)
        auto_advance: If True, automatically advance to next step when all allowed inputs are executed
        tutorial_state: Reference to Tutorial_PlayState for auto-advancing
        """
        super().__init__(fade_duration=0)

        self.surface = None
        
        self.allow_draw_card = allow_draw_card
        self.allow_left_click_rect = allow_left_click_rect
        self.allow_hover_rect = allow_hover_rect
        self.allow_scroll_down = allow_scroll_down
        self.allow_scroll_up = allow_scroll_up
        self.tutorial_state = tutorial_state
        self.auto_advance = auto_advance
        
        # Track usage counts
        self.draw_card_count = 0
        self.left_click_count = 0
        self.hover_count = 0
        self.hover_triggered = False
        self.scroll_down_count = 0
        self.scroll_up_count = 0
        
        # For tracking multiple rects (used when modules are merged)
        self.clicked_rects = set()  # Indices of clicked rects
        self.hovered_rects = set()  # Indices of hovered rects
        
        # Calculate total required inputs (skip unlimited inputs)
        self.total_required = 0
        if allow_draw_card > 0:
            self.total_required += allow_draw_card
        if allow_left_click_rect is not None:
            self.total_required += 1  # One left click required
        if allow_hover_rect is not None:
            self.total_required += 1  # One hover required
        if allow_scroll_down > 0:
            self.total_required += allow_scroll_down
        if allow_scroll_up > 0:
            self.total_required += allow_scroll_up
    
    def is_draw_card_allowed(self) -> bool:
        """Check if drawing card input is allowed (spacebar or right click)"""
        if self.allow_draw_card == -1:
            return True
        return self.draw_card_count < self.allow_draw_card
    
    def is_left_click_allowed(self, pos: tuple) -> bool:
        """Check if left click at position is allowed"""
        if self.allow_left_click_rect is None:
            return False
        
        # Support multiple rects (for merged modules)
        rects_to_check = getattr(self, 'allow_left_click_rects', None) or [self.allow_left_click_rect]
        
        for idx, rect in enumerate(rects_to_check):
            # Convert canvas rect to screen coordinates to match mouse position
            if self.tutorial_state is not None:
                screen_x1, screen_y1, screen_x2, screen_y2 = utils.canvas_rect_to_screen(
                    rect, 
                    self.tutorial_state.game
                )
            else:
                # No scaling available, use coords as-is
                screen_x1, screen_y1, screen_x2, screen_y2 = rect
            
            mouse_x, mouse_y = pos
            if (screen_x1 <= mouse_x <= screen_x2 and screen_y1 <= mouse_y <= screen_y2):
                # Store the index of the rect that was clicked
                self._last_clicked_rect_idx = idx
                return True
        
        return False
    
    def is_hover_allowed(self, pos: tuple) -> bool:
        """Check if hovering at position is allowed (for magic fruit card preview)"""
        if self.allow_hover_rect is None:
            return False
        
        # Support multiple rects (for merged modules)
        rects_to_check = getattr(self, 'allow_hover_rects', None) or [self.allow_hover_rect]
        
        for idx, rect in enumerate(rects_to_check):
            # Convert canvas rect to screen coordinates to match mouse position
            if self.tutorial_state is not None:
                screen_x1, screen_y1, screen_x2, screen_y2 = utils.canvas_rect_to_screen(
                    rect, 
                    self.tutorial_state.game
                )
            else:
                # No scaling available, use coords as-is
                screen_x1, screen_y1, screen_x2, screen_y2 = rect
            
            mouse_x, mouse_y = pos
            if (screen_x1 <= mouse_x <= screen_x2 and screen_y1 <= mouse_y <= screen_y2):
                # Store the index of the rect that was hovered
                self._last_hovered_rect_idx = idx
                return True
        
        return False
    
    def consume_draw_card(self):
        """Consume one draw card use"""
        if self.allow_draw_card != -1:
            self.draw_card_count += 1
            self._check_auto_advance()
    
    def consume_left_click(self):
        """Consume one left click use"""
        # For multiple rects, track each one separately
        if hasattr(self, 'allow_left_click_rects') and hasattr(self, '_last_clicked_rect_idx'):
            idx = self._last_clicked_rect_idx
            # If advance flags are present, only count clicks for rects that contribute to advancement
            if hasattr(self, 'allow_left_click_rects_adv_flags'):
                if idx not in self.clicked_rects and self.allow_left_click_rects_adv_flags[idx]:
                    self.clicked_rects.add(idx)
                    self.left_click_count += 1
                    self._check_auto_advance()
            else:
                if idx not in self.clicked_rects:
                    self.clicked_rects.add(idx)
                    self.left_click_count += 1
                    self._check_auto_advance()
        else:
            # Single rect - old behavior
            self.left_click_count += 1
            self._check_auto_advance()
    
    def consume_hover(self):
        """Consume one hover use (only counts once when hover is first detected)"""
        # For multiple rects, track each one separately
        if hasattr(self, 'allow_hover_rects') and hasattr(self, '_last_hovered_rect_idx'):
            idx = self._last_hovered_rect_idx
            # Respect per-rect advance flags if present
            if hasattr(self, 'allow_hover_rects_adv_flags'):
                if idx not in self.hovered_rects and self.allow_hover_rects_adv_flags[idx]:
                    self.hovered_rects.add(idx)
                    self.hover_count += 1
                    self._check_auto_advance()
            else:
                if idx not in self.hovered_rects:
                    self.hovered_rects.add(idx)
                    self.hover_count += 1
                    self._check_auto_advance()
        else:
            # Single rect - old behavior
            if not self.hover_triggered:
                self.hover_triggered = True
                self.hover_count += 1
                self._check_auto_advance()
    
    def is_scroll_down_allowed(self) -> bool:
        """Check if scrolling down is allowed (s key or down arrow)"""
        if self.allow_scroll_down == -1:
            return True
        return self.scroll_down_count < self.allow_scroll_down
    
    def consume_scroll_down(self):
        """Consume one scroll down use"""
        if self.allow_scroll_down != -1:
            self.scroll_down_count += 1
            self._check_auto_advance()
    
    def is_scroll_up_allowed(self) -> bool:
        """Check if scrolling up is allowed (w key or up arrow)"""
        if self.allow_scroll_up == -1:
            return True
        return self.scroll_up_count < self.allow_scroll_up
    
    def consume_scroll_up(self):
        """Consume one scroll up use"""
        if self.allow_scroll_up != -1:
            self.scroll_up_count += 1
            self._check_auto_advance()
    
    def _check_auto_advance(self):
        """Check if all required inputs have been executed and auto-advance if enabled"""
        if not self.auto_advance or self.tutorial_state is None:
            return
        
        # Only auto-advance if we have limited inputs (not unlimited)
        if self.total_required > 0:
            total_executed = self.draw_card_count + self.left_click_count + self.hover_count + self.scroll_down_count + self.scroll_up_count
            if total_executed >= self.total_required:
                self.tutorial_state.current_step += 1
