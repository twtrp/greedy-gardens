from src.library.essentials import *
from src.classes.SettingsManager import SettingsManager
from src.states.MenuState import MenuState
from src.states.TutorialState import TutorialState
import traceback
import tkinter as tk
from tkinter import messagebox

class Game:
    def __init__(self):
        self.settings_manager = SettingsManager()
        if not os.path.exists(self.settings_manager.settings_file):
            self.first_run = True
        else:
            self.first_run = False

        self.settings = self.settings_manager.load_all_settings()
        self.fps_cap = self.settings['fps_cap']

        self.version_number = 'v1.0.0.beta12'
        self.title = f'Greedy Gardens'

        pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=4096)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
        pygame.display.set_caption(self.title)
        self.canvas = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))
        self.display_info = pygame.display.Info()
        
        if self.settings['fullscreen']:
            self.screen_width = self.display_info.current_w
            self.screen_height = self.display_info.current_h
            self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
        else:
            self.screen_width = constants.window_width
            self.screen_height = constants.window_height
            self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                  flags=pygame.HWSURFACE|pygame.DOUBLEBUF)

        utils.set_cursor(cursor=cursors.normal)
        self.screen.fill(color=colors.white)
        pygame.display.update()
        self.clock = pygame.time.Clock()

        self.music_channel = pygame.mixer.music
        self.music_channel.set_volume(self.settings['music_volume'] * 0.65)
        self.sfx_volume = self.settings['sfx_volume']
        self.ambience_channel = pygame.mixer.Channel(0)
        self.ambience_channel.set_volume(self.settings['ambience_volume'] * 0.75)
        utils.sound_play(sound=sfx.ambience, sound_channel=self.ambience_channel, loops=-1, fade_ms=3000)

        self.state_stack = []

        if not self.first_run:
            utils.music_load(music_channel=self.music_channel, name=music.menu_intro)
            utils.music_queue(music_channel=self.music_channel, name=music.menu_loop, loops=-1)

        self.finished_bootup = False


    # Class methods

    def apply_settings(self, setting_index):
        self.settings = self.settings_manager.load_all_settings()
        if setting_index == 2:
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
                self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
            else:
                self.screen_width = constants.window_width
                self.screen_height = constants.window_height
                self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                      flags=pygame.HWSURFACE|pygame.DOUBLEBUF)
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

        # Handle quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
            
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
        if (constants.canvas_width, constants.canvas_height) != (self.screen_width, self.screen_height):
            scaled_canvas = pygame.transform.scale(surface=self.canvas, size=(self.screen_width, self.screen_height))
            utils.blit(dest=self.screen, source=scaled_canvas)
        else:
            utils.blit(dest=self.screen, source=self.canvas)
        
        # Update display
        pygame.display.update()


    def game_loop(self):
        while True:
            try:
                # pygame.display.set_caption(f'{self.title} ({int(self.clock.get_fps())} FPS)')
                dt = self.clock.tick(self.fps_cap)/1000.0
                events = pygame.event.get()
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
