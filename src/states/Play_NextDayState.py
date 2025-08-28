from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_NextDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # print("Next Day")
 
        # update parent value
        self.parent.strikes = 0
        self.parent.current_day += 1
        # print(self.parent.current_day)
        # state
        self.fruit_not_drawn = True
        self.card_drawn_image = None
        
        self.parent.endDayState = False
        self.parent.set_start_state=False

        self.parent.left_box_none_text = utils.get_text(text=f'Draw day {self.parent.current_day + 1} fruit', font=fonts.lf2, size='tiny', color=colors.white)
        self.card_drawn_text = utils.get_text(text=f'Day {self.parent.current_day + 1} Fruit', font=fonts.lf2, size='large', color=colors.white)

        if self.parent.current_day < 5:
            utils.sound_play(sound=sfx.chicken_crowing, volume=self.game.sfx_volume)
            self.parent.day_title_tween_chain()

    def update(self, dt, events):
        if self.parent.current_day>=5:
            for index in self.parent.game_board.connected_indices:
                cell = self.parent.game_board.board[index]
                if getattr(self.parent, f'day{self.parent.current_day - 1}_fruit') in cell.fruit:
                    cell.fruit = [None if item == getattr(self.parent, f'day{self.parent.current_day - 1}_fruit') else item for item in cell.fruit]
                if self.parent.seasonal_fruit in cell.fruit:
                    cell.fruit = [None if item == self.parent.seasonal_fruit else item for item in cell.fruit]
            self.exit_state()
        else:
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
                    if event.key == pygame.K_SPACE and self.parent.shown_day_title:
                        if self.fruit_not_drawn:
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                            self.card_drawn_image_props = {
                                'x': 1080,
                                'y': 130,
                                'scale': 1,
                            }
                            def on_complete():
                                self.parent.tween_list.clear()
                            utils.multitween(
                                tween_list=self.parent.tween_list,
                                container=self.card_drawn_image_props,
                                keys=['x', 'y', 'scale'],
                                end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                                time=0.5,
                                ease_type=tweencurves.easeOutQuint,
                                on_complete=on_complete
                            )
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3 and self.parent.shown_day_title:  # Right click
                        if self.fruit_not_drawn:
                            utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                            self.card_drawn_image_props = {
                                'x': 1080,
                                'y': 130,
                                'scale': 1,
                            }
                            def on_complete():
                                self.parent.tween_list.clear()
                            utils.multitween(
                                tween_list=self.parent.tween_list,
                                container=self.card_drawn_image_props,
                                keys=['x', 'y', 'scale'],
                                end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                                time=0.5,
                                ease_type=tweencurves.easeOutQuint,
                                on_complete=on_complete
                            )
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
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=self.card_drawn_image_props['scale'])
            # scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(self.card_drawn_image_props['x'], self.card_drawn_image_props['y']), pos_anchor='center')

        # Should have text showing Days number