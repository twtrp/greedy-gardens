from src.library.essentials import *


class BaseTutorialModule:    
    def __init__(self, fade_duration: int = 300):
        # Fade-in animation
        self.fade_duration = fade_duration  # Duration in milliseconds
        self.fade_timer = 0  # Current time in milliseconds
        self.alpha = 0  # Start fully transparent
        self.is_fading = True

    def _update_inject(self, dt, events):
        """Override this in child classes for custom update logic"""
        pass
    
    def update(self, dt, events):
        """Update fade-in animation. Child classes should override _render_inject instead."""
        self._update_inject(dt, events)
        if self.is_fading:
            self.fade_timer += dt * 1000  # Convert dt to milliseconds
            if self.fade_timer >= self.fade_duration:
                self.alpha = 255
                self.is_fading = False
            else:
                # Linear fade from 0 to 255
                self.alpha = int((self.fade_timer / self.fade_duration) * 255)
    
    def _render_inject(self, canvas):
        """Override this in child classes to create self.surface, self.pos, and self.pos_anchor"""
        pass
    
    def render(self, canvas):
        """Render with fade-in applied. Child classes should override _render_inject instead."""
        # Let child class prepare the surface
        self._render_inject(canvas)
        
        # Apply fade-in alpha and blit
        if hasattr(self, 'surface') and self.surface:
            self.surface.set_alpha(self.alpha)
            utils.blit(
                dest=canvas,
                source=self.surface,
                pos=self.pos,
                pos_anchor=self.pos_anchor
            )
