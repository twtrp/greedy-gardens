from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.PlayState import PlayState
import webbrowser

class Menu_CreditsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        
        # Scrolling properties
        self.scroll_y = 0  # Start at top
        self.scroll_speed = 30  # pixels per second
        self.manual_scroll = False
        self.manual_scroll_timer = 0  # Timer to resume auto-scroll
        self.auto_scroll_delay = 2.0  # Resume auto-scroll after 2 seconds
        self.auto_scroll_start_delay = 3.0  # Wait 3 seconds before starting auto-scroll
        self.auto_scroll_start_timer = 0  # Timer for initial delay
        self.auto_scroll_started = False  # Track if auto-scroll has started
        self.total_height = 0
        
        # Link handling
        self.clickable_links = []  # Store clickable link areas
        self.hovered_link = None
        
        self.load_assets()


    #Main methods

    def update(self, dt, events):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_link = None
        
        # Check for link hovers and clicks
        for link in self.clickable_links:
            if link['rect'].collidepoint(mouse_pos):
                self.hovered_link = link
                self.cursor = cursors.hand
                break
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()
                elif event.key == pygame.K_UP:
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_start_timer = 0  # Reset start delay
                    self.scroll_y -= 100
                elif event.key == pygame.K_DOWN:
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_start_timer = 0  # Reset start delay
                    self.scroll_y += 100
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.hovered_link:
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        webbrowser.open(self.hovered_link['url'])
                elif event.button == 2:  # Middle mouse
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()
                elif event.button == 4:  # Scroll up
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_start_timer = 0  # Reset start delay
                    self.scroll_y -= 50
                elif event.button == 5:  # Scroll down
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_start_timer = 0  # Reset start delay
                    self.scroll_y += 50

        # Handle manual scroll timer
        if self.manual_scroll:
            self.manual_scroll_timer += dt
            if self.manual_scroll_timer >= self.auto_scroll_delay:
                self.manual_scroll = False
                self.manual_scroll_timer = 0

        # Handle initial auto-scroll delay
        if not self.auto_scroll_started and not self.manual_scroll:
            self.auto_scroll_start_timer += dt
            if self.auto_scroll_start_timer >= self.auto_scroll_start_delay:
                self.auto_scroll_started = True

        # Auto-scroll if not manually controlled and delay has passed
        if not self.manual_scroll and self.auto_scroll_started:
            # Calculate max scroll position
            max_scroll_y = self.total_height - constants.canvas_height + 150
            
            # Only auto-scroll if we haven't reached the bottom
            if self.scroll_y < max_scroll_y:
                self.scroll_y += self.scroll_speed * dt
            
        # Apply scroll limits for both auto and manual scrolling
        # Top limit: don't scroll above the visible area
        min_scroll_y = 0  # Start position for credits
        # Bottom limit: don't scroll beyond all content being visible
        max_scroll_y = self.total_height - constants.canvas_height + 150  # Small buffer after content ends
        
        self.scroll_y = max(min(self.scroll_y, max_scroll_y), min_scroll_y)

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                self.cursor = button.hover_cursor
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                        if button.clicked:
                            utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                            self.exit_state()
            else:
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def load_assets(self):
        # Initialize button system
        self._setup_buttons()
        
        # Load graphics
        self._load_graphics()
        
        # Setup credits content
        self._setup_credits_content()

    def _setup_buttons(self):
        """Setup the back button"""
        self.button_option_surface_list = []
        self.button_list = []
        
        self.button_option_surface_list.append({
            'id': 'back',
            'surface': utils.get_text(text='Back', font=fonts.lf2, size='medium', color=colors.white),
            'scale': 1.0
        })
        
        self.button_list.append(Button(
            game=self.game,
            id='back',
            width=300,
            height=80,
            pos=(constants.canvas_width/2, 680),
            pos_anchor=posanchors.center
        ))

    def _load_graphics(self):
        """Load all graphics assets"""
        self.image_ttewtor = utils.get_image(dir=dir.graphics, name='ttewtor_logo.png', mode='colorkey')

    def _setup_credits_content(self):
        """Setup the credits sections - edit this to modify credits content"""
        self.credits_sections = [
            {
                'texts': [
                    {
                        'text': 'Greedy Gardens',
                        'font': fonts.minecraftia,
                        'size': 'large',
                        'color': colors.green_light,
                        'long_shadow': True,
                        'long_shadow_direction': 'bottom',
                        'long_shadow_color': None,
                        'outline': True,
                        'outline_color': colors.mono_35,
                        'link': 'https://lazy-fox.itch.io/lazy-pixel-fonts'
                    }
                ],
                'padding_top': 50,
                'padding_bottom': 20
            },
            {
                'image': self.image_ttewtor,
                'padding_top': 50,
                'padding_bottom': 20
            }
        ]
        
        # Calculate total height
        self._calculate_total_height()

    def _calculate_total_height(self):
        """Calculate total height for scrolling"""
        total = 0  # Starting offset
        for section in self.credits_sections:
            if 'texts' in section:
                # Text section
                total += section.get('padding_top', 0)
                total += len(section['texts']) * 30  # Text item height
                total += section.get('padding_bottom', 0)
            elif 'image' in section:
                # Image section
                total += section.get('padding_top', 0)
                image = section['image']
                if image:
                    total += image.get_height() + 10  # Image height + spacing
                else:
                    total += 50  # Default image spacing if image is None
                total += section.get('padding_bottom', 0)
        self.total_height = total



    def render(self, canvas):
        # Draw background
        self._draw_background(canvas)
        
        # Setup clipping for scrolling area
        self._setup_clipping(canvas)
        
        # Clear clickable links for this frame
        self.clickable_links.clear()
        
        # Render scrolling content
        self._render_credits_content(canvas)
        
        # Remove clipping
        canvas.set_clip(None)
        
        # Render UI elements
        self._render_back_button(canvas)

    def _draw_background(self, canvas):
        """Draw the background box"""
        utils.draw_rect(
            dest=canvas,
            size=(constants.canvas_width - 40, constants.canvas_height - 100),
            pos=(20, 20),
            pos_anchor=posanchors.topleft,
            color=(*colors.mono_50, 225),
            inner_border_width=3
        )

    def _setup_clipping(self, canvas):
        """Setup clipping mask for scrolling area"""
        clip_rect = pygame.Rect(23, 23, constants.canvas_width - 46, constants.canvas_height - 106)
        canvas.set_clip(clip_rect)

    def _render_credits_content(self, canvas):
        """Render all credits sections with scrolling"""
        current_y = 0 - self.scroll_y
        
        for section in self.credits_sections:
            if 'texts' in section:
                # Text section with padding
                current_y += section.get('padding_top', 0)
                
                # Render text items
                for item in section['texts']:
                    if isinstance(item, dict):
                        # Text item with all text options
                        if item.get('text'):  # Skip empty text
                            # Determine if this is a clickable link
                            is_link = 'link' in item
                            text_color = item.get('color', colors.blue_light if is_link else colors.white)
                            
                            item_surface = utils.get_text(
                                text=item['text'],
                                font=item.get('font', fonts.lf2),
                                size=item.get('size', 'small'),
                                color=text_color,
                                long_shadow=item.get('long_shadow', True),
                                long_shadow_direction=item.get('long_shadow_direction', 'bottom'),
                                long_shadow_color=item.get('long_shadow_color', None),
                                outline=item.get('outline', True),
                                outline_color=item.get('outline_color', colors.mono_35)
                            )
                            
                            # Create clickable rectangle if it's a link
                            if is_link:
                                text_rect = pygame.Rect(
                                    constants.canvas_width // 2 - item_surface.get_width() // 2,
                                    current_y - item_surface.get_height() // 2,
                                    item_surface.get_width(),
                                    item_surface.get_height()
                                )
                                self.clickable_links.append({'rect': text_rect, 'url': item['link']})
                            
                            utils.blit(dest=canvas, source=item_surface, pos=(constants.canvas_width // 2, current_y), pos_anchor=posanchors.center)
                    elif isinstance(item, str):
                        # Simple string item with default styling
                        if item:  # Skip empty strings
                            item_surface = utils.get_text(
                                text=item,
                                font=fonts.lf2,
                                size='small',
                                color=colors.white,
                                long_shadow=True,
                                long_shadow_direction='bottom',
                                long_shadow_color=None,
                                outline=True,
                                outline_color=colors.mono_35
                            )
                            utils.blit(dest=canvas, source=item_surface, pos=(constants.canvas_width // 2, current_y), pos_anchor=posanchors.center)
                    current_y += 30
                
                current_y += section.get('padding_bottom', 0)
                
            elif 'image' in section:
                # Image section
                current_y += section.get('padding_top', 0)
                image = section['image']
                if image:
                    utils.blit(dest=canvas, source=image, pos=(constants.canvas_width // 2, current_y), pos_anchor=posanchors.center)
                    current_y += image.get_height() + 10
                current_y += section.get('padding_bottom', 0)

    def _render_back_button(self, canvas):
        """Render the back button"""
        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 680), pos_anchor=posanchors.center)
