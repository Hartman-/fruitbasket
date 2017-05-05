import collections
import json
import os

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


# a recursive function that builds lists of folder paths
# http://stackoverflow.com/questions/18819154/python-finding-parent-keys-for-a-specific-value-in-a-nested-dictionary
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


def collapseFolderList(folder_list):
    root_path = ''

    for root_folder in folder_list:
        root_path = os.path.join(root_path, root_folder)

    return root_path


def createBaseStructure(show, basepath):
    root = openfile()
    shots = openfile('list.shots')
    shotfolders = openfile('list.folders')

    showpath = os.path.join(basepath, show)

    for rvalue in list(keypaths(root)):

        if str(rvalue[1]) == 'list.shots':
            for svalue in list(keypaths(shots)):
                for shot in svalue[1]:
                    shot_path = os.path.join(svalue[0][0], shot)
                    for shot_folder in list(keypaths(shotfolders)):
                        shot_folder_collapsed = collapseFolderList(shot_folder[0])
                        root_folder_collapsed = collapseFolderList(rvalue[0])
                        fullpath = os.path.join(showpath, root_folder_collapsed, shot_path, shot_folder_collapsed)
                        createDir(fullpath)

        else:
            root_path = ''
            for root_folder in rvalue[0]:
                root_path = os.path.join(showpath, root_path, root_folder)
            createDir(root_path)

if __name__ == "__main__":
    createBaseStructure('HONU', "C:\\Users\\imh29\\Desktop\\thurster\\server")
