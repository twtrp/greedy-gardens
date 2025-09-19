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
        self.scroll_speed = 125  # pixels per second (auto-scroll speed)
        self.mouse_scroll_amount = 100  # pixels per mouse scroll input
        self.manual_scroll = False
        self.manual_scroll_timer = 0  # Timer to resume auto-scroll
        self.auto_scroll_delay = 1.0  # Resume auto-scroll after seconds (manual scroll cooldown)
        self.auto_scroll_start_delay = 1.0  # Wait seconds before starting auto-scroll
        self.auto_scroll_start_timer = 0  # Timer for initial delay & post-click delay
        self.auto_scroll_started = False  # Track if auto-scroll has started
        self.total_height = 0

        # Hold/drag state
        self.hold_pause = False
        self.drag_active = False
        self.drag_last_y = 0

        # Link handling
        self.clickable_links = []  # Store clickable link areas
        self.hovered_link = None
        
        # Pre-rendered surface for maximum performance
        self.credits_surface = None  # Will hold the entire credits as one surface
        self.credits_surface_height = 0
        self.static_links = []  # Store link positions relative to the surface

        self.is_hovering_back_button = False
        
        self.load_assets()


    #Main methods

    def update(self, dt, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Adjust mouse position for fullscreen scaling
        if self.game.screen_width != constants.canvas_width or self.game.screen_height != constants.canvas_height:
            rel_x = mouse_pos[0] / self.game.screen_width
            rel_y = mouse_pos[1] / self.game.screen_height
            mouse_pos = (rel_x * constants.canvas_width, rel_y * constants.canvas_height)
        
        self.hovered_link = None
        
        # Check for link hovers and clicks
        self.hovered_link = None
        for link in self.static_links:
            # Adjust link position based on scroll and clipping area
            adjusted_rect = pygame.Rect(
                link['rect'].x,  # Account for clipping area offset
                link['rect'].y + 23 - int(self.scroll_y),  # Account for scroll and clipping
                link['rect'].width + 5,
                link['rect'].height
            )
            
            # Check if the link is within the visible clipping area
            clip_area = pygame.Rect(23, 23, constants.canvas_width - 46, constants.canvas_height - 106)
            if clip_area.colliderect(adjusted_rect) and adjusted_rect.collidepoint(mouse_pos):
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
                    # Also push back auto-scroll start
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0
                    self.scroll_y -= 100
                elif event.key == pygame.K_DOWN:
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    # Also push back auto-scroll start
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0
                    self.scroll_y += 100

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.hold_pause = True
                    if not self.hovered_link:
                        self.drag_active = True
                        # Hold to pause AND drag-to-scroll
                        self.drag_last_y = event.pos[1]
                        # Apply "start delay" semantics to left-click, so auto-scroll
                        # waits self.auto_scroll_start_delay after the click/drag ends.
                        self.auto_scroll_started = False
                        self.auto_scroll_start_timer = 0
                        # We don't want the manual cooldown here; touch-like interactions
                        # should rely on start delay instead of manual delay.
                        self.manual_scroll = False
                        self.manual_scroll_timer = 0

                elif event.button == 2:  # Middle mouse
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()

                elif event.button == 4:  # Scroll up
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0  # Reset start delay as well
                    self.scroll_y -= self.mouse_scroll_amount

                elif event.button == 5:  # Scroll down
                    self.manual_scroll = True
                    self.manual_scroll_timer = 0  # Reset timer
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0  # Reset start delay as well
                    self.scroll_y += self.mouse_scroll_amount

            elif event.type == pygame.MOUSEBUTTONUP and not self.is_hovering_back_button:
                if event.button == 1:
                    # Release the hold-to-pause / drag
                    self.hold_pause = False
                    self.drag_active = False
                    # After releasing LMB, restart the "start delay" timer so auto-scroll resumes after delay
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0
                    # Ensure manual cooldown doesn't interfere; we want start-delay behavior
                    self.manual_scroll = False
                    self.manual_scroll_timer = 0

                    if self.hovered_link:
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        webbrowser.open(self.hovered_link['url'])

            elif event.type == pygame.MOUSEMOTION:
                # Drag-to-scroll (like touch): while holding LMB on empty area
                if self.drag_active and self.hold_pause and not self.hovered_link:
                    # Move opposite of mouse delta so dragging up scrolls down (touch-like)
                    dy = event.pos[1] - self.drag_last_y
                    self.drag_last_y = event.pos[1]
                    self.scroll_y -= dy  # invert for natural touch feel
                    # Keep auto-scroll off until the start delay elapses after release
                    self.auto_scroll_started = False
                    self.auto_scroll_start_timer = 0
                    # Make sure manual cooldown isn't running
                    self.manual_scroll = False
                    self.manual_scroll_timer = 0

        # Handle manual scroll timer (used for wheel/keys only)
        if self.manual_scroll:
            self.manual_scroll_timer += dt
            if self.manual_scroll_timer >= self.auto_scroll_delay:
                self.manual_scroll = False
                self.manual_scroll_timer = 0

        # Handle initial auto-scroll delay and left-click/drag post-delay
        # Only count if we're not in manual scroll mode and not currently holding
        if not self.manual_scroll and not self.hold_pause:
            if not self.auto_scroll_started:
                self.auto_scroll_start_timer += dt
                if self.auto_scroll_start_timer >= self.auto_scroll_start_delay:
                    self.auto_scroll_started = True

        # Auto-scroll if not manually controlled, not paused by hold, and delay has passed
        if not self.manual_scroll and not self.hold_pause and self.auto_scroll_started:
            # Calculate max scroll position using actual viewable area height
            viewable_height = constants.canvas_height - 106  # Match clipping area
            max_scroll_y = self.total_height - viewable_height + 50
            
            # Only auto-scroll if we haven't reached the bottom
            if self.scroll_y < max_scroll_y:
                self.scroll_y += self.scroll_speed * dt
            
        # Apply scroll limits for both auto and manual scrolling
        # Top limit: don't scroll above the visible area
        min_scroll_y = 0  # Start position for credits
        # Bottom limit: don't scroll beyond all content being visible
        viewable_height = constants.canvas_height - 106  # Match clipping area
        max_scroll_y = self.total_height - viewable_height + 50  # Small buffer after content ends
        
        self.scroll_y = max(min(self.scroll_y, max_scroll_y), min_scroll_y)

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                self.is_hovering_back_button = True
                self.cursor = button.hover_cursor
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                        if button.clicked:
                            utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                            self.exit_state()
            else:
                self.is_hovering_back_button = False
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

        # Cursor hint while holding to pause/drag (avoid overriding link-hand cursor)
        if (self.hold_pause or self.drag_active) and not self.hovered_link:
            self.cursor = cursors.normal

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

        self.bts_paper = utils.get_image(dir=dir.bts, name='paper.png')
        self.bts_paper = utils.effect_outline(surface=self.bts_paper, color=colors.mono_40, distance=3)

        self.bts_figma_paper = utils.get_image(dir=dir.bts, name='figma_paper.png')
        self.bts_figma_paper = utils.effect_outline(surface=self.bts_figma_paper, color=colors.mono_40, distance=3)

        self.bts_figma_game = utils.get_image(dir=dir.bts, name='figma_game.png')
        self.bts_figma_game = utils.effect_outline(surface=self.bts_figma_game, color=colors.mono_40, distance=3)
        
        self.bts_pygame_board_sim = utils.get_image(dir=dir.bts, name='pygame_board_sim.png')
        self.bts_pygame_board_sim = utils.effect_outline(surface=self.bts_pygame_board_sim, color=colors.mono_40, distance=3)
        

    def _setup_credits_content(self):
        """Setup the credits sections - edit this to modify credits content"""
        self.credits_sections = [
            {
                'texts': {
                    'text': ['Greedy Gardens'],
                    'font': fonts.wacky_pixels,
                    'size': 'large',
                    'padding': 0,
                },
                'padding_top': 200,
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['made with love by'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'padding': 0
                },
                'padding_bottom': 70
            },
            {
                'image': self.my_logo,
                'padding_bottom': -15
            },
            {
                'texts': {
                    'text': ['<itch.io>', ' ','<Linktree>'],
                    'size': 'small',
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': ['https://ttewtor.short.gy/itchio', None, 'https://ttewtor.short.gy/linktree']
                },
                'inline': True,
                'padding_bottom': 340,
            },


            {
                'image': self.bts_pygame_board_sim,
                'padding_bottom': -192
            },
            {
                'texts': {
                    'text': ['Game Board Generator Test in Pygame'],
                    'size': 'tiny',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 3
            },
            {
                'texts': {
                     'text': ['We screenshotted the board and then played the game by drawing on our iPad.'],
                    'size': 'tiny',
                    'color': colors.mono_205,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 100
            },


            {
                'texts': {
                    'text': ['Originally a college project by'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'color': colors.white,
                    'outline': True,
                },
                'padding_bottom': 35
            },
            {
                'image': self.team_namsom_logo_long,
                'padding_bottom': 30
            },
            {
                'texts': {
                    'text': ['Lead Designer and Programmer'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
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
                    'text': ['Core Programmers'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
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
                    'text': ['Development Pattern Designer'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
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
                'padding_bottom': 300
            },


            {
                'image': self.bts_figma_paper,
                'padding_bottom': -205
            },
            {
                'texts': {
                     'text': ['Paper Prototype Printouts in Figma'],
                    'size': 'tiny',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 3
            },
            {
                'texts': {
                     'text': ['We chose a balanced board from the generator to be played in class lab.'],
                    'size': 'tiny',
                    'color': colors.mono_205,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 90
            },


            {
                'texts': {
                    'text': ['Special Thanks'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'color': colors.white,
                    'outline': True,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Visual Consultant'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                    'padding': 10,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Alison (dmx)'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Windows Playtester'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['promptnut no.1 player'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['macOS Playtesters'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Alison (dmx)', 'noellnon'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'padding': 15,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Linux Playtester'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Ranviee', '<GitHub>'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [None, 'https://ttewtor.short.gy/ranvieegithub']
                },
                'inline': True,
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Help with Display Mode Issues'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Martinus from Pygame Discord'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Game Dev Class Teacher'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
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
                'padding_bottom': 50
            },
            {
                'texts': {
                    'text': ['Being cute'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                    'padding': 10,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['noellnon'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 100
            },


            {
                'texts': {
                    'text': ['Made with'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'color': colors.white,
                    'outline': True,
                },
                'padding_bottom': 60
            },
            {
                'image': self.pygame_ce_logo,
                'padding_bottom': 250
            },


            {
                'image': self.bts_paper,
                'padding_bottom': -200
            },
            {
                'texts': {
                    'text': ['Paper Prototype Played in Class Lab'],
                    'size': 'tiny',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 3
            },
            {
                'texts': {
                    'text': ['We decided the house and magic fruit locations with dice rolls.'],
                    'size': 'tiny',
                    'color': colors.mono_205,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 90
            },


            {
                'texts': {
                    'text': ['Inspired by'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'color': colors.white,
                    'outline': True,
                },
                'padding_bottom': 40
            },
            {
                'texts': {
                    'text': ['Aporta Game\'s Avenue'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 100
            },


            {
                'texts': {
                    'text': ['Asset Attributions'],
                    'font': fonts.wacky_pixels,
                    'size': 'small',
                    'color': colors.white,
                    'outline': True,
                },
                'padding_bottom': 50
            },

            {
                'texts': {
                    'text': ['Soundtrack'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['Towball - Towball\'s Crossing!', '<itch.io>'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [None, 'https://towball.itch.io/towballs-crossing']
                },
                'inline': True,
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Ambience'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': ['BurghRecords - Forest Ambience', '<YouTube>'],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [None, 'https://youtu.be/83X26UkmbkM?si=_xANQHf0wvVhEGTz']
                },
                'inline': True,
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Sound Effects'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['HUNTER AUDIO PRODUCTION - Retro 8bit SFX and Music Pack', '<itch.io>'],
                        ['SoupTonic - SoupTonic\'s sound SFX Pack 1', '<itch.io>'],
                        ['freesound community - Rooster crow', '<pixabay>'],
                        ['freesound community - card mixing', '<pixabay>'],
                        ['ZapSplat - Wooden stake hit, impact dry dirt, soil 1', '<zapsplat>'],
                        ['ZapSplat - Wooden stake hit, impact dry dirt, soil 3', '<zapsplat>'],
                        ['ZapSplat - Wooden stake hit, impact dry dirt, soil 4', '<zapsplat>'],
                        ['NE Sounds - enter button on a keyboard sound effect', '<YouTube>']
                    ],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [
                        [None,'https://hunteraudio.itch.io/8bit-sfx-and-music-pack'],
                        [None, 'https://souptonic.itch.io/souptonic-sfx-pack-1-ui-sounds'],
                        [None,'https://pixabay.com/sound-effects/rooster-crow-105568/'],
                        [None, 'https://pixabay.com/sound-effects/search/card-mixing-48088/'],
                        [None, 'https://www.zapsplat.com/music/wooden-stake-hit-impact-dry-dirt-soil-1/'],
                        [None, 'https://www.zapsplat.com/music/wooden-stake-hit-impact-dry-dirt-soil-3/'],
                        [None, 'https://www.zapsplat.com/music/wooden-stake-hit-impact-dry-dirt-soil-4/'],
                        [None, 'https://youtu.be/p47fFW2-I0k?si=-LXQlg4GhphGAIhX']
                    ],
                    'padding': 15
                },
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Fonts'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['Lazy Fox - LazyFox pixel font 2', '<itch.io>'],
                        ['Cool Boy Zone! - Wacky Pixels', '<itch.io>'],
                        ['Fekete_Tamas - Windows', '<itch.io>'],
                        ['Nimble Beasts - magofont1', '<itch.io>'],
                    ],
                    'size': [
                        ['small', 'small'],
                        ['smaller', 'smaller'],
                        ['small', 'small'],
                        ['small', 'small']
                    ],
                    'color': colors.white,
                    'font': [
                        [fonts.lf2, fonts.lf2],
                        [fonts.wacky_pixels, fonts.wacky_pixels],
                        [fonts.windows, fonts.windows],
                        [fonts.mago1, fonts.mago1],
                    ],
                    'long_shadow': False,
                    'link': [
                        [None, 'https://lazy-fox.itch.io/lazy-pixel-fonts'],
                        [None, 'https://3d.itch.io/fonts'],
                        [None, 'https://www.dafont.com/windows-2.font'],
                        [None, 'https://nimblebeastscollective.itch.io/magosfonts']
                    ],
                    'padding': 20
                },
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Menu Background Art'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['craftpix.net - Free Summer Pixel Backgrounds', '<itch.io>'],
                        ['craftpix.net - Nature Landscapes Free Pixel Art', '<itch.io>'],
                        ['craftpix.net - Free Sky Backgrounds', '<itch.io>'],
                    ],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [
                        [None, 'https://free-game-assets.itch.io/free-summer-pixel-art-backgrounds'],
                        [None, 'https://free-game-assets.itch.io/nature-landscapes-free-pixel-art'],
                        [None, 'https://free-game-assets.itch.io/free-sky-with-clouds-background-pixel-art-set'],
                    ],
                    'padding': 20
                },
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Tileset Sprites'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['SnowHex - Harvest Summer Forest Pack', '<itch.io>'],
                        ['almostApixel - SmallBurg Town Pack', '<itch.io>'],
                        ['danieldiggle - Sunnyside World', '<itch.io>'],
                        ['Kenmi - Cute Fantasy RPG 16x16', '<itch.io>'],
                    ],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [
                        [None, 'https://snowhex.itch.io/harvest-summer-forest-pack'],
                        [None, 'https://almostapixel.itch.io/smallburg-town-pack'],
                        [None, 'https://danieldiggle.itch.io/sunnyside'],
                        [None, 'https://kenmi-art.itch.io/cute-fantasy-rpg']
                    ],
                    'padding': 20
                },
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Fruit Sprites'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['SciGho - Fruit+', '<itch.io>'],
                    ],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [
                        [None, 'https://ninjikin.itch.io/fruit'],
                    ],
                    'padding': 20
                },
                'padding_bottom': 40
            },

            {
                'texts': {
                    'text': ['Miscellaneous Sprites'],
                    'size': 'smaller',
                    'color': colors.yellow_light,
                    'font': fonts.wacky_pixels,
                    'long_shadow': False,
                },
                'padding_bottom': 20
            },
            {
                'texts': {
                    'text': [
                        ['NYKNCK - Wind Pixel Art', '<itch.io>'],
                        ['craftpix.net - Free Skill 32x32 Cyberpunk Icons Pixel Art', '<itch.io>'],
                        ['Crusenho - Complete UI Essential Pack', '<itch.io>'],
                        ['Dream Mix - Pixel Keyboard Keys for UI', '<itch.io>'],
                        ['greenpixels - Buttons', '<itch.io>'],
                    ],
                    'size': 'small',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                    'link': [
                        [None, 'https://nyknck.itch.io/wind'],
                        [None, 'https://free-game-assets.itch.io/free-skill-3232-icons-for-cyberpunk-game'],
                        [None, 'https://crusenho.itch.io/complete-ui-essential-pack'],
                        [None, 'https://dreammixgames.itch.io/keyboard-keys-for-ui'],
                        [None, 'https://greenpixels.itch.io/pixel-art-asset-3']
                    ],
                    'padding': 20
                },
                'padding_bottom': 330
            },

            {
                'image': self.bts_figma_game,
                'padding_bottom': -228
            },
            {
                'texts': {
                     'text': ['Art and UI Concept in Figma'],
                    'size': 'tiny',
                    'color': colors.white,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 3
            },
            {
                'texts': {
                     'text': ['The rest was history.'],
                    'size': 'tiny',
                    'color': colors.mono_205,
                    'font': fonts.mago1,
                    'long_shadow': False,
                },
                'padding_bottom': 310
            },



            {
                'texts': {
                    'text': ['Thanks for playing!'],
                    'font': fonts.wacky_pixels,
                    'size': 'large',
                    'color': colors.white,
                },
                'padding_bottom': 240
            },
        ]
        
        # Calculate total height
        self._calculate_total_height()
        
        # Pre-render entire credits to single surface
        self._prerender_credits_surface()

    def _calculate_total_height(self):
        """Calculate total height for scrolling"""
        total = 0  # Starting offset
        
        for section in self.credits_sections:
            if 'texts' in section:
                # Text section
                total += section.get('padding_top', 0)
                
                # Calculate height for text structure
                texts_data = section['texts']
                text_array = texts_data['text']
                text_padding = texts_data.get('padding', 0)
                
                # Check if this section is inline (single line for all elements)
                is_inline = section.get('inline', False)
                
                if is_inline:
                    # Inline sections count as a single line regardless of text count
                    total += 30
                else:
                    # Check if we have nested arrays (new format)
                    if text_array and isinstance(text_array[0], list):
                        # Nested array format: each sub-array is a line
                        total += len(text_array) * 30
                        
                        # Additional padding between lines (but not after the last line)
                        if len(text_array) > 1:
                            total += (len(text_array) - 1) * text_padding
                    else:
                        # Normal format: base height for all text lines
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

    def _prerender_credits_surface(self):
        """Pre-render the entire credits to a single surface for maximum performance"""
        # Create a surface large enough to hold all credits content
        surface_height = self.total_height + 100  # Add minimal buffer
        self.credits_surface = pygame.Surface((constants.canvas_width, surface_height), pygame.SRCALPHA)
        self.credits_surface_height = surface_height
        
        # Clear static links and rebuild them
        self.static_links.clear()
        
        # Render all content to the surface
        current_y = 0
        line_height = 30
        
        for section in self.credits_sections:
            if 'texts' in section:
                # Text section with padding
                current_y += section.get('padding_top', 0)
                
                texts_data = section['texts']
                text_array = texts_data['text']
                text_padding = texts_data.get('padding', 0)
                is_inline = section.get('inline', False)
                
                # Handle links - can be string or array
                links = texts_data.get('link', [])
                if isinstance(links, str):
                    links = [links]
                
                # Check if we have nested arrays (new format)
                if text_array and isinstance(text_array[0], list):
                    # New nested format: each sub-array is a line with its own links
                    for line_idx, line_array in enumerate(text_array):
                        # Calculate total width for this line to center it
                        total_width = 0
                        text_surfaces = []
                        
                        # Get corresponding link array for this line
                        line_links = links[line_idx] if line_idx < len(links) else []
                        
                        # Pre-render all text elements in this line
                        for element_idx, text_element in enumerate(line_array):
                            if text_element:
                                # Check if this element has a corresponding link
                                has_link = element_idx < len(line_links) and line_links[element_idx] is not None
                                link_url = line_links[element_idx] if has_link else None
                                
                                # Get styling for this specific element
                                # Support both single values and arrays for per-element styling
                                font_data = texts_data.get('font', fonts.lf2)
                                size_data = texts_data.get('size', 'small')
                                color_data = texts_data.get('color', colors.white)
                                
                                # Handle per-element font - support 3D matrix [line][element]
                                if isinstance(font_data, list):
                                    # Check if this is a 3D matrix (list of lists)
                                    if line_idx < len(font_data) and isinstance(font_data[line_idx], list):
                                        # 3D matrix: font_data[line_idx][element_idx]
                                        line_fonts = font_data[line_idx]
                                        element_font = line_fonts[element_idx] if element_idx < len(line_fonts) else line_fonts[-1]
                                    else:
                                        # 2D array: font_data[element_idx] (same font array for all lines)
                                        element_font = font_data[element_idx] if element_idx < len(font_data) else font_data[-1]
                                else:
                                    # Single font for all elements
                                    element_font = font_data
                                
                                # Handle per-element size - support 3D matrix [line][element]
                                if isinstance(size_data, list):
                                    # Check if this is a 3D matrix (list of lists)
                                    if line_idx < len(size_data) and isinstance(size_data[line_idx], list):
                                        # 3D matrix: size_data[line_idx][element_idx]
                                        line_sizes = size_data[line_idx]
                                        element_size = line_sizes[element_idx] if element_idx < len(line_sizes) else line_sizes[-1]
                                    else:
                                        # 2D array: size_data[element_idx] (same size array for all lines)
                                        element_size = size_data[element_idx] if element_idx < len(size_data) else size_data[-1]
                                else:
                                    # Single size for all elements
                                    element_size = size_data
                                
                                # Handle per-element color - support 3D matrix [line][element] (but links are always blue)
                                if has_link:
                                    text_color = colors.link
                                else:
                                    if isinstance(color_data, list):
                                        # Check if this is a 3D matrix (list of lists)
                                        if line_idx < len(color_data) and isinstance(color_data[line_idx], list):
                                            # 3D matrix: color_data[line_idx][element_idx]
                                            line_colors = color_data[line_idx]
                                            text_color = line_colors[element_idx] if element_idx < len(line_colors) else line_colors[-1]
                                        else:
                                            # 2D array: color_data[element_idx] (same color array for all lines)
                                            text_color = color_data[element_idx] if element_idx < len(color_data) else color_data[-1]
                                    else:
                                        # Single color for all elements
                                        text_color = color_data
                                
                                item_surface = utils.get_text(
                                    text=text_element,
                                    font=element_font,
                                    size=element_size,
                                    color=text_color,
                                    long_shadow=texts_data.get('long_shadow', True),
                                    long_shadow_direction=texts_data.get('long_shadow_direction', 'bottom'),
                                    long_shadow_color=texts_data.get('long_shadow_color', None),
                                    outline=texts_data.get('outline', False),
                                    outline_color=texts_data.get('outline_color', colors.mono_40)
                                )
                                text_surfaces.append((item_surface, has_link, link_url))
                                total_width += item_surface.get_width()
                                if element_idx < len(line_array) - 1:  # Add spacing between elements
                                    total_width += 10
                        
                        # Calculate starting x position to center the entire line
                        start_x = (constants.canvas_width // 2) - (total_width // 2)
                        current_x = start_x
                        
                        # Render each text element in this line
                        for element_idx, (item_surface, has_link, link_url) in enumerate(text_surfaces):
                            text_x = current_x + item_surface.get_width() // 2
                            text_y = current_y

                            # Store link information if this is a link
                            if has_link and link_url:
                                text_rect = pygame.Rect(
                                    text_x - item_surface.get_width() // 2,
                                    text_y - item_surface.get_height() // 2,
                                    item_surface.get_width(),
                                    item_surface.get_height()
                                )
                                self.static_links.append({'rect': text_rect, 'url': link_url})
                            
                            # Blit to pre-rendered surface
                            utils.blit(dest=self.credits_surface, source=item_surface, pos=(text_x, text_y), pos_anchor=posanchors.center)
                            
                            # Move to next position
                            current_x += item_surface.get_width() + 10
                        
                        # Move to next line
                        current_y += line_height
                        if line_idx < len(text_array) - 1:
                            current_y += text_padding
                
                elif is_inline:
                    # Inline rendering: calculate total width and center all elements on one line
                    total_width = 0
                    text_surfaces = []
                    
                    # Pre-render all text elements to calculate total width
                    for i, text_line in enumerate(text_array):
                        if text_line:
                            # Check if this element has a corresponding link
                            has_link = i < len(links) and links[i] is not None
                            
                            # Use blue color for links, otherwise use specified color or white
                            if has_link:
                                text_color = colors.link
                            else:
                                text_color = texts_data.get('color', colors.white)
                            
                            item_surface = utils.get_text(
                                text=text_line,
                                font=texts_data.get('font', fonts.lf2),
                                size=texts_data.get('size', 'small'),
                                color=text_color,
                                long_shadow=texts_data.get('long_shadow', True),
                                long_shadow_direction=texts_data.get('long_shadow_direction', 'bottom'),
                                long_shadow_color=texts_data.get('long_shadow_color', None),
                                outline=texts_data.get('outline', False),
                                outline_color=texts_data.get('outline_color', colors.mono_40)
                            )
                            text_surfaces.append((item_surface, has_link, links[i] if has_link else None))
                            total_width += item_surface.get_width()
                            if i < len(text_array) - 1:  # Add spacing between elements
                                total_width += 10
                    
                    # Calculate starting x position to center the entire line
                    start_x = (constants.canvas_width // 2) - (total_width // 2)
                    current_x = start_x
                    
                    # Render each text element
                    for item_surface, has_link, link_url in text_surfaces:
                        text_x = current_x + item_surface.get_width() // 2
                        
                        # Store link information if this is a link
                        if has_link and link_url:
                            text_rect = pygame.Rect(
                                text_x - item_surface.get_width() // 2,
                                current_y - item_surface.get_height() // 2,
                                item_surface.get_width(),
                                item_surface.get_height()
                            )
                            self.static_links.append({'rect': text_rect, 'url': link_url})
                        
                        # Blit to pre-rendered surface
                        utils.blit(dest=self.credits_surface, source=item_surface, pos=(text_x, current_y), pos_anchor=posanchors.center)
                        
                        # Move to next position
                        current_x += item_surface.get_width() + 10
                    
                    # Move to next line
                    current_y += line_height
                else:
                    # Normal rendering: each text element on its own line
                    for i, text_line in enumerate(text_array):
                        if text_line:
                            # Check if this element has a corresponding link
                            has_link = i < len(links) and links[i] is not None
                            link_url = links[i] if has_link else None
                            
                            # Use blue color for links, otherwise use specified color or white
                            if has_link:
                                text_color = colors.link
                            else:
                                text_color = texts_data.get('color', colors.white)
                            
                            item_surface = utils.get_text(
                                text=text_line,
                                font=texts_data.get('font', fonts.lf2),
                                size=texts_data.get('size', 'small'),
                                color=text_color,
                                long_shadow=texts_data.get('long_shadow', True),
                                long_shadow_direction=texts_data.get('long_shadow_direction', 'bottom'),
                                long_shadow_color=texts_data.get('long_shadow_color', None),
                                outline=texts_data.get('outline', False),
                                outline_color=texts_data.get('outline_color', colors.mono_40)
                            )
                            
                            # Position calculation - center horizontally
                            text_x = constants.canvas_width // 2
                            
                            # Store link information with surface-relative coordinates
                            if has_link and link_url:
                                text_rect = pygame.Rect(
                                    text_x - item_surface.get_width() // 2,
                                    current_y - item_surface.get_height() // 2,
                                    item_surface.get_width(),
                                    item_surface.get_height()
                                )
                                self.static_links.append({'rect': text_rect, 'url': link_url})
                            
                            # Blit to pre-rendered surface
                            utils.blit(dest=self.credits_surface, source=item_surface, pos=(text_x, current_y), pos_anchor=posanchors.center)
                        
                        # Handle line advancement
                        current_y += line_height
                        if i < len(text_array) - 1:
                            current_y += text_padding
                
                current_y += section.get('padding_bottom', 0)
                
            elif 'image' in section:
                # Image section
                current_y += section.get('padding_top', 0)
                image = section['image']
                if image:
                    utils.blit(dest=self.credits_surface, source=image, pos=(constants.canvas_width // 2, current_y), pos_anchor=posanchors.center)
                    current_y += image.get_height() + 10
                current_y += section.get('padding_bottom', 0)



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
            color=(*colors.mono_40, 235),
            inner_border_width=3
        )

    def _setup_clipping(self, canvas):
        """Setup clipping mask for scrolling area"""
        clip_rect = pygame.Rect(23, 23, constants.canvas_width - 46, constants.canvas_height - 106)
        canvas.set_clip(clip_rect)

    def _render_credits_content(self, canvas):
        """Render the pre-rendered credits surface with scrolling"""
        if self.credits_surface:
            # Simply blit the pre-rendered surface with scroll offset
            source_rect = pygame.Rect(0, int(self.scroll_y), constants.canvas_width, constants.canvas_height - 106)
            dest_pos = (0, 23)  # Match the clipping area
            
            # Only blit if there's content to show
            if source_rect.y < self.credits_surface_height:
                canvas.blit(self.credits_surface, dest_pos, source_rect)
            

    def _render_back_button(self, canvas):
        """Render the back button"""
        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 680), pos_anchor=posanchors.center)
