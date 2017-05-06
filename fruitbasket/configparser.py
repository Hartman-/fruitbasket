import ConfigParser
import collections
import json
import jsonschema
import jsonref
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
    return os.path.join(settingspath, 'json', filename)

# ----------------------------------------------------------------------------------------------------
# JSON FILE PARSER
# ----------------------------------------------------------------------------------------------------


# need to figure out how to use the jsonschema reference resolver
def readJson(filename='configuration.json'):
    if os.path.splitext(filename)[1] != '.json':
        filename = filename + '.json'

    file_path = fullJsonPath(filename)

    # If it doesn't exist in the correct settings/json folder
    # return without attempting to open a file that doesn't exist
    if not os.path.isfile(file_path):
        print 'JSON File [%s] does not exist.'
        return 1

    with open(file_path) as data_file:
        data = jsonref.load(data_file)
        return data

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
        newpath = os.makedirs(path)
        return newpath
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
    # config_data = readJson('folders.default.json')
    # pprint.pprint(config_data)
    print 'yeah'
