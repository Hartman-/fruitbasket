import json
import os
from pprint import pprint

relpath = os.path.dirname(os.path.abspath(__file__))
settingspath = os.path.join(relpath, 'settings')

JSON_FILES = ['configuration.json',
              'stages.json']

# Only necessary to update the file name, this will append the correct path to each
for i, f in enumerate(JSON_FILES):
    JSON_FILES[i] = os.path.join(settingspath, f)


def openfile(name='configuration'):
    filename = name + '.json'
    filepath = os.path.join(settingspath, filename)

    if filepath not in JSON_FILES:
        print 'not here boss'
        return 1

    with open(filepath) as data_file:
        data = json.load(data_file)
        return data


if __name__ == "__main__":
    data = openfile()
    pprint(data)
