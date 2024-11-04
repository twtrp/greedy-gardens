from src.library.essentials import *
from src.template.BaseState import BaseState

class Menu_PlayState(BaseState):
    def __init__(self, parent, stack):
        BaseState.__init__(self, parent, stack)

        text_props = {'font': fonts.lf2, 'size': 'medium'}
        text_deco_distance = utils.get_font_deco_distance(font=text_props['font'], size=text_props['size'])
        text = utils.get_text(text='Back', font=text_props['font'], size=text_props['size'], color=colors.white)
        text = utils.effect_long_shadow(surface=text,
                                        direction='bottom',
                                        distance=text_deco_distance,
                                        color=utils.color_darken(color=colors.white, factor=0.5))
        self.back_text = utils.effect_outline(surface=text, distance=text_deco_distance, color=colors.mono_50)
        self.back_rect = text.get_rect(center=(self.parent.parent.canvas_width / 2, self.parent.parent.canvas_height / 2))

    #Main methods

    def update(self, dt, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if self.back_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.exit_state()

    def render(self, canvas):
        utils.blit(dest=canvas, source=self.back_text, pos=self.back_rect.center, pos_anchor='center')
