import copy
import toml

settings = 1
default_setting = { 
    "window_pos" : [-1, -1, -1, -1],
    "current_UILang" : 'English',
    "lang_codes" : ['En']
    }

loaded_setting = {}

config_path = ""

def loadSettings():
    global loaded_setting
    loaded_setting = read_toml_config(config_path)
    if not loaded_setting:
        print("No config loaded, copy from default.")
        loaded_setting = copy.deepcopy(default_setting)
    for key, value in default_setting.items():
        if key not in loaded_setting.keys():
            print(f"Add missing config content\nMissing: {key} = {value}")
            loaded_setting[key] = copy.deepcopy(value)
    print(f"👇Setting Loaded👇 \n{loaded_setting}")


def getSetting():
    return copy.deepcopy(loaded_setting)

def saveSetting(setting):
    global loaded_setting
    loaded_setting = save_toml_config(setting, config_path)
    print(f"Setting Manager: {loaded_setting} Syncronized!")


def save_toml_config(config, file_path):
    try:
        with open(file_path, 'w', encoding='utf-16') as f:
            toml.dump(config, f)
        print(f"Saved configuration to '{file_path}'")
        return config
    except Exception as e:
        print(f"Error saving '{file_path}': {e}")

def read_toml_config(file_path):
    try:
        with open(file_path, 'r', encoding='utf-16') as f:
            config = toml.load(f)
            return config
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.\nCreating new...")
        return save_toml_config(default_setting, file_path)
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return None