import datetime
import json
import os
import uuid
import chardet
import MsgHandler
from datetime import datetime
import LangLoader

mcmdict = ["text","param","displayName","help","pageDisplayName"]
mcm_lang_text = {}
mcm_lang_key_stats = {}
file_encoding = None

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        print(f"Detected encoding: {encoding} with confidence: {confidence}")
        return encoding

def read_json_file(file_path):
    """
    Try reading the JSON file using various encodings and returning the parsed data.

    Parameters:
    - file_path (str): JSON file path

    Returns:
    - dict: The parsed JSON data, or None if the file reading fails.
    """
    global file_encoding
    file_encoding = detect_encoding(file_path)
    try:
        with open(file_path, 'r', encoding=file_encoding) as file:
            print(f"load {os.path.basename(file_path)} success!\nUsing Encoding:{file_encoding}")
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found!")
        MsgHandler.errorBox(LangLoader.text("Msg_File_Not_Found", "File Not Found!"), LangLoader.text("Msg_File_Not_Found_Text", "File not found at: \n") + str(file_path))
        return None
    except Exception as e:
        print(f"Failed to read JSON: {str(e)}")
        MsgHandler.errorBox(LangLoader.text("Msg_Fail_To_Read", "Failed To Read Json!"), LangLoader.text("Msg_Fail_To_Read_Text", "Failed to read Json!\nError message: ") + str(e))
        return None

    # LangLoader.text("", )
def saveLangText(file_path, data = dict, encoding='utf-16'):
    """
    saveLangText save language text to file

    :param file_path: path to save the text file
    :param data: keywords and original text descriptions, defaults to dict
    """
    try:
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # make all key values into a list, and join them with \n symbol
        # this helps text file not ending with a new line
        temp_list = []
        for key, value in data.items():
            temp_list.append(f"{key}\t{value}")
        content = "\n".join(temp_list)
        # Open file, 'w' mode means writing mode, if the file does not exist, create a new file
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
            
    except Exception as e:
        MsgHandler.errorBox(LangLoader.text("Msg_Fail_Save_Lang", "Fail To Save Language Translation File!"), LangLoader.text("Msg_Fail_Save_Lang_Text", "Fail to save translation text file!\nError message: ") + str(e))
        


def saveJson(file_path, data, encoding = None):
    """
    saveJson save json file to this path

    :param file_path: path to save json file
    :param data: json data to save
    :param encoding: encoding to save json file
    """
    if not encoding:
        encoding = file_encoding
    try:
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent = 4 )
    except Exception as e:
        MsgHandler.errorBox(LangLoader.text("Msg_Fail_Save_Json", "Fail To Save Json!"), LangLoader.text("Msg_Fail_Save_Json_Text", "Fail To Save Json!\nError message: ") + str(e))


def getTimeTag():
    """
        Get the current time formatted as a tag.

        :return: Formatted current time tag in the format "YYYY_MM_DD_HH_MM_SS".
    """
    # Get the current time
    current_time = datetime.now()
    # Format the current time as specified, replacing default separators with underscores
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    return formatted_time


def readMCM(mcm = dict, modName = None):
    """
    Reads and processes the MCM data.

    :param mcm: MCM data to be processed, defaults to an empty dictionary.
    :return: Converted MCM data.
    """
    global mcm_lang_text
    global mcm_lang_key_stats
    mcm_lang_key_stats = {}
    mcm_lang_text = {}
    converted_mcm = traverse(mcm,[modName])
    # print(json.dumps(mcm_lang_text, indent=4))
    # print(json.dumps(converted_mcm, indent=4))
    return converted_mcm


def traverse(obj, path=None, parentName = None):
    """
    Traverse and process the MCM data.

    :param obj: The MCM data to be processed.
    :param path: The current traversal path, defaults to None.
    :param isOption: Flag to indicate if the current object is an option, defaults to False.
    :return: The processed MCM data.
    """
    global mcm_lang_text
    global mcmdict
    global mcm_lang_key_stats
    if path is None:
        path = []
    if isinstance(obj, dict):
        temp_dict = {}
        for key, value in obj.items(): # Iterate over dictionary items
            # define reusable variables
            temp_dict[key] = value 
            key_set = obj.keys()
            lang_keyword = path + [key]
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # waiting to implement optional value
            if key in mcmdict and '<' not in value: 

                lang_keyword, id_good_stats = getKeyword(full_set=obj,suffix=key,lang_keyword=lang_keyword,path=path)
                """
                # if it has ID or Type, use it first
                # mark this data if it's not using id as keyword for further determine
                # id_good_stats, when it's 0, means it has an ID to make its' keyword
                # when 1, means there are a type can use for it's keyword
                # when 2, means there aren't type for it to use as keyword
                id_good_stats = 0
                if "id" in key_set:
                    lang_keyword = makeLangKeyword([obj["id"]],key)
                elif "text" == key:
                    id_good_stats = 1
                    suffix = key
                    if "type" in key_set and obj["type"] != "text":
                        suffix = f"{obj["type"]}_{suffix}"
                    lang_keyword = makeLangKeyword(path, suffix)
                elif "help" == key:
                    id_good_stats = 1
                    suffix = key
                    if "type" in key_set and obj["type"] != "help":
                        suffix = f"{obj["type"]}_{suffix}"
                    lang_keyword = makeLangKeyword(path, suffix)
                else:
                    id_good_stats = 2
                    lang_keyword = makeLangKeyword(lang_keyword)
                # Store the value in mcm_lang_text with lang_keyword
                # Save keyword and value to lang text dictionary
                """
                mcm_lang_text[lang_keyword] = value 
                # store orignal text and converted keyword to dict for user to preview
                mcm_lang_key_stats[lang_keyword] = id_good_stats
                # Replace the value with new language keyword after
                value = lang_keyword 
            # if found valueOptions, means there is a option list,
            # pass parent name to options to make them use parent name
            # better if mcm update a big difference, as long as the id's not change
            # it will keep consist 
            elif key == "valueOptions":
                temp_key, _ = getKeyword(full_set=obj,suffix="",lang_keyword=lang_keyword,path=path)
                temp_key = temp_key.removeprefix('$').removesuffix("_")
                if lang_keyword != temp_key:
                    value = traverse(value, path + [key], temp_key)
                else:
                    value = traverse(value, lang_keyword)
            elif key == "options":
                value = traverse(value, [key], parentName)
            temp_dict[key] = traverse(value, lang_keyword)
        # Return the processed dictionary
        return temp_dict 
    elif isinstance(obj, list):
        temp_list = []
        for index, item in enumerate(obj):
            if parentName:
                # Create language keyword for option
                lang_keyword = makeLangKeyword([parentName] + path, index)
                temp_list.append(lang_keyword)
                # Store the item in mcm_lang_text with lang_keyword
                mcm_lang_text[lang_keyword] = item
                mcm_lang_key_stats[lang_keyword] = 3
            else:
                temp_list.append(traverse(item, path + [index]))
        return temp_list # Return the processed list
    return obj

def getKeyword(full_set, suffix, lang_keyword, path):
    key_set = full_set.keys()
    if "id" in key_set:
        id_good_stats = 0
        lang_keyword = makeLangKeyword([path[0], full_set["id"]], suffix)
    elif "type" in key_set:
        id_good_stats = 1
        if full_set["type"] != "text":
            if suffix:
                suffix = f"{full_set["type"]}_{suffix}"
            else:
                suffix = f"{full_set["type"]}"
        lang_keyword = makeLangKeyword(path, suffix)
    else:
        id_good_stats = 2
        lang_keyword = makeLangKeyword(lang_keyword)
    if "isplayName" in suffix:
        id_good_stats = 0
    return lang_keyword, id_good_stats

def replaceModifiedKey(obj, replace_key, path=None, ):
    """
    Traverse and process the MCM data.

    :param obj: The MCM data to be processed.
    :param path: The current traversal path, defaults to None.
    :param isOption: Flag to indicate if the current object is an option, defaults to False.
    :return: The processed MCM data.
    """
    if path is None:
        path = []
    if isinstance(obj, dict):
        temp_dict = {}
        for key, value in obj.items(): # Iterate over dictionary items
            temp_dict[key] = value
            
            if isinstance(value, str) and value in replace_key.keys():
                new_key  = replace_key[value]
                temp_dict[key] = new_key
            else:
                temp_dict[key] = replaceModifiedKey(value, replace_key, path + [key])
        return temp_dict 
    elif isinstance(obj, list):
        temp_list = []
        for index, item in enumerate(obj):
            if isinstance(item, str) and item in replace_key.keys():
                new_key  = replace_key.pop(item)
                temp_list.append(new_key)
            else:
                temp_list.append(replaceModifiedKey(item, replace_key, path + [index]))
        return temp_list # Return the processed list
    return obj


def makeLangKeyword(path, pathkey = None):
    """
    Create a language keyword from the given path and path key to make it unique.

    :param path: The current traversal path as a list.
    :param pathkey: The current key or index being processed.
    :return: A string representing the language keyword.
    """
    # Join path and pathkey with underscores and prefix with '$'
    if pathkey != None:
        return '$' + '_'.join(map(str, path + [pathkey])).replace(':','_')
    else:
        return '$' + '_'.join(map(str, path)).replace(':','_')