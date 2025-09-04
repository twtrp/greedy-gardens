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
        self.scroll_speed = 100  # pixels per second (auto-scroll speed)
        self.mouse_scroll_amount = 100  # pixels per mouse scroll input
        self.manual_scroll = False
        self.manual_scroll_timer = 0  # Timer to resume auto-scroll
        self.auto_scroll_delay = 1.25  # Resume auto-scroll after seconds
        self.auto_scroll_start_delay = 1.0  # Wait seconds before starting auto-scroll
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
                    self.scroll_y -= self.mouse_scroll_amount
                elif event.button == 5:  # Scroll down
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_start_timer = 0  # Reset start delay
                    self.scroll_y += self.mouse_scroll_amount

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
        self.cursor = cursors.scroll


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
        self.my_logo = utils.get_image(dir=dir.branding, name='ttewtor_logo.png', mode='colorkey')
        self.my_logo = pygame.transform.scale_by(surface=self.my_logo, factor=2)

        self.team_namsom_logo_long = utils.get_image(dir=dir.branding, name='team_namsom_logo_long.png', mode='colorkey')
        self.team_namsom_logo_long = pygame.transform.scale_by(surface=self.team_namsom_logo_long, factor=4)

        self.pygame_ce_logo = utils.get_image(dir=dir.branding, name='pygame_ce_logo.png', mode='colorkey')
        self.pygame_ce_logo = pygame.transform.smoothscale_by(surface=self.pygame_ce_logo, factor=0.15)

    def _setup_credits_content(self):
        """Setup the credits sections - edit this to modify credits content"""
        self.credits_sections = [
            {
                'texts': {
                    'text': ['Greedy Gardens'],
                    'size': 'large',
                    'padding': 0
                },
                'padding_top': 250,
                'padding_bottom': 30
            },
            {
                'texts': {
                    'text': ['a game by'],
                    'size': 'medium',
                    'padding': 0
                },
                'padding_bottom': 55
            },
            {
                'image': self.my_logo,
                'padding_bottom': -25
            },
            {
                'texts': {
                    'text': ['<itch.io>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://ttewtor.short.gy/itchio'
                },
                'next_line': False,
                'padding_right': 10,
            },
            {
                'texts': {
                    'text': ['<Linktree>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://ttewtor.short.gy/linktree'
                },
                'padding_bottom': 150,
            },


            {
                'texts': {
                    'text': ['Originally a college project by'],
                    'size': 'medium',
                    'color': colors.white,
                },
                'padding_bottom': 35
            },
            {
                'image': self.team_namsom_logo_long,
                'padding_bottom': 30
            },
            {
                'texts': {
                    'text': ['Lead Designing and Programming'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Piraboon (ttewtor) Piyawarapong'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Core Programming'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        'Kittisak Wanganansukdee',
                        'Krittidech Paijitjinda',
                        'Napat Ariyapattanaporn',
                    ],
                    'padding': 15,
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Development Pattern Designing'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Teetawat Bussabarati'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 105
            },


            {
                'texts': {
                    'text': ['Made with'],
                    'size': 'medium',
                    'color': colors.white,
                },
                'padding_bottom': 60
            },
            {
                'image': self.pygame_ce_logo,
                'padding_bottom': 50
            },


            {
                'texts': {
                    'text': ['Special Thanks'],
                    'size': 'medium',
                    'color': colors.white,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Windows Playtesting'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['promptnut - #1 player'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['macOS Playtesting and ttewtor Logo Dino Idea'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'padding': 10,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['alison (dmx)'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Linux Playtesting'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Ranviee'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'next_line': False,
                'padding_right': 10
            },
            {
                'texts': {
                    'text': ['<GitHub>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://ttewtor.short.gy/ranvieegithub'
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Game Dev Class Teacher'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Dr. SangGyu Nam'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Being Cute'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Noell'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 105
            },


            {
                'texts': {
                    'text': ['Attributions'],
                    'size': 'medium',
                    'color': colors.white,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Main Menu Song'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['RoccoW - Why Did the Crow Cross the Road?'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'next_line': False,
                'padding_right': 10
            },
            {
                'texts': {
                    'text': ['<SoundCloud>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://soundcloud.com/roccow/why-did-the-crow-cross-the-road'
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Gameplay Soundtrack'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Towball - Towball\'s Crossing!'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'next_line': False,
                'padding_right': 10
            },
            {
                'texts': {
                    'text': ['<itch.io>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://towball.itch.io/towballs-crossing'
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Sound Effects'],
                    'size': 'small',
                    'color': colors.yellow_light,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Towball - Towball\'s Crossing!'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'next_line': False,
                'padding_right': 10
            },
            {
                'texts': {
                    'text': ['<itch.io>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': 'https://towball.itch.io/towballs-crossing'
                },
                'padding_bottom': 40
            },
        ]
        
        # Calculate total height
        self._calculate_total_height()

    def _calculate_total_height(self):
        """Calculate total height for scrolling"""
        total = 0  # Starting offset
        skip_next = False  # Track if we should skip sections that are part of inline groups
        
        for i, section in enumerate(self.credits_sections):
            if skip_next:
                skip_next = False
                continue
                
            if 'texts' in section:
                # Text section
                total += section.get('padding_top', 0)
                
                # Calculate height for new text structure
                texts_data = section['texts']
                text_array = texts_data['text']
                text_padding = texts_data.get('padding', 0)
                
                # Check if this section is inline
                next_line = section.get('next_line', True)
                
                if not next_line:
                    # This is an inline section, find all connected inline sections
                    inline_sections = [section]
                    for j in range(i + 1, len(self.credits_sections)):
                        next_section = self.credits_sections[j]
                        if 'texts' not in next_section:
                            break
                        inline_sections.append(next_section)
                        if next_section.get('next_line', True):
                            break
                    
                    # Count only one line height for all inline sections
                    total += 30  # One line for all inline content
                    
                    # Add bottom padding from the last inline section
                    if inline_sections:
                        total += inline_sections[-1].get('padding_bottom', 0)
                    
                    # Skip the sections we've already counted
                    skip_next = len(inline_sections) - 1 > 0
                    for _ in range(len(inline_sections) - 1):
                        if i + 1 < len(self.credits_sections):
                            # Mark to skip next iterations
                            pass
                else:
                    # Normal section (not inline)
                    # Base height for all text lines
                    total += len(text_array) * 30
                    
                    # Additional padding between lines (but not after the last line)
                    if len(text_array) > 1:
                        total += (len(text_array) - 1) * text_padding
                    
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
        current_x = constants.canvas_width // 2  # Start at center
        line_height = 30  # Standard line height
        inline_mode = False  # Track if we're in inline mode
        inline_start_x = 0  # Track where inline content started
        
        for section_idx, section in enumerate(self.credits_sections):
            if 'texts' in section:
                # Text section with padding
                current_y += section.get('padding_top', 0)
                
                # Check if texts is an array of items or a single object with text array
                texts_data = section['texts']
                # New structure: single object with text array
                text_array = texts_data['text']
                text_padding = texts_data.get('padding', 0)
                
                # Check if this section starts inline mode or continues it
                next_line = section.get('next_line', True)
                
                # If starting inline mode, calculate starting position for centering
                if not next_line and not inline_mode:
                    # Calculate total width of inline content to center it
                    total_width = 0
                    temp_sections = []
                    
                    # Look ahead to find all inline sections
                    for temp_idx in range(section_idx, len(self.credits_sections)):
                        temp_section = self.credits_sections[temp_idx]
                        if 'texts' not in temp_section:
                            break
                        
                        temp_texts_data = temp_section['texts']
                        temp_text_array = temp_texts_data['text']
                        
                        for temp_text in temp_text_array:
                            if temp_text:
                                temp_surface = utils.get_text(
                                    text=temp_text,
                                    font=temp_texts_data.get('font', fonts.lf2),
                                    size=temp_texts_data.get('size', 'small'),
                                    color=temp_texts_data.get('color', colors.white),
                                    long_shadow=temp_texts_data.get('long_shadow', True),
                                    long_shadow_direction=temp_texts_data.get('long_shadow_direction', 'bottom'),
                                    long_shadow_color=temp_texts_data.get('long_shadow_color', None),
                                    outline=temp_texts_data.get('outline', True),
                                    outline_color=temp_texts_data.get('outline_color', colors.mono_35)
                                )
                                total_width += temp_surface.get_width()
                                
                        # Add padding_right if specified
                        total_width += temp_section.get('padding_right', 0)
                        
                        # Stop if next section goes to new line
                        if temp_section.get('next_line', True):
                            break
                    
                    # Set starting position to center the entire inline content
                    inline_start_x = (constants.canvas_width // 2) - (total_width // 2)
                    current_x = inline_start_x
                    inline_mode = True
                
                for i, text_line in enumerate(text_array):
                    if text_line:  # Skip empty strings
                        # Determine if this is a clickable link
                        is_link = 'link' in texts_data
                        text_color = texts_data.get('color', colors.blue_light if is_link else colors.white)
                        
                        item_surface = utils.get_text(
                            text=text_line,
                            font=texts_data.get('font', fonts.lf2),
                            size=texts_data.get('size', 'small'),
                            color=text_color,
                            long_shadow=texts_data.get('long_shadow', True),
                            long_shadow_direction=texts_data.get('long_shadow_direction', 'bottom'),
                            long_shadow_color=texts_data.get('long_shadow_color', None),
                            outline=texts_data.get('outline', True),
                            outline_color=texts_data.get('outline_color', colors.mono_35)
                        )
                        
                        # Position for inline mode (left-aligned from current_x) or centered
                        if inline_mode:
                            text_x = current_x + item_surface.get_width() // 2
                        else:
                            text_x = constants.canvas_width // 2
                        
                        # Create clickable rectangle if it's a link
                        if is_link:
                            text_rect = pygame.Rect(
                                text_x - item_surface.get_width() // 2,
                                current_y - item_surface.get_height() // 2,
                                item_surface.get_width(),
                                item_surface.get_height()
                            )
                            self.clickable_links.append({'rect': text_rect, 'url': texts_data['link']})
                        
                        utils.blit(dest=canvas, source=item_surface, pos=(text_x, current_y), pos_anchor=posanchors.center)
                        
                        # Move current_x for next inline element
                        if inline_mode:
                            current_x += item_surface.get_width()
                    
                    # Add vertical spacing for normal mode
                    if not inline_mode:
                        current_y += line_height
                        if i < len(text_array) - 1:  # Add padding between items, but not after the last one
                            current_y += text_padding
                
                # Handle end of section
                if next_line:
                    # This section ends the line
                    if inline_mode:
                        current_y += line_height  # Move to next line
                        current_x = constants.canvas_width // 2  # Reset to center
                        inline_mode = False
                else:
                    # This section continues inline, add right padding
                    if inline_mode:
                        current_x += section.get('padding_right', 10)
                
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
