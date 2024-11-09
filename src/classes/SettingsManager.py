from src.library.essentials import *

class SettingsManager():
    def __init__(self):
        self.settings_file = os.path.join(dir.data, 'settings.lst')
        self.settings_list = [
            {
                'id': 'music_volume',
                'label': 'Music Volume',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.3,
                'value_default_label': '30%',
                'value_default_index': 3,
            },
            {
                'id': 'sfx_volume',
                'label': 'SFX Volume',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.4,
                'value_default_label': '40%',
                'value_default_index': 4,
            },
            {
                'id': 'ambience_volume',
                'label': 'Ambience Volume',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.3,
                'value_default_label': '30%',
                'value_default_index': 3,
            },
            {
                'id': 'fullscreen',
                'label': 'Fullscreen',
                'value': [0, 1],
                'value_label': ['off', 'on'],
                'value_default': 0,
                'value_default_label': 'off',
                'value_default_index': 0,
            },
            {
                'id': 'fps_cap',
                'label': 'FPS Cap',
                'value': [30, 60, 999],
                'value_label': ['30', '60', 'uncapped'],
                'value_default': 30,
                'value_default_label': '30',
                'value_default_index': 0,
            },
            {
                'id': 'skip_bootup',
                'label': 'Skip Bootup',
                'value': [0, 1],
                'value_label': ['off', 'on'],
                'value_default': 0,
                'value_default_label': 'off',
                'value_default_index': 0,
            },
        ]


    def load_all_settings_index(self):
        self.current_settings_index = []
        with open(self.settings_file, 'r') as fp:
            for line in fp.readlines():
                key, value = line.strip().split('=')
                for i in range(len(self.settings_list)):
                    if self.settings_list[i]['id'] == key:
                        self.current_settings_index.append(self.settings_list[i]['value'].index(float(value)))

        return self.current_settings_index


    def load_all_settings(self):
        self.current_settings = {}
        # when settings file is missing
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as fp:
                for setting in self.settings_list:
                    fp.write(f'{setting['id']}={setting['value_default']}\n')
                    self.current_settings[setting['id']] = setting['value_default']

        else:
            with open(self.settings_file, 'r+') as fp:
                for line in fp.readlines():
                    key, value = line.strip().split('=')
                    self.current_settings[key] = float(value)

        return self.current_settings
    

    def load_setting(self, setting):
        with open(self.settings_file, 'r') as fp:
            for line in fp.readlines():
                key, value = line.strip().split('=')
                if setting == key:
                    return float(value)
                

    def save_setting(self, current_settings_index):
        with open(self.settings_file, 'w') as fp:
            for i in range(len(self.settings_list)):
                option = self.settings_list[i]
                value = option['value'][current_settings_index[i]]
                fp.write(f"{option['id']}={value}\n")

            
    def reset_settings(self):
        with open(self.settings_file, 'w') as fp:
            for setting in self.settings_list:
                fp.write(f'{setting['id']}={setting['value_default']}\n')
                