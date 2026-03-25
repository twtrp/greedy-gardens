from src.library.essentials import *
from src.classes.SettingsManager import SettingsManager
from src.states.MenuState import MenuState
from src.states.TutorialState import TutorialState

class Game:
    def __init__(self):
        self.settings_manager = SettingsManager()
        
        # Delete settings.lst at startup if debug_first_run is enabled
        if debug.debug_first_run and os.path.exists(self.settings_manager.settings_file):
            try:
                os.remove(self.settings_manager.settings_file)
            except Exception as e:
                print(f"Debug: Failed to delete settings.lst at startup: {e}")
        
        if not os.path.exists(self.settings_manager.settings_file):
            self.first_run = True
        else:
            self.first_run = False

        self.settings = self.settings_manager.load_all_settings()
        self.fps_cap = self.settings['fps_cap']

        self.version_number = constants.game_version
        self.title = f'Greedy Gardens'

        pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=4096)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
        pygame.display.set_caption(self.title)
        self.canvas = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))
        # Ensure the logical canvas starts filled white so the visible game
        # area shows white while the letterboxed bars are black on first frame.
        try:
            self.canvas.fill(colors.white)
        except Exception:
            self.canvas.fill((255, 255, 255))
        self.display_info = pygame.display.Info()
        
        if self.settings['fullscreen']:
            self.screen_width = self.display_info.current_w
            self.screen_height = self.display_info.current_h
            self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.NOFRAME)
        else:
            self.screen_width = constants.window_width
            self.screen_height = constants.window_height
            self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height))

        # Compute display scale and offset for letterboxing (preserve aspect ratio)
        # display_scale: uniform scale to apply to the game canvas
        # display_target_size: scaled canvas size in pixels
        # display_offset: top-left offset where the scaled canvas is blitted on the screen
        def compute_display_geometry():
            sw, sh = self.screen_width, self.screen_height
            cw, ch = constants.canvas_width, constants.canvas_height
            scale = min(sw / cw, sh / ch)
            target_w = int(cw * scale)
            target_h = int(ch * scale)
            offset_x = (sw - target_w) // 2
            offset_y = (sh - target_h) // 2
            self.display_scale = scale
            self.display_target_size = (target_w, target_h)
            self.display_offset = (offset_x, offset_y)

        compute_display_geometry()

        utils.set_cursor(cursor=cursors.normal)
        # Draw initial frame with letterboxing (black bars) so the very first
        # frame shown to the user matches the runtime scaling and doesn't flash
        # an all-white screen.
        try:
            self.screen.fill((0, 0, 0))
            target_w, target_h = self.display_target_size
            scaled_canvas = pygame.transform.scale(self.canvas, (target_w, target_h))
            self.screen.blit(scaled_canvas, self.display_offset)
            pygame.display.update()
        except Exception:
            # If anything goes wrong, fallback to a solid black fill
            self.screen.fill((0, 0, 0))
            pygame.display.update()
        self.clock = pygame.time.Clock()

        self.music_channel = pygame.mixer.music
        # Apply debug mute if enabled
        if debug.debug_mute_music:
            self.music_channel.set_volume(0)
        else:
            self.music_channel.set_volume(self.settings['music_volume'] * 0.65)
        self.sfx_volume = self.settings['sfx_volume']
        self.ambience_channel = pygame.mixer.Channel(0)
        self.ambience_channel.set_volume(self.settings['ambience_volume'])
        utils.sound_play(sound=sfx.ambience, sound_channel=self.ambience_channel, loops=-1, fade_ms=3000)

        self.state_stack = []

        utils.music_load(music_channel=self.music_channel, name=music.menu_intro)
        utils.music_queue(music_channel=self.music_channel, name=music.menu_loop, loops=-1)

        self.finished_bootup = False
        self.focus_log_path = None  # Can be set to a file path for debugging focus issues
        self.window_minimized = False
        
        # 4K zoom mode for trailer capture (developer mode)
        self.zoom_4k_mode = False
        self.zoom_view_offset_x = 0
        self.zoom_view_offset_y = 0
        self.zoom_edge_pan_speed = 800  # pixels per second
        self._original_mouse_get_pos = pygame.mouse.get_pos  # Store original function
        self.zoom_cursor_sprite = None  # Scaled cursor for zoom mode
        self.zoom_cursor_name = None  # Track active cursor sprite key in zoom mode
        self.zoom_4k_surface = None  # Cached 4K surface for performance


    # Class methods

    def _get_transformed_mouse_pos(self):
        """Transform mouse position for 4K zoom mode"""
        screen_x, screen_y = self._original_mouse_get_pos()
        
        # Convert to viewport position (accounting for letterboxing)
        viewport_x = (screen_x - self.display_offset[0]) / self.display_scale
        viewport_y = (screen_y - self.display_offset[1]) / self.display_scale
        
        # The viewport shows a portion of the 4K surface
        # Calculate position in 4K space
        zoom_4k_x = viewport_x + (-self.zoom_view_offset_x)
        zoom_4k_y = viewport_y + (-self.zoom_view_offset_y)
        
        # Scale back down from 4K to original canvas coordinates (4K is 3x scale)
        canvas_x = zoom_4k_x / 3.0
        canvas_y = zoom_4k_y / 3.0
        
        # Clamp to canvas bounds
        canvas_x = max(0, min(constants.canvas_width, canvas_x))
        canvas_y = max(0, min(constants.canvas_height, canvas_y))
        
        # Convert back to screen coordinates where the game expects them
        adjusted_screen_x = int(canvas_x * self.display_scale + self.display_offset[0])
        adjusted_screen_y = int(canvas_y * self.display_scale + self.display_offset[1])
        
        return (adjusted_screen_x, adjusted_screen_y)

    def _refresh_zoom_cursor_sprite(self):
        """Sync zoom cursor sprite with the currently active game cursor."""
        cursor_data = utils.get_current_cursor()
        sprite_name = cursor_data.get('sprite', 'cursor_normal')
        if sprite_name == self.zoom_cursor_name and self.zoom_cursor_sprite is not None:
            return
        cursor_sprite = utils.get_sprite(sprite_sheet=spritesheets.cursors, target_sprite=sprite_name)
        self.zoom_cursor_sprite = pygame.transform.scale(
            cursor_sprite,
            (cursor_sprite.get_width() * 3, cursor_sprite.get_height() * 3)
        )
        self.zoom_cursor_name = sprite_name

    def apply_settings(self, setting_index):
        self.settings = self.settings_manager.load_all_settings()
        if setting_index == 2:
            # Apply debug mute if enabled, otherwise use settings
            if debug.debug_mute_music:
                self.music_channel.set_volume(0)
            else:
                self.music_channel.set_volume(self.settings['music_volume']*0.75)
        if setting_index == 3:
            self.sfx_volume = self.settings['sfx_volume']
        if setting_index == 4:
            self.ambience_channel.set_volume(self.settings['ambience_volume']*0.75)
        if setting_index == 0:
            mx, my = pygame.mouse.get_pos()
            current_w, current_h = self.screen.get_size()
            rel_x = mx / current_w
            rel_y = my / current_h
            if platform.system() == "Darwin":
                pygame.display.quit()
                pygame.display.init()       
            pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
            pygame.display.set_caption(self.title)
            if self.settings['fullscreen']:
                self.screen_width = self.display_info.current_w
                self.screen_height = self.display_info.current_h
                self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.NOFRAME)
            else:
                self.screen_width = constants.window_width
                self.screen_height = constants.window_height

                self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height))
            # Recompute display geometry after changing screen size
            try:
                # recompute using the same helper defined in __init__ scope
                sw, sh = self.screen_width, self.screen_height
                cw, ch = constants.canvas_width, constants.canvas_height
                scale = min(sw / cw, sh / ch)
                target_w = int(cw * scale)
                target_h = int(ch * scale)
                offset_x = (sw - target_w) // 2
                offset_y = (sh - target_h) // 2
                self.display_scale = scale
                self.display_target_size = (target_w, target_h)
                self.display_offset = (offset_x, offset_y)
            except Exception:
                # Keep previous values if anything goes wrong
                pass
            current_w, current_h = self.screen.get_size()
            new_mx = int(rel_x * current_w)
            new_my = int(rel_y * current_h)
            pygame.mouse.set_pos((new_mx, new_my))
        if setting_index == 1:
            self.fps_cap = self.settings['fps_cap'] + 1

    def start_menu_music(self):
        if not self.music_channel.get_busy():
            self.music_channel.play()

    def show_error_popup(self, error):
        error_message = f"{traceback.format_exc()}"

        # Create a minimal tkinter window as parent (for taskbar support)
        root = tk.Tk()
        root.title("Greedy Gardens - Fatal Error")
        root.geometry("1x1+0+0") 
        root.attributes('-alpha', 0.0) 
        
        # Make sure the messagebox appears in front
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # Create error message with version info
        full_message = f"Greedy Gardens has encountered a fatal error.\n\n"
        full_message += f"\n{error_message}\n\n"
        full_message += f"Please screenshot this error and report it to the developer. Thanks!"
        
        # Show the error dialog with parent for taskbar visibility
        messagebox.showerror("Greedy Gardens - Fatal Error", full_message, parent=root)
        root.destroy()


    # Main methods

    def update(self, dt, events):
        # Handle 4K zoom edge panning (developer mode)
        if debug.debug_developer_mode and self.zoom_4k_mode:
            mouse_x, mouse_y = self._original_mouse_get_pos()  # Use original position for edge detection
            screen_w, screen_h = self.screen.get_size()
            
            # Define edge threshold (pixels from edge)
            edge_threshold = 50
            pan_amount = self.zoom_edge_pan_speed * dt
            
            # Pan left
            if mouse_x < edge_threshold:
                self.zoom_view_offset_x += pan_amount
                # Clamp to not pan beyond left edge
                self.zoom_view_offset_x = min(self.zoom_view_offset_x, 0)
            
            # Pan right
            if mouse_x > screen_w - edge_threshold:
                self.zoom_view_offset_x -= pan_amount
                # Clamp to not pan beyond right edge (4K width - canvas width)
                self.zoom_view_offset_x = max(self.zoom_view_offset_x, -(3840 - constants.canvas_width))
            
            # Pan up
            if mouse_y < edge_threshold:
                self.zoom_view_offset_y += pan_amount
                # Clamp to not pan beyond top edge
                self.zoom_view_offset_y = min(self.zoom_view_offset_y, 0)
            
            # Pan down
            if mouse_y > screen_h - edge_threshold:
                self.zoom_view_offset_y -= pan_amount
                # Clamp to not pan beyond bottom edge (4K height - canvas height)
                self.zoom_view_offset_y = max(self.zoom_view_offset_y, -(2160 - constants.canvas_height))
        
        # Update current state
        if self.state_stack:
            self.state_stack[-1].update(dt=dt, events=events)
        else:
            if self.first_run:
                self.first_run = False
                TutorialState(game=self, parent=self, stack=self.state_stack, finished_bootup=self.finished_bootup).enter_state()
            else:
               MenuState(game=self, parent=self, stack=self.state_stack, finished_bootup=self.finished_bootup).enter_state()
            # MenuState(game=self, parent=self, stack=self.state_stack, finished_bootup=self.finished_bootup).enter_state()

        # Handle quit
        for event in events:
            # Handle window focus/minimize events
            try:
                # Check for window minimize/restore events
                if hasattr(pygame, 'WINDOWEVENT') and event.type == pygame.WINDOWEVENT:
                    # WINDOWEVENT_MINIMIZED = 5, WINDOWEVENT_RESTORED = 6, WINDOWEVENT_FOCUS_GAINED = 12
                    if hasattr(event, 'event'):
                        if event.event == 5:  # Minimized
                            self.window_minimized = True
                        elif event.event in (6, 12):  # Restored or focus gained
                            if self.window_minimized:
                                self.window_minimized = False
                                # Force a display refresh to fix potential rendering issues
                                pygame.event.clear()
                                self.render()
                                pygame.display.flip()
                
                # Legacy pygame versions use ACTIVEEVENT
                if hasattr(pygame, 'ACTIVEEVENT') and event.type == pygame.ACTIVEEVENT:
                    if hasattr(event, 'state') and hasattr(event, 'gain'):
                        if event.state == 1 and event.gain == 0:  # Lost focus
                            self.window_minimized = True
                        elif event.state == 1 and event.gain == 1:  # Gained focus
                            if self.window_minimized:
                                self.window_minimized = False
                                pygame.event.clear()
                                self.render()
                                pygame.display.flip()
                
                # Diagnostic logging for focus/window events
                if self.focus_log_path and event.type in (pygame.ACTIVEEVENT if hasattr(pygame, 'ACTIVEEVENT') else -1, 
                                                           pygame.VIDEOEXPOSE if hasattr(pygame, 'VIDEOEXPOSE') else -1,
                                                           pygame.WINDOWEVENT if hasattr(pygame, 'WINDOWEVENT') else -1):
                    with open(self.focus_log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - EVENT {event!r}\n")
                        if hasattr(event, 'event'):
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - WINDOWEVENT {event.event}\n")
            except Exception:
                # Don't let event handling failures break the game
                pass

            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
            
            # Developer mode: F1 to toggle 4K zoom mode
            if debug.debug_developer_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.zoom_4k_mode = not self.zoom_4k_mode
                    if self.zoom_4k_mode:
                        print("4K zoom mode enabled - use mouse at screen edges to pan")
                        # Center the view initially
                        self.zoom_view_offset_x = -(3840 - constants.canvas_width) // 2
                        self.zoom_view_offset_y = -(2160 - constants.canvas_height) // 2
                        # Override mouse.get_pos to return transformed coordinates
                        pygame.mouse.get_pos = self._get_transformed_mouse_pos
                        # Hide system cursor and create scaled cursor
                        pygame.mouse.set_visible(False)
                        self._refresh_zoom_cursor_sprite()
                        # Pre-create 4K surface for performance
                        self.zoom_4k_surface = pygame.Surface((3840, 2160))
                    else:
                        print("4K zoom mode disabled")
                        self.zoom_view_offset_x = 0
                        self.zoom_view_offset_y = 0
                        # Restore original mouse.get_pos
                        pygame.mouse.get_pos = self._original_mouse_get_pos
                        # Show system cursor
                        pygame.mouse.set_visible(True)
                        self.zoom_cursor_sprite = None
                        self.zoom_cursor_name = None
                        self.zoom_4k_surface = None
            
            # Developer mode: print cursor position with '/' key
            if debug.debug_developer_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SLASH:
                    mouse_pos = pygame.mouse.get_pos()
                    canvas_x = (mouse_pos[0] - self.display_offset[0]) / self.display_scale
                    canvas_y = (mouse_pos[1] - self.display_offset[1]) / self.display_scale
                    print(f"Cursor position - ({int(canvas_x)}, {int(canvas_y)})")
                
                # Developer mode: move window with arrow keys (only in windowed mode)
                if not self.settings['fullscreen']:
                    window_pos = pygame.display.get_window_position() if hasattr(pygame.display, 'get_window_position') else (0, 0)
                    new_x, new_y = window_pos
                    
                    if event.key == pygame.K_UP:
                        new_y -= 300
                    elif event.key == pygame.K_DOWN:
                        new_y += 300
                    elif event.key == pygame.K_LEFT:
                        new_x -= 300
                    elif event.key == pygame.K_RIGHT:
                        new_x += 300
                    
                    if (event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
                        if hasattr(pygame.display, 'set_window_position'):
                            pygame.display.set_window_position((new_x, new_y))
                            print(f"Window moved to ({new_x}, {new_y})")
            
            # F11 to cycle fullscreen modes
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Cycle fullscreen setting: 0 -> 1 -> 2 -> 0
                    self.settings['fullscreen'] = (self.settings['fullscreen'] + 1) % 3
                    
                    # Save the new setting to file
                    with open(self.settings_manager.settings_file, 'w') as fp:
                        for setting in self.settings_manager.settings_list:
                            fp.write(f"{setting['id']}={self.settings[setting['id']]}\n")
                    
                    # Update settings state if it's open
                    for state in self.state_stack:
                        if hasattr(state, 'substate_stack'):
                            for substate in state.substate_stack:
                                if substate.__class__.__name__ == 'Menu_SettingsState':
                                    # Reload the settings index to reflect the change
                                    substate.current_settings_index = substate.settings_manager.load_all_settings_index()
                                    # Update the displayed text
                                    for i, setting in enumerate(substate.settings_manager.settings_list):
                                        text_string = setting['label'] + ':  ' + setting['value_label'][substate.current_settings_index[i]]
                                        text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
                                        substate.settings_option_surface_list[i]['surface'] = text
                        
                        # Update pause menu settings in PlayState/Tutorial_PlayState if open
                        if hasattr(state, 'pause_settings_surface_list') and hasattr(state, 'settings_manager'):
                            # Reload the settings index
                            state.current_settings_index = state.settings_manager.load_all_settings_index()
                            # Update pause menu settings display
                            for pause_setting in state.pause_settings_surface_list:
                                i = pause_setting['settings_list_index']
                                setting = state.settings_manager.settings_list[i]
                                text_string = setting['label'] + ':  ' + setting['value_label'][state.current_settings_index[i]]
                                text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white, outline=False)
                                pause_setting['surface'] = text
                    
                    # Preserve mouse position
                    mx, my = pygame.mouse.get_pos()
                    current_w, current_h = self.screen.get_size()
                    rel_x = mx / current_w
                    rel_y = my / current_h
                    
                    # Recreate screen with new mode
                    if platform.system() == "Darwin":
                        pygame.display.quit()
                        pygame.display.init()
                    pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
                    pygame.display.set_caption(self.title)
                    
                    if self.settings['fullscreen']:
                        self.screen_width = self.display_info.current_w
                        self.screen_height = self.display_info.current_h
                        self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.NOFRAME)
                    else:
                        self.screen_width = constants.window_width
                        self.screen_height = constants.window_height
                        self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height))
                    
                    # Recompute display geometry for letterboxing
                    try:
                        sw, sh = self.screen_width, self.screen_height
                        cw, ch = constants.canvas_width, constants.canvas_height
                        scale = min(sw / cw, sh / ch)
                        target_w = int(cw * scale)
                        target_h = int(ch * scale)
                        offset_x = (sw - target_w) // 2
                        offset_y = (sh - target_h) // 2
                        self.display_scale = scale
                        self.display_target_size = (target_w, target_h)
                        self.display_offset = (offset_x, offset_y)
                    except Exception:
                        pass
                    
                    # Restore mouse position
                    current_w, current_h = self.screen.get_size()
                    new_mx = int(rel_x * current_w)
                    new_my = int(rel_y * current_h)
                    pygame.mouse.set_pos((new_mx, new_my))

            # # TEST CRASH: Press Ctrl+Shift+C to simulate a crash
            # if event.type == pygame.KEYDOWN:
            #     keys = pygame.key.get_pressed()
            #     if keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT] and event.key == pygame.K_c:
            #         raise RuntimeError("This is a test crash! Press Ctrl+Shift+C was pressed to simulate an error.")
    

    def render(self):
        # Render current state
        if self.state_stack:
            self.state_stack[-1].render(canvas=self.canvas)

        # Render canvas to screen
        cw, ch = constants.canvas_width, constants.canvas_height
        if self.zoom_4k_mode:
            self._refresh_zoom_cursor_sprite()
            # Scale the canvas up to 4K (3x scale from 1280x720) and blit to cached surface
            scaled_canvas = pygame.transform.scale(self.canvas, (3840, 2160))
            self.zoom_4k_surface.blit(scaled_canvas, (0, 0))
            
            # Extract the viewport (original canvas size) from the 4K surface
            viewport_rect = pygame.Rect(
                -self.zoom_view_offset_x,
                -self.zoom_view_offset_y,
                cw,
                ch
            )
            viewport = self.zoom_4k_surface.subsurface(viewport_rect)
            
            # Now scale this viewport to fit the screen
            if (cw, ch) != (self.screen_width, self.screen_height):
                target_w, target_h = self.display_target_size
                final_scaled = pygame.transform.scale(viewport, (target_w, target_h))
                self.screen.fill((0, 0, 0))
                self.screen.blit(final_scaled, self.display_offset)
            else:
                self.screen.blit(viewport, (0, 0))
            
            # Draw scaled cursor on top
            if self.zoom_cursor_sprite:
                mouse_x, mouse_y = self._original_mouse_get_pos()
                self.screen.blit(self.zoom_cursor_sprite, (mouse_x, mouse_y))
        else:
            # Normal rendering (original code)
            # If the screen size doesn't match the game's logical canvas, scale the
            # canvas while preserving aspect ratio and center it. Fill the rest of
            # the screen with black bars (letterbox/pillarbox).
            if (cw, ch) != (self.screen_width, self.screen_height):
                target_w, target_h = self.display_target_size
                # Use .scale for sharpened (2), .smoothscale for consistent (1 or default)
                if self.settings.get('fullscreen', 1) == 2:
                    scaled_canvas = pygame.transform.scale(self.canvas, (target_w, target_h))
                else:
                    scaled_canvas = pygame.transform.smoothscale(self.canvas, (target_w, target_h))
                # Fill background with black bars
                try:
                    self.screen.fill((0, 0, 0))
                except Exception:
                    self.screen.fill((0, 0, 0))
                # Blit the centered, scaled canvas
                self.screen.blit(scaled_canvas, self.display_offset)
            else:
                self.screen.blit(self.canvas, (0, 0))
        
        # Update display
        pygame.display.update()


    def game_loop(self):
        while True:
            try:
                raw_dt = self.clock.tick(self.fps_cap)/1000.0
                dt = min(raw_dt, 0.1)
                
                # Pump events to keep window responsive
                pygame.event.pump()
                
                # Get events, but limit queue size to prevent flooding after focus loss
                events = pygame.event.get()
                
                # If event queue is suspiciously large (>100), clear non-essential events
                if len(events) > 100:
                    # Keep only quit, key, and mouse events
                    events = [e for e in events if e.type in (
                        pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
                        pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, 
                        pygame.MOUSEMOTION
                    )]
                
                self.update(dt=dt, events=events)
                self.render()
                
                # Extra display update to ensure window responsiveness after minimize/restore
                if self.window_minimized:
                    pygame.display.flip()
            except KeyboardInterrupt:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
            except Exception as e:
                traceback.print_exc()
                self.show_error_popup(e)
                pygame.mixer.stop()
                pygame.quit()
                sys.exit(1)


if __name__ == '__main__':
    game = Game()
    try:
        game.game_loop()
    except Exception as e:
        traceback.print_exc()
        game.show_error_popup(e)
        sys.exit(1)
    finally:
        # Delete settings.lst after game closes if debug_first_run is enabled
        if debug.debug_first_run:
            try:
                if os.path.exists(game.settings_manager.settings_file):
                    os.remove(game.settings_manager.settings_file)
            except Exception as e:
                print(f"Debug: Failed to delete settings.lst: {e}")
