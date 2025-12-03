from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule

class Module_Textbox(BaseTutorialModule):
    def __init__(
            self,
            content: list[pygame.Surface],
            bg: bool = True,
            bg_opacity: int = 175,
            align: str = 'center',
            pos: tuple = (constants.canvas_width // 2, constants.canvas_height // 2),
            pos_anchor: str = posanchors.center,
            fade_duration: int = 300,
        ):
        super().__init__(fade_duration=fade_duration)
        
        if align not in ['left', 'right', 'center']:
            raise ValueError(f"align must be 'left', 'right', or 'center', got '{align}'")
        
        self.content = content
        self.bg = bg
        self.bg_opacity = bg_opacity
        self.align = align
        self.pos = pos
        self.pos_anchor = pos_anchor

        self.padding_x = 20
        self.padding_y = 10
        self.line_spacing = 0

        self.surface = pygame.Surface(
            size=(
                max([line.get_width() for line in self.content]) + (self.padding_x) * 2,
                sum([line.get_height() for line in self.content]) + (self.padding_y) * 2 + (self.line_spacing * (len(self.content) - 1))
            ),
            flags=pygame.SRCALPHA
        )
        if self.bg:
            utils.draw_rect(
                dest=self.surface,
                size=(self.surface.get_width(), self.surface.get_height()),
                pos=(0, 0),
                pos_anchor=posanchors.topleft,
                color=(*colors.mono_50, self.bg_opacity),
                inner_border_width=3
            )
        current_y = self.padding_y
        for line in self.content:
            if self.align == 'center':
                utils.blit(
                    dest=self.surface,
                    source=line,
                    pos=(self.surface.get_width() // 2, current_y),
                    pos_anchor=posanchors.midtop
                )
            elif self.align == 'left':
                utils.blit(
                    dest=self.surface,
                    source=line,
                    pos=(self.padding_x if self.bg else 0, current_y),
                    pos_anchor=posanchors.topleft
                )
            elif self.align == 'right':
                utils.blit(
                    dest=self.surface,
                    source=line,
                    pos=(self.surface.get_width() - (self.padding_x if self.bg else 0), current_y),
                    pos_anchor=posanchors.topright
                )
            current_y += line.get_height() + self.line_spacing
        

