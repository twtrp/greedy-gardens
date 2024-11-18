from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_NextDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        print("Next Day")

        # Update score if fail to make more than yesterday
        if 5> self.parent.current_day > 1:
            if getattr(self.parent, f'final_day{self.parent.current_day}_score') <= getattr(self.parent, f'final_day{self.parent.current_day - 1}_score'):
                setattr(self.parent, f'final_day{self.parent.current_day}_score', getattr(self.parent, f'final_day{self.parent.current_day}_score') if getattr(self.parent, f'final_day{self.parent.current_day}_score') < 0 else 0)

        # update parent value
        self.parent.strikes = 0
        self.parent.current_day += 1
        print(self.parent.current_day)
        # state
        self.fruit_not_drawn = True
        self.card_drawn_image = None
        
        self.parent.endDayState = False
        self.parent.set_start_state=False

        self.parent.left_box_none_text = utils.get_text(text=f'Draw {self.parent.current_day} fruit', font=fonts.lf2, size='tiny', color=colors.white)
        self.card_drawn_text = utils.get_text(text=f'Day {self.parent.current_day + 1} Fruit', font=fonts.lf2, size='large', color=colors.white)

        utils.sound_play(sound=sfx.chicken_crowing, volume=self.game.sfx_volume)

    def update(self, dt, events):
        if self.parent.current_day>=5:
            self.exit_state()
        for index in self.parent.game_board.connected_indices:
            cell = self.parent.game_board.board[index]
            if getattr(self.parent, f'day{self.parent.current_day - 1}_fruit') in cell.fruit:
                cell.fruit = [None if item == getattr(self.parent, f'day{self.parent.current_day - 1}_fruit') else item for item in cell.fruit]

        # clear free(temp) path
        for i, rect in enumerate(self.parent.grid_hitboxes):
            if self.parent.game_board.board[i].temp:
                self.parent.game_board.board[i].north = False
                self.parent.game_board.board[i].west = False
                self.parent.game_board.board[i].east = False
                self.parent.game_board.board[i].south = False
                self.parent.game_board.board[i].temp = False
                self.parent.game_board.board[i].path = False

        # draw fruit for next next day
        if self.parent.current_day < self.parent.day:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.fruit_not_drawn:
                            self.card_drawn = self.parent.deck_fruit.draw_card()
                            if self.card_drawn:
                                setattr(self.parent, f"day{self.parent.current_day + 1}_fruit", self.card_drawn.card_name)
                                self.parent.drawn_cards_fruit.append(self.card_drawn)
                                self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                                self.fruit_not_drawn = False
                        else:
                            self.parent.drawing = True
                            self.parent.set_start_state=True
                            self.exit_state()
        elif self.parent.current_day == self.parent.day:
            self.parent.drawing = True
            self.parent.set_start_state=True
            self.exit_state()
        

    def render(self, canvas):
        if self.card_drawn_image:
            utils.blit(dest=canvas, source=self.card_drawn_text, pos=(constants.canvas_width/2, constants.canvas_height/2 - 190), pos_anchor='center')
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=2)
            scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
        
        # Should have text showing Days number