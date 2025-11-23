from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_EndDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        
        # Stop the rightclick hint animation loop
        self.parent.tween_list.clear()
        
        # Animation state
        self.fruits_animating = True
        self.collected_fruit_animations = []
        # Track which fruits to hide during animation: (cell_index, fruit_slot_position)
        self.parent.hidden_fruits_during_animation = set()
        
        # Get current day's info
        self.current_day = self.parent.current_day
        if self.current_day == 1:
            self.current_score = self.parent.final_day1_score
            self.current_fruit = self.parent.day1_fruit
        elif self.current_day == 2:
            self.current_score = self.parent.final_day2_score
            self.current_fruit = self.parent.day2_fruit
        elif self.current_day == 3:
            self.current_score = self.parent.final_day3_score
            self.current_fruit = self.parent.day3_fruit
        elif self.current_day == 4:
            self.current_score = self.parent.final_day4_score
            self.current_fruit = self.parent.day4_fruit

        # Update score if fail to make more than yesterday
        if self.parent.current_day > 1:
            self.current_score = getattr(self.parent, f'final_day{self.parent.current_day}_score')
            previous_score = getattr(self.parent, f'final_day{self.parent.current_day - 1}_score')

            # If today's score is not higher than yesterday's
            if self.current_score <= previous_score or self.current_score < 0:
                # Replace today's score with 0
                new_score = 0
                setattr(self.parent, f'final_day{self.parent.current_day}_score', new_score)
                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                # Set penalty flag to prevent score recalculation
                setattr(self.parent, f'day{self.parent.current_day}_penalty_applied', True)

        else: 
            if self.current_score < 0:
                new_score = 0
                setattr(self.parent, f'final_day{self.parent.current_day}_score', new_score)
                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                setattr(self.parent, f'day{self.parent.current_day}_penalty_applied', True)
            
        self.button_list = []

        # Initialize farmhouse scale for animation on parent
        self.parent.farmhouse_scale = 1.0
        
        # CRITICAL: Ensure hidden_fruits is completely clear before animation starts
        # This prevents any stale data from affecting score calculations
        self.parent.hidden_fruits_during_animation.clear()

        # Start fruit collection animation (before setting is_choosing)
        # Keep is_choosing False during animation, set to True when animation completes
        self.parent.is_choosing = False
        self._start_fruit_collection_animation()
        
        # Note: If no fruits to animate, _start_fruit_collection_animation sets is_choosing to True

        self.load_assets()
    
    def _start_fruit_collection_animation(self):
        """Collect fruits from board and animate them flying to the farmhouse."""
        self.collected_fruit_animations = []
        
        # Get today's fruit
        today_fruit = getattr(self.parent, f'day{self.parent.current_day}_fruit')
        
        # Calculate farmhouse center position using the actual home_index from game_board
        # Home sprite is rendered at: grid_start + (index * cell_size) + offset(17, 16) as topleft
        # Home sprite dimensions: get actual center by adding half the sprite size
        farmhouse_index = self.parent.game_board.home_index
        home_sprite_center_x = self.parent.home.get_width() // 2
        home_sprite_center_y = self.parent.home.get_height() // 2
        farmhouse_x = self.parent.grid_start_x + ((farmhouse_index % 8) * self.parent.cell_size) + 17 + home_sprite_center_x
        farmhouse_y = self.parent.grid_start_y + ((farmhouse_index // 8) * self.parent.cell_size) + 16 + home_sprite_center_y
        
        # Position offsets for the 4 fruit slots within a cell
        fruit_offsets = [
            (0, 0),    # pos 0: top-left
            (48, 0),   # pos 1: top-right
            (0, 48),   # pos 2: bottom-left
            (48, 48)   # pos 3: bottom-right
        ]
        
        # Collect all fruits that need to be collected
        fruits_to_collect = []
        for index in self.parent.game_board.connected_indices:
            cell = self.parent.game_board.board[index]
            
            # Check each fruit slot in this cell
            if cell.fruit:
                for pos, fruit in enumerate(cell.fruit):
                    if fruit == today_fruit:
                        # Calculate exact fruit position based on slot
                        offset_x, offset_y = fruit_offsets[pos]
                        fruit_x = self.parent.grid_start_x + ((index % 8) * self.parent.cell_size) + offset_x + 16
                        fruit_y = self.parent.grid_start_y + ((index // 8) * self.parent.cell_size) + offset_y + 16
                        
                        fruits_to_collect.append({
                            'index': index,
                            'pos': pos,
                            'x': fruit_x,
                            'y': fruit_y,
                            'sprite': self.parent.big_fruit_sprites[today_fruit]
                        })
        
        # If no fruits to animate, show screen immediately
        if len(fruits_to_collect) == 0:
            self.fruits_animating = False
            self.parent.is_choosing = True  # Show dim mask immediately
            return
        
        # Store fruits queue and collection state
        self.fruits_to_collect = fruits_to_collect
        self.current_fruit_index = 0
        self.collection_timer = 0.0
        self.fruits_animating = True
        
        # Calculate delay between fruits with smoother exponential curve
        # Starts at 0.3s, decreases to ~0.02s at 16 fruits
        total_fruits = len(fruits_to_collect)
        if total_fruits == 1:
            self.fruit_delays = [0.3]
        else:
            max_delay = 0.4
            min_delay = 0.05
            self.fruit_delays = []
            for i in range(total_fruits):
                # Quartic curve (original formula)
                progress = i / (total_fruits - 1)
                eased_progress = 1 - (1 - progress) ** 4
                delay = max_delay - (eased_progress * (max_delay - min_delay))
                self.fruit_delays.append(delay)
        
        # Start collecting the first fruit immediately
        self._collect_next_fruit()
    
    def _collect_next_fruit(self):
        """Collect the next fruit in the queue."""
        if self.current_fruit_index >= len(self.fruits_to_collect):
            return
        
        fruit_data = self.fruits_to_collect[self.current_fruit_index]
        
        # Calculate farmhouse position
        farmhouse_index = self.parent.game_board.home_index
        home_sprite_center_x = self.parent.home.get_width() // 2
        home_sprite_center_y = self.parent.home.get_height() // 2
        farmhouse_x = self.parent.grid_start_x + ((farmhouse_index % 8) * self.parent.cell_size) + 17 + home_sprite_center_x
        farmhouse_y = self.parent.grid_start_y + ((farmhouse_index // 8) * self.parent.cell_size) + 16 + home_sprite_center_y
        
        # Create animation data
        animation_data = {
            'sprite': fruit_data['sprite'],
            'x': fruit_data['x'],
            'y': fruit_data['y'],
            'alpha': 255,
            'scale': 1.0
        }
        
        self.collected_fruit_animations.append(animation_data)
        
        # Hide this fruit on the board during animation (but keep in array for scoring)
        self.parent.hidden_fruits_during_animation.add((fruit_data['index'], fruit_data['pos']))
        
        # Calculate pitch for sound
        # Pitch increases as we collect more fruits, scaled by how many fruits there are
        # Fewer fruits = smaller pitch range, more fruits = larger pitch range
        total_fruits = len(self.fruits_to_collect)
        if total_fruits > 1:
            pitch_progress = self.current_fruit_index / (total_fruits - 1)
            # Scale pitch range more gradually: 2 fruits = 0.15 range, increases by 0.06 per fruit, max 1.2 at 20+ fruits
            pitch_range = min(0.15 + (total_fruits - 2) * 0.06, 1.2)
            pitch = 1.0 + (pitch_progress * pitch_range)
        else:
            pitch = 1.0
        
        # Play sound when fruit starts animation
        utils.sound_play(sound=sfx.fruit_collect, volume=self.game.sfx_volume, pitch=pitch)
        
        # Create tween animation for this fruit
        tween_duration = 0.6
        self.parent.tween_list.append(
            tween.to(
                container=animation_data,
                key='x',
                end_value=farmhouse_x,
                time=tween_duration,
                ease_type=tweencurves.easeInCubic
            )
        )
        # Animate farmhouse scale when fruit arrives
        # Scale up to 1.2 quickly, then decay back to 1.0
        def on_fruit_arrive():
            # Play sound when fruit enters house
            utils.sound_play(sound=sfx.fruit_collect_end, volume=self.game.sfx_volume, pitch=pitch)
            
            # Scale up to 1.2 (more visible)
            self.parent.farmhouse_scale = 1.2
            # Then decay back to 1.0
            self.parent.tween_list.append(
                tween.to(
                    container=self.parent,
                    key='farmhouse_scale',
                    end_value=1.0,
                    time=0.3,
                    ease_type=tweencurves.easeOutQuad
                )
            )
        
        # Add Y position tween with callback attached BEFORE adding to list
        y_tween = tween.to(
            container=animation_data,
            key='y',
            end_value=farmhouse_y,
            time=tween_duration,
            ease_type=tweencurves.easeInCubic
        )
        y_tween.on_complete(on_fruit_arrive)
        self.parent.tween_list.append(y_tween)
        
        self.parent.tween_list.append(
            tween.to(
                container=animation_data,
                key='alpha',
                end_value=0,
                time=tween_duration * 0.3,
                delay=tween_duration * 0.7,
                ease_type=tweencurves.easeInExpo
            )
        )
        
        self.current_fruit_index += 1
            
    def load_assets(self):
        # Text
        self.result_title = utils.get_text(text=f'Day {self.current_day} Result', font=fonts.wacky_pixels, size='large', color=colors.white)
        self.vs_title = utils.get_text(text=f'VS', font=fonts.wacky_pixels, size='smaller', color=colors.mono_205)
        self.pass_title = utils.get_text(text=f'Pass', font=fonts.wacky_pixels, size='medium', color=colors.green_light)
        self.fail_title = utils.get_text(text=f'Fail', font=fonts.wacky_pixels, size='medium', color=colors.red_light)
        self.fail_description = utils.get_text(text=f'You failed to collect more than yesterday!', font=fonts.windows, size='smaller', color=colors.red_light)
        self.fail_description_2 = utils.get_text(text=f'Your score for the day was set to zero.', font=fonts.windows, size='smaller', color=colors.red_light)

        self.result_list = []
        if self.parent.current_day == 1:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        elif self.parent.current_day <= self.parent.day:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day - 1}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day - 1}_fruit'),
                                    })
            self.result_list.append({
                                    'text': str(self.current_score),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        self.result_surface_list = []
        for i, option in enumerate(self.result_list):
                text = utils.get_text(text=option['text'], font=fonts.wacky_pixels, size='medium', color=colors.white)
                fruit = self.parent.fruit_sprites[option['fruit']]
                scaled_fruit_image = pygame.transform.scale_by(surface=fruit, factor=3)
                glow_fruit_image = utils.effect_outline(surface=scaled_fruit_image, distance=3, color=colors.mono_50)
                if i == 0 and self.parent.current_day != 1:
                    glow_fruit_image = utils.effect_grayscale(surface=glow_fruit_image)
                self.result_surface_list.append({
                    'surface': text,
                    'surface_fruit': glow_fruit_image,
                })
        self.parent.endDayState = False
        
        self.button_list.append(Button(
            game=self.game,
            id='bg',
            width=constants.canvas_width,
            height=constants.canvas_height,
            pos=(0, 0),
            pos_anchor='topleft'
        ))
        self.continue_text = utils.get_text(text="Click anywhere to continue", font=fonts.lf2, size='small', color=colors.yellow_light)
        
    def update(self, dt, events):
        # Update animation timer for sequential collection
        if self.fruits_animating:
            # Check if we need to collect the next fruit
            if self.current_fruit_index < len(self.fruits_to_collect):
                self.collection_timer += dt
                current_delay = self.fruit_delays[self.current_fruit_index - 1] if self.current_fruit_index > 0 else 0
                
                if self.collection_timer >= current_delay:
                    self.collection_timer = 0.0
                    self._collect_next_fruit()
            
            # Check if all fruits have been collected and last animation is done
            # Last fruit needs 0.6s to complete its animation
            if self.current_fruit_index >= len(self.fruits_to_collect):
                self.collection_timer += dt
                if self.collection_timer >= 0.7:  # Wait for last fruit animation (0.6s) + small buffer
                    self.fruits_animating = False
                    self.collected_fruit_animations.clear()
                    # DON'T clear hidden_fruits here - keep fruits hidden during result screen
                    # They will be cleared when exiting this state or when Play_NextDayState removes them
                    # Now show the dim mask and end day screen
                    self.parent.is_choosing = True
        
        # Only allow clicking when animations are done
        if not self.fruits_animating:
            for button in self.button_list:
                button.update(dt=dt, events=events)
                if button.hovered:
                    if button.hover_cursor is not None:
                        self.cursor = button.hover_cursor
                if button.clicked:
                    if button.id == 'bg':
                        # print("exiting end day")
                        self.parent.endDayState = True
                        if self.parent.current_day >= 4:
                            self.parent.end_game=True
                        self.parent.is_choosing = False
                        # Restart the rightclick hint animation when returning to normal gameplay
                        if hasattr(self.parent, 'start_draw_card_hint_animation'):
                            # Reset draw hint animation state so it restarts cleanly at the minimum scale
                            try:
                                # Ensure any tweens that might modify the scale are cleared
                                if hasattr(self.parent, 'tween_list'):
                                    self.parent.tween_list.clear()

                                # If min/max exist, compute an animation time that yields the min amplitude
                                if hasattr(self.parent, 'draw_card_hint_scale_min') and hasattr(self.parent, 'draw_card_hint_scale_max') and hasattr(self.parent, 'draw_card_hint_animation_cycle_duration'):
                                    # For sine: min occurs at -1 -> phase = 3*pi/2 (or -pi/2). We'll set animation_time so cycle_progress yields -pi/2
                                    # cycle_progress = (t % duration) / duration -> sin(2*pi*cycle_progress) = -1 when cycle_progress = 3/4
                                    # So set animation_time to 3/4 * cycle_duration
                                    self.parent.draw_card_hint_animation_time = 0.75 * self.parent.draw_card_hint_animation_cycle_duration
                                    # Set the visible scale to the minimum explicitly to avoid any one-frame jump
                                    self.parent.draw_card_hint_scale = self.parent.draw_card_hint_scale_min
                                else:
                                    # Fallback: zero the animation timer and set scale to 1.0
                                    self.parent.draw_card_hint_animation_time = 0.0
                                    self.parent.draw_card_hint_scale = getattr(self.parent, 'draw_card_hint_scale', 1.0)
                            except Exception:
                                # If anything unexpected happens, fallback silently
                                pass
                            self.parent.start_draw_card_hint_animation()
                        # Clear the hidden fruits set now that we're moving to next day
                        self.parent.hidden_fruits_during_animation.clear()
                        self.exit_state()
 
    def render(self, canvas):
        # Render animating fruits on top of everything
        if self.fruits_animating:
            for fruit_data in self.collected_fruit_animations:
                # Apply alpha to the sprite
                if fruit_data['alpha'] > 0:
                    fruit_sprite = fruit_data['sprite'].copy()
                    fruit_sprite.set_alpha(int(fruit_data['alpha']))
                    
                    utils.blit(
                        dest=canvas,
                        source=fruit_sprite,
                        pos=(int(fruit_data['x']), int(fruit_data['y'])),
                        pos_anchor='center'
                    )
            # Don't show the end day screen while animating
            return
        
        # Title text
        utils.blit(dest=canvas, source=self.result_title, pos=(constants.canvas_width/2, constants.canvas_height/2 - 150), pos_anchor='center')
        if self.parent.current_day > 1:
            utils.blit(dest=canvas, source=self.vs_title, pos=(constants.canvas_width/2, constants.canvas_height/2 + 4), pos_anchor='center')
            if getattr(self.parent, f'final_day{self.parent.current_day}_score') <= getattr(self.parent, f'final_day{self.parent.current_day -1}_score'):
                utils.blit(dest=canvas, source=self.fail_title, pos=(constants.canvas_width/2, 515), pos_anchor='center')
                utils.blit(dest=canvas, source=self.fail_description, pos=(constants.canvas_width/2, 565), pos_anchor='center')
                utils.blit(dest=canvas, source=self.fail_description_2, pos=(constants.canvas_width/2, 595), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.pass_title, pos=(constants.canvas_width/2, 515), pos_anchor='center')
                
        # Fruit and score
        if self.parent.current_day == 1:
            utils.blit(dest=canvas, source=self.result_surface_list[0]['surface_fruit'], pos=(constants.canvas_width/2 - 32, constants.canvas_height/2), pos_anchor='center')
            utils.blit(dest=canvas, source=self.result_surface_list[0]['surface'], pos=(constants.canvas_width/2 + 32, constants.canvas_height/2 + 4), pos_anchor='center')
        else:
            for i, option in enumerate(self.result_surface_list):
                utils.blit(dest=canvas, source=option['surface_fruit'], pos=(constants.canvas_width/2 - 32, 305 + i*120), pos_anchor='center')
                utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2 + 32, 307 + i*120), pos_anchor='center')
        
        # Continue text
        utils.blit(dest=canvas, source=self.continue_text, pos=(constants.canvas_width/2, 695), pos_anchor='center')
        