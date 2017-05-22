import ConfigParser
import collections
import json
import jsonref
from operator import itemgetter
import os

# Configuration files will always be relative to the parser file
# Instead of attemping to find the path settings/application.conf relative to the file that made the call
parserpath = os.path.dirname(os.path.abspath(__file__))
settingspath = os.path.join(parserpath, 'settings')

CONFIG_FILES = ['configuration.conf']

# Only necessary to update the file name, this will append the correct path to each
for i, f in enumerate(CONFIG_FILES):
    CONFIG_FILES[i] = os.path.join(settingspath, f)


def fullJsonPath(filename):
    """
    Returns the full path to the input json file.

    :param filename: Input file name.
    :return: String, Full path.
    """
    return os.path.join(settingspath, 'json', filename)

# ----------------------------------------------------------------------------------------------------
# JSON FILE PARSER
# ----------------------------------------------------------------------------------------------------


def readJson(filename='configuration.json', resolveReferences=True):
    """
    Reads the input json file (defaults to configuration.json) and returns the data.
    :param filename: Name of file to read.
    :param resolveReferences: Resolve json refs, defaults to True.
    :return: Return json data.
    """
    if os.path.splitext(filename)[1] != '.json':
        filename = filename + '.json'

    file_path = fullJsonPath(filename)

    # If it doesn't exist in the correct settings/json folder
    # return without attempting to open a file that doesn't exist
    if not os.path.isfile(file_path):
        print 'JSON File [%s] does not exist.'
        return 1

    with open(file_path) as data_file:
        if resolveReferences:
            data = jsonref.load(data_file)
            return data
        data = json.load(data_file)
        return data


# THANKS STACK OVERFLOW
# http://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value
def nested_set(dic, keys, value):
    """
    Sets the value in a nested dictionary, given a list path of keys.
    :param dic: Base dictionary in which to set the value.
    :param keys: Key path leading to the key to set value for.
    :param value: Value to set.
    :return: None.
    """
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def updateJson(key_path, input_data, filename='configuration.json', resolveRef=True):
    """
    Update json settings file with the input data at the location pointed to by the key path.
    :param key_path: Path of keys, ending with the key to set.
    :param input_data: Value to set.
    :param filename: File to set data for, defaults to configuration.json
    :param resolveRef: Resolve references when reading the file, defaults to True.
    :return: Edited json data.
    """
    if os.path.splitext(filename)[1] != '.json':
        filename = filename + '.json'

    file_path = fullJsonPath(filename)

    tmp_json = readJson(filename=filename, resolveReferences=resolveRef)
    nested_set(tmp_json, key_path, input_data)

    with open(file_path, "w") as json_file:
        json.dump(tmp_json, json_file, indent=4)


def applicationSettings(app, show="default", includePath=False, resolveRef=True):
    """
    Returns the settings for given application, for given show.
    :param app: The application for which to return application settings.
    :param show: The show, uses default settings by default, to return settings for.
    :param includePath: Include key path to the application data, defaults to False.
    :param resolveRef: Resolve the references when reading the json file, defaults to True.
    :return: json data of the application.
    """
    json_data = readJson(resolveReferences=resolveRef)
    data = json_data[show]['apps'][app]
    key_path = [show, 'apps', app]

    if includePath:
        return [data, key_path]
    return data


def supportedApplications(show="default", keys=True, includePath=False, resolveRef=True):
    """
    Returns the supported applications for the current show.
    :param show: (Optional) Current show, defaults to 'default'
    :param keys: Defines return type for the json data.
    :param includePath: Include key path to the application data, defaults to False.
    :param resolveRef: Resolve the references when reading the json file, defaults to True.
    :return: If keys, returns list of application names, else returns application dictionary
    """
    json_data = readJson(resolveReferences=resolveRef)
    if keys is True:
        data = json_data[show]['apps'].keys()
    else:
        data = json_data[show]['apps']

    key_path = [show, 'apps']

    if includePath:
        return [data, key_path]
    return data


def rootSettings(includePath=False, resolveRef=True):
    """
    Returns the root settings from the configuration.json file.
    :param includePath: Include key path in the return data with the application data, defaults to False.
    :param resolveRef: Resolve the references when reading the json file, defaults to True.
    :return: Json data
    """
    json_data = readJson(resolveReferences=resolveRef)
    data = json_data['default']['root']
    key_path = ['default', 'root']

    if includePath:
        return [data, key_path]
    return data


def sequences(show, resolveRef=False):
    """
    Returns the sequences for the current show.
    :param show: Define what show to get sequences for.
    :param resolveRef: Resolve the references when reading the json file, defaults to True.
    :return: Returns list of sequences.
    """
    json_filename = 'folders.%s.json' % str(show).lower()

    json_data = readJson(filename=json_filename, resolveReferences=resolveRef)
    return json_data['definitions']['sequences'].keys()


def shots(show, sequence, resolveRef=False):
    """
    Returns the shots for the current show, sequence combination.
    :param show: Define what show to get sequence/shot for.
    :param sequence: Define the sequence.
    :param resolveRef: Resolve the references when reading the json file, defaults to True.
    :return: Returns list of shots.
    """
    json_filename = 'folders.%s.json' % str(show).lower()

    json_data = readJson(filename=json_filename, resolveReferences=resolveRef)
    return json_data['definitions']['sequences'][str(sequence)].keys()

# ----------------------------------------------------------------------------------------------------
# CONF FILE PARSER
# ----------------------------------------------------------------------------------------------------

config = ConfigParser.SafeConfigParser()


def readfile(name):
    filename = name + '.conf'
    filepath = os.path.join(settingspath, filename)

    if filepath not in CONFIG_FILES:
        print 'not here boss'
        return 1

    config.read(filepath)


def value(section, option, name='configuration'):
    readfile(name)

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.get(section, option)
            return value
        else:
            print 'No Option: %s Exists' % option
            return None
    else:
        print 'No Section: %s Exists' % section
        return None


def setvalue(section, option, value, name='configuration'):
    readfile(name)

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.set(section, option, value)

            with open(CONFIG_FILES[0], 'wb') as configfile:
                config.write(configfile)

            return value
        else:
            print 'No Option: %s Exists' % option
            return None
    else:
        print 'No Section: %s Exists' % section
        return None


def get_sections(name='configuration'):
    readfile(name)
    return config.sections()


def keypaths(nested):
    for key, value in nested.iteritems():
        if isinstance(value, collections.Mapping):
            for subkey, subvalue in keypaths(value):
                yield [key] + subkey, subvalue
        else:
            yield [key], value


def createDir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        return path
    return 1


def folderPaths(json_data):
    all_paths = []
    for key_path in list(keypaths(json_data)):
        if key_path[0][0] == "definitions":
            continue

        rel_path = ''
        for folder in key_path[0]:
            rel_path = os.path.join(rel_path, folder)

        all_paths.append(rel_path)

    return all_paths

if __name__ == "__main__":
    json_data = readJson('stages.honu.json')
    print sorted(json_data.values(), key=itemgetter('id'))
