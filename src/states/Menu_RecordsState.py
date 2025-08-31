from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Menu_RecordsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # Ensure data directory exists
        if not os.path.exists(dir.data):
            os.makedirs(dir.data)

        try:
            self.sql_conn = sqlite3.connect(os.path.join(dir.data, 'records.sqlite'))
            self.sql_cursor = self.sql_conn.cursor()
            
            # Create table if it doesn't exist
            self.sql_cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    score INTEGER,
                    seed INTEGER,
                    seed_type TEXT
                )
            ''')
            self.sql_conn.commit()
        except Exception as e:
            print(f"Error connecting to records database: {e}")
            # Create dummy connection that will fail gracefully
            self.sql_conn = None
            self.sql_cursor = None

        self.table_width = 600
        self.table_height = 300
        self.table_scroll_offset = 0
        self.table_row_height = 36

        self.button_list = []
        self.load_assets()

        self.table_row_surface_dict = {}
        self.ordered_row_ids = []

        if self.sql_cursor is not None:
            try:
                query = f'SELECT rowid, * FROM records ORDER BY {self.parent.records_sorter["column"]} {self.parent.records_sorter["order"]}'
                self.sql_cursor.execute(query)
                rows = self.sql_cursor.fetchall()
                    
                for row in rows:
                    rowid = row[0]
                    self.ordered_row_ids.append(rowid)
                    surface = pygame.Surface(size=(constants.canvas_width, self.table_row_height), flags=pygame.SRCALPHA)
                    row_data = {
                        'rowid': rowid,
                        'score': row[1],
                        'seed': row[2],
                        'seed_type': row[3]
                    }
                    for idx, key in enumerate(row_data.keys()):
                        cell = utils.get_text(
                            text=str(row_data[key]),
                            font=fonts.lf2,
                            size='small',
                            color=colors.mono_50,
                            long_shadow=False,
                            outline=False
                        )
                        utils.blit(dest=surface,
                                   source=cell,
                                   pos=(self.table_header_list[idx]['x'] - 8, 0),
                                   pos_anchor=posanchors.midtop)
                    self.table_row_surface_dict[rowid] = surface
            except Exception as e:
                print(f"Error loading records data: {e}")
                # Continue with empty records if there's an error

        self.table_max_scroll_offset = min(0, -len(self.ordered_row_ids) * self.table_row_height + self.table_height - 12)

    
    #Main methods

    def load_assets(self):
        self.page_title = utils.get_text(text='Records', font=fonts.lf2, size='huge', color=colors.yellow_light)
        
        self.table_header_list = [
            {
                'id': 'rowid',
                'text': 'Game',
                'x': 400
            },
            {
                'id': 'score',
                'text': 'Score',
                'x': 520
            },
            {
                'id': 'seed',
                'text': 'Seed',
                'x': 650
            },
            {
                'id': 'seed_type',
                'text': 'Seed Type',
                'x': 840
            }
        ]
        self.table_header_surface_list = []
        for i, header in enumerate(self.table_header_list):
            dummy = utils.get_text(text=header['text']+' ^', font=fonts.lf2, size='small', color=colors.white)
            header_surface = pygame.Surface(size=dummy.get_size(), flags=pygame.SRCALPHA)
            if self.parent.records_sorter['column'] == header['id']:
                if self.parent.records_sorter['order'] == 'ASC':
                    text_surface = utils.get_text(text=header['text'], font=fonts.lf2, size='small', color=colors.white)
                    utils.blit(dest=header_surface, source=text_surface, pos=(0, 0), pos_anchor=posanchors.topleft)
                    arrow_surface = utils.get_text(text=' ^', font=fonts.lf2, size='small', color=colors.white, long_shadow=False, outline=False)
                    flipped_arrow_surface = pygame.transform.flip(surface=arrow_surface, flip_x=False, flip_y=True)
                    deco_distance = utils.get_font_deco_distance(font=fonts.lf2, size='small')
                    deco_arrow_surface = utils.effect_long_shadow(surface=flipped_arrow_surface,
                                                                  distance=deco_distance,
                                                                  color=utils.color_darken(color=colors.white, factor=0.5))
                    deco_arrow_surface = utils.effect_outline(surface=deco_arrow_surface, distance=deco_distance)
                    utils.blit(dest=header_surface, source=deco_arrow_surface, pos=(header_surface.get_width(), 3), pos_anchor=posanchors.topright)
                elif self.parent.records_sorter['order'] == 'DESC':
                    header_surface = utils.get_text(text=header['text']+' ^', font=fonts.lf2, size='small', color=colors.white)
            else:
                header_surface = pygame.Surface(size=dummy.get_size(), flags=pygame.SRCALPHA)
                text_surface = utils.get_text(text=header['text'], font=fonts.lf2, size='small', color=colors.white)
                utils.blit(dest=header_surface, source=text_surface, pos=(0, 0), pos_anchor=posanchors.topleft)
            self.table_header_surface_list.append({
                'id': header['id'],
                'surface': header_surface,
                'scale': 1.0,
                'x': header['x']
            })
        for i, header in enumerate(self.table_header_surface_list):
            self.button_list.append(Button(game=self.game,
                                            id=header['id'],
                                            group='header',
                                            surface=header['surface'],
                                            pos=(header['x'], 200),
                                            pos_anchor=posanchors.center,
                                            padding_x=9,
                                            padding_y=10))
        
        if self.sql_cursor is not None:
            try:
                query = f'SELECT rowid,* FROM records ORDER BY {self.parent.records_sorter["column"]} {self.parent.records_sorter["order"]}'
                self.sql_cursor.execute(query)
                rows = self.sql_cursor.fetchall()
                self.table_row_list = []
                for row in rows:
                    self.table_row_list.append({
                        'rowid': row[0],
                        'score': row[1],
                        'seed': row[2],
                        'seed_type': row[3]
                    })
            except Exception as e:
                print(f"Error loading table data: {e}")
                self.table_row_list = []
        else:
            self.table_row_list = []
        self.table_row_surface_list = []
        for row in self.table_row_list:
            row_keys = list(self.table_row_list[0].keys())
            surface = pygame.Surface(size=(constants.canvas_width, 30), flags=pygame.SRCALPHA)
            for key in row_keys:
                cell = utils.get_text(text=str(row[key]),
                                      font=fonts.lf2,
                                      size='small',
                                      color=colors.mono_50,
                                      long_shadow=False,
                                      outline=False)
                utils.blit(dest=surface,
                           source=cell,
                           pos=(self.table_header_list[row_keys.index(key)]['x'] - 8, 0),
                           pos_anchor=posanchors.midtop)
            self.table_row_surface_list.append(surface)

        self.button_option_list = [
            {
                'id': 'back',
                'text': 'Back',
            }
        ]
        self.button_option_surface_list = []
        for option in self.button_option_list:
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.button_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1.0
            })
        for i, option in enumerate(self.button_option_surface_list):
            self.button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=300,
                height=80,
                pos=(constants.canvas_width/2, 580),
                pos_anchor=posanchors.center
            ))

        self.button_list.append(Button(
            game=self.game,
            id='table',
            width=self.table_width,
            height=self.table_height,
            pos=(constants.canvas_width/2, 380),
            pos_anchor=posanchors.center,
            enable_click=False,
            hover_cursor=cursors.scroll
        ))

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()
                for button in self.button_list:
                    if button.id == 'table' and button.hovered:
                        if event.button == 4:
                            if self.table_scroll_offset != 0:
                                utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.table_scroll_offset = min(self.table_scroll_offset + self.table_row_height, 0)
                        elif event.button == 5:
                            if self.table_scroll_offset != self.table_max_scroll_offset:
                                utils.sound_play(sound=sfx.scroll, volume=self.game.sfx_volume*0.35)
                            self.table_scroll_offset = max(self.table_scroll_offset - self.table_row_height, self.table_max_scroll_offset)

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                if button.hover_cursor is not None:
                    self.cursor = button.hover_cursor

                for surface in self.table_header_surface_list + self.button_option_surface_list:
                    if button.id == surface['id']:
                        surface['scale'] = min(surface['scale'] + 2.4*dt, 1.2)

            else:
                for surface in self.table_header_surface_list + self.button_option_surface_list:
                    if button.id == surface['id']:
                        surface['scale'] = max(surface['scale'] - 2.4*dt, 1.0)

            if button.clicked:
                if button.id == 'rowid' or button.id == 'score' or button.id == 'seed' or button.id == 'seed_type':
                    if button.id == self.parent.records_sorter['column']:
                        if self.parent.records_sorter['order'] == 'ASC':
                            self.parent.records_sorter['order'] = 'DESC'
                        else:
                            self.parent.records_sorter['order'] = 'ASC'
                    else:
                        self.parent.records_sorter['column'] = button.id
                    self.table_header_surface_list = []
                    for i, header in enumerate(self.table_header_list):
                        dummy = utils.get_text(text=header['text']+' ^', font=fonts.lf2, size='small', color=colors.white)
                        header_surface = pygame.Surface(size=dummy.get_size(), flags=pygame.SRCALPHA)
                        if self.parent.records_sorter['column'] == header['id']:
                            if self.parent.records_sorter['order'] == 'ASC':
                                text_surface = utils.get_text(text=header['text'], font=fonts.lf2, size='small', color=colors.white)
                                utils.blit(dest=header_surface, source=text_surface, pos=(0, 0), pos_anchor=posanchors.topleft)
                                arrow_surface = utils.get_text(text=' ^', font=fonts.lf2, size='small', color=colors.white, long_shadow=False, outline=False)
                                flipped_arrow_surface = pygame.transform.flip(surface=arrow_surface, flip_x=False, flip_y=True)
                                deco_distance = utils.get_font_deco_distance(font=fonts.lf2, size='small')
                                deco_arrow_surface = utils.effect_long_shadow(
                                    surface=flipped_arrow_surface,
                                    distance=deco_distance,
                                    color=utils.color_darken(color=colors.white, factor=0.5
                                ))
                                deco_arrow_surface = utils.effect_outline(surface=deco_arrow_surface, distance=deco_distance)
                                utils.blit(dest=header_surface, source=deco_arrow_surface, pos=(header_surface.get_width(), 3), pos_anchor=posanchors.topright)
                            elif self.parent.records_sorter['order'] == 'DESC':
                                header_surface = utils.get_text(text=header['text']+' ^', font=fonts.lf2, size='small', color=colors.white)
                        else:
                            header_surface = pygame.Surface(size=dummy.get_size(), flags=pygame.SRCALPHA)
                            text_surface = utils.get_text(text=header['text'], font=fonts.lf2, size='small', color=colors.white)
                            utils.blit(dest=header_surface, source=text_surface, pos=(0, 0), pos_anchor=posanchors.topleft)
                        new_scale = 1.0 if header['id'] != button.id else 1.2
                        self.table_header_surface_list.append({
                            'id': header['id'],
                            'surface': header_surface,
                            'scale': new_scale,
                            'x': header['x']
                        })
                        if self.sql_cursor is not None:
                            try:
                                query = f'SELECT rowid FROM records ORDER BY {self.parent.records_sorter["column"]} {self.parent.records_sorter["order"]}'
                                if self.parent.records_sorter['column'] == 'score':
                                    query += ', seed ASC, seed_type ASC'
                                elif self.parent.records_sorter['column'] == 'seed':
                                    query += ', score DESC, seed_type ASC'
                                elif self.parent.records_sorter['column'] == 'seed_type':
                                    query += ', score DESC, seed ASC'
                                self.sql_cursor.execute(query)
                                self.ordered_row_ids = [row[0] for row in self.sql_cursor.fetchall()]
                            except Exception as e:
                                print(f"Error sorting records: {e}")
                                self.ordered_row_ids = []
                    utils.sound_play(sound=sfx.click, volume=self.game.sfx_volume)

                if button.id == 'back':
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    if self.sql_conn is not None:
                        try:
                            self.sql_conn.close()
                        except Exception as e:
                            print(f"Error closing database connection: {e}")
                    self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor=posanchors.center)

        for header in self.table_header_surface_list:
            scaled_surface = pygame.transform.scale_by(surface=header['surface'], factor=header['scale'])
            utils.blit(dest=canvas, source=scaled_surface, pos=(header['x'], 200), pos_anchor=posanchors.center)

        utils.draw_rect(
            dest=canvas,
            size=(self.table_width, self.table_height),
            pos=(constants.canvas_width/2, 380),
            pos_anchor=posanchors.center,
            color=(*colors.white, 165),
            inner_border_width=3
        )
        
        table_surface = pygame.Surface(size=(constants.canvas_width, self.table_height), flags=pygame.SRCALPHA)
        if not self.ordered_row_ids:
            no_records_text = utils.get_text(
                text="No games played yet",
                font=fonts.lf2,
                size='small',
                color=colors.mono_50,
                long_shadow=False,
                outline=False
            )
            utils.blit(
                dest=table_surface,
                source=no_records_text,
                pos=(constants.canvas_width / 2, self.table_height / 2),
                pos_anchor=posanchors.center
            )
        else:
            for i, rowid in enumerate(self.ordered_row_ids):
                row_surface = self.table_row_surface_dict[rowid]
                utils.blit(
                    dest=table_surface,
                    source=row_surface,
                    pos=(0, 7 + i*self.table_row_height + self.table_scroll_offset),
                    pos_anchor=posanchors.topleft
                )
        utils.blit(dest=canvas, source=table_surface, pos=(constants.canvas_width/2, 380), pos_anchor=posanchors.center)

        for i, option in enumerate(self.button_option_surface_list):
            scaled_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=scaled_surface, pos=(constants.canvas_width/2, 580), pos_anchor=posanchors.center)
