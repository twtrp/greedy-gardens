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


    # Class methods

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
            # Diagnostic logging for focus/window events
            try:
                if self.focus_log_path and event.type in (pygame.ACTIVEEVENT, pygame.VIDEOEXPOSE, getattr(pygame, 'WINDOWFOCUS', None)):
                    with open(self.focus_log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - EVENT {event!r}\n")
                # Some pygame versions use WINDOWEVENT with event.event attribute values
                if self.focus_log_path and event.type == getattr(pygame, 'WINDOWEVENT', None):
                    with open(self.focus_log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - WINDOWEVENT {event.event}\n")
            except Exception:
                # Don't let logging failures break the game
                pass

            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
            
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
            
            # F11 to toggle fullscreen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Toggle fullscreen setting
                    self.settings['fullscreen'] = 1 if self.settings['fullscreen'] == 0 else 0
                    
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
        # If the screen size doesn't match the game's logical canvas, scale the
        # canvas while preserving aspect ratio and center it. Fill the rest of
        # the screen with black bars (letterbox/pillarbox).
        cw, ch = constants.canvas_width, constants.canvas_height
        if (cw, ch) != (self.screen_width, self.screen_height):
            target_w, target_h = self.display_target_size
            scaled_canvas = pygame.transform.scale(self.canvas, (target_w, target_h))
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
