import collections
import json
import os
from pprint import pprint

relpath = os.path.dirname(os.path.abspath(__file__))
settingspath = os.path.join(relpath, 'settings')

JSON_FILES = ['root.folders.json',
              'list.shots.json',
              'list.folders.json']


def fullJsonPath(filename):
    return os.path.join(settingspath, filename)


# Only necessary to update the file name, this will append the correct path to each
for i, f in enumerate(JSON_FILES):
    JSON_FILES[i] = fullJsonPath(f)


def openfile(name='root.folders'):
    if os.path.splitext(name)[1] != '.json':
        name = name + '.json'

    filepath = os.path.join(settingspath, name)

    if filepath not in JSON_FILES:
        print 'not here boss'
        return 1

    with open(filepath) as data_file:
        data = json.load(data_file)
        return data


def keypaths(nested):
    for key, value in nested.iteritems():
        if isinstance(value, collections.Mapping):
            for subkey, subvalue in keypaths(value):
                yield [key] + subkey, subvalue
        else:
            yield [key], value


if __name__ == "__main__":
    containsVariables = True
    tempContainer = {}

    for jsonfile in JSON_FILES:
        filename = os.path.splitext(os.path.basename(jsonfile))[0]
        data = openfile(name=jsonfile)
        tempContainer[filename] = data
        # for i, value in enumerate(list(keypaths(data))):
        #     print value[0]

    for key, value in tempContainer.iteritems():
        for k in list(keypaths(value)):
            templist = []
            templist += k[0]
            if str(k[1]) != '':
                for kp in list(keypaths(tempContainer[str(k[1])])):
                    newlist = templist + kp[0]
                    print newlist
