from src.library.essentials import *

class SettingsManager():
    def __init__(self):
        self.settings_file = os.path.join(dir.data, 'settings.lst')
        self.settings_list = [
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
                'label': 'Framerate',
                'value': [60, 999],
                'value_label': ['60', 'uncapped'],
                'value_default': 60,
                'value_default_label': '60',
                'value_default_index': 0,
            },
            {
                'id': 'music_volume',
                'label': 'Music',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.8,
                'value_default_label': '80%',
                'value_default_index': 8,
            },
            {
                'id': 'sfx_volume',
                'label': 'Sound Effects',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.8,
                'value_default_label': '80%',
                'value_default_index': 8,
            },
            {
                'id': 'ambience_volume',
                'label': 'Ambience',
                'value': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'value_label': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                'value_default': 0.8,
                'value_default_label': '80%',
                'value_default_index': 8,
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
        settings_corrected = False
        
        with open(self.settings_file, 'r') as fp:
            for line in fp.readlines():
                key, value = line.strip().split('=')
                for i in range(len(self.settings_list)):
                    if self.settings_list[i]['id'] == key:
                        try:
                            self.current_settings_index.append(self.settings_list[i]['value'].index(float(value)))
                        except ValueError:
                            # Value not found in list, reset to default (index 0)
                            print(f"Warning: Invalid setting value {value} for {key}, resetting to default")
                            self.current_settings_index.append(0)
                            settings_corrected = True
        
        # If any settings were corrected, save the corrected values back to file
        if settings_corrected:
            self.save_setting(self.current_settings_index)

        return self.current_settings_index


    def load_all_settings(self):
        self.current_settings = {}
        
        # Ensure data directory exists
        if not os.path.exists(dir.data):
            os.makedirs(dir.data)
            
        # when settings file is missing
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as fp:
                for setting in self.settings_list:
                    fp.write(f'{setting['id']}={setting['value_default']}\n')
                    self.current_settings[setting['id']] = setting['value_default']

        else:
            settings_corrected = False
            with open(self.settings_file, 'r') as fp:
                for line in fp.readlines():
                    key, value = line.strip().split('=')
                    float_value = float(value)
                    
                    # Validate that this value exists in the corresponding setting's value list
                    setting_found = False
                    for setting in self.settings_list:
                        if setting['id'] == key:
                            if float_value in setting['value']:
                                self.current_settings[key] = float_value
                            else:
                                # Invalid value, reset to default
                                print(f"Warning: Invalid setting value {float_value} for {key}, resetting to default")
                                self.current_settings[key] = setting['value_default']
                                settings_corrected = True
                            setting_found = True
                            break
                    
                    # If setting ID not found in settings_list, ignore it
                    if not setting_found:
                        print(f"Warning: Unknown setting {key}, ignoring")
            
            # If any settings were corrected, save them back to file
            if settings_corrected:
                with open(self.settings_file, 'w') as fp:
                    for setting in self.settings_list:
                        if setting['id'] in self.current_settings:
                            fp.write(f'{setting['id']}={self.current_settings[setting['id']]}\n')
                        else:
                            fp.write(f'{setting['id']}={setting['value_default']}\n')
                            self.current_settings[setting['id']] = setting['value_default']

        return self.current_settings
    

    def load_setting(self, setting):
        with open(self.settings_file, 'r') as fp:
            for line in fp.readlines():
                key, value = line.strip().split('=')
                if setting == key:
                    return float(value)
                

    def save_setting(self, current_settings_index):
        # Ensure data directory exists
        if not os.path.exists(dir.data):
            os.makedirs(dir.data)
            
        with open(self.settings_file, 'w') as fp:
            for i in range(len(self.settings_list)):
                option = self.settings_list[i]
                value = option['value'][current_settings_index[i]]
                fp.write(f"{option['id']}={value}\n")

            
    def reset_settings(self):
        # Ensure data directory exists
        if not os.path.exists(dir.data):
            os.makedirs(dir.data)
            
        with open(self.settings_file, 'w') as fp:
            for setting in self.settings_list:
                fp.write(f'{setting['id']}={setting['value_default']}\n')
                