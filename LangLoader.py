import os
import SettingManager

languages = {}
failsave_lang = "English"

def load_files(path):
    try:
        path = os.path.normpath(path)
        language_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if language_files:
            for lang in language_files:
                lang_key = lang.removesuffix('.txt')
                languages[lang_key] = load_file(os.path.abspath(os.path.join(path, lang)))
        print(f"{"|".join(languages.keys())} language file loaded!")
    except Exception:
        pass

def load_file(path):
    if not os.path.exists(path):
         return
    loaded_file = {}
    with open(path, 'r', encoding="utf-16") as file:
                while True:
                    line =  file.readline().encode("raw_unicode_escape").decode('unicode_escape')
                    if not line :
                         break
                    if line.endswith('\n'):
                        line = line[:-1]
                    splits = line.split('=')
                    if len(splits) == 0 or len(splits) > 2 or '$' not in line:
                         continue
                    key = splits[0].removeprefix('$')
                    value = splits[1]
                    loaded_file[key] = value
    return loaded_file
                    

def text(keyword, default_text):
    setting_lang =  SettingManager.loaded_setting.get("current_UILang")
    lang_code = setting_lang if setting_lang else failsave_lang
    if lang_code in languages.keys() and keyword in languages[lang_code].keys():
        lang = languages[lang_code]
    else:
        lang = {keyword : default_text}

    if keyword in lang.keys():
        return lang[keyword]


# LangLoader.text("", )