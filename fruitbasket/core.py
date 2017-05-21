import getpass
import glob
from operator import itemgetter
import os
import platform
import psutil
import shutil
import sys
import subprocess

import configparser as config

'''
Name parts... 
   [SHOW]: Show
    [SEQ]: Sequence
   [SHOT]: Shot
  [STAGE]: Stage (integer)
    [TAG]: Description Tag
[VERSION]: Version (v0001, always padding 4)
   [USER]: Username
    [EXT]: File extension
Common Naming conventions...

- Working Scene file:
[SEQ]_[SHOT]_[TAG]_[STAGE]_[VERSION]_[USER].[EXT]
'''

class Setup(object):
    def __init__(self, environment):
        self.env = environment

        # self.checkRootPaths()

    def checkRootPaths(self):
        root_data = config.rootSettings()
        root_paths = root_data['paths']

        results = {}

        for key in root_paths:

            # tst_path = 'C:\\Users\\IanHartman\\Desktop\\Pipeline'
            results[key] = True
            if not os.path.isdir(root_paths[key]):
                # key_path = list(root_data[1])
                # key_path.append('paths')
                #
                # tst_path = os.path.join(tst_path, key)
                #
                # key_path.append(key)
                # config.updateJson(key_path, tst_path, resolveRef=False)
                results[key] = False

        return results

    def setRootSetting(self, set_path, value):
        key_path = ['default', 'root']
        for key in set_path:
            key_path.append(key)

        config.updateJson(key_path, value, resolveRef=False)

    def createBaseStructure(self, server=True):
        root = self.env.rootserver()
        if server is not True:
            root = self.env.rootlocal()

        show_path = os.path.join(root, self.env.SHOW)

        json_str = 'folders.%s.json' % self.env.SHOW

        data = config.readJson(json_str)
        rel_paths = config.folderPaths(data)
        for rel_path in rel_paths:
            full_path = os.path.join(show_path, rel_path)
            config.createDir(full_path)

    def setupShow(self, show):
        default_name = 'folders.default.json'
        default_path = config.fullJsonPath(default_name)

        new_name = 'folders.%s.json' % str(show).lower()
        new_path = config.fullJsonPath(new_name)

        shutil.copy(default_path, new_path)

        # Setup the show to use the default application settings
        self.setShowApps(show)

    def setShowApps(self, show, show_data=None):
        # base string, need to add application name to complete the reference
        ref_string = "#/default/apps/"

        # return the default application json data
        json_file = config.supportedApplications(keys=False, includePath=True, resolveRef=False)
        json_data = json_file[0]

        if show_data is not None and type(show_data) is dict:
            data_keys = json_data.keys()
            for data_key in data_keys:
                if data_key in show_data:
                    key_path = list(json_file[1])
                    key_path[0] = show

                    key_path.append(str(data_key))
                    for app_key in show_data[data_key]:
                        full_path = list(key_path)
                        full_path.append(app_key)

                        config.updateJson(full_path, show_data[data_key][app_key], resolveRef=False)

                else:
                    key_path = list(json_file[1])
                    key_path[0] = show

                    key_path.append(str(data_key))
                    key_path.append('$ref')

                    full_ref = ref_string + data_key

                    config.updateJson(key_path, full_ref, resolveRef=False)

        # If no unique data is passed as an argument, set app settings to reference the defaults
        else:
            data_keys = json_data.keys()
            for data_key in data_keys:
                key_path = list(json_file[1])
                key_path[0] = show

                key_path.append(str(data_key))
                key_path.append('$ref')

                full_ref = ref_string + data_key
                config.updateJson(key_path, full_ref, resolveRef=False)


class Environment(object):

    def __init__(self):
        self.SHOW = 'HONU'
        self.SEQ = 'ABC'
        self.SHOT = '010'

    def setShow(self, show):
        if show:
            self.SHOW = str(show)
            return 0
        return 1

    def setSeq(self, seq):
        if seq:
            self.SEQ = str(seq)
            return 0
        return 1

    def setShot(self, shot):
        if shot:
            self.SEQ = str(shot)
            return 0
        return 1

    def os(self):
        curos = platform.system()
        return curos.lower()

    def rootlocal(self, path=None):
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'localdir', str(path))
                return 0
            return 1

        localdir = config.rootSettings()['paths']['local']
        if not os.path.isdir(localdir):
            raise ValueError, "[%s] Local Directory does not exist." % localdir
        return localdir

    def rootserver(self, path=None):
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'serverdir', str(path))
                return 0
            return 1

        serverdir = config.rootSettings()['paths']['server']
        if not  os.path.isdir(serverdir):
            raise ValueError, "[%s] Server Directory does not exist." % serverdir
        return serverdir

    def shotdirectory(self, toserver=1, toshots=1, show=None, seq=None, shot=None):
        basepaths = [self.rootlocal(), self.rootserver()]
        subpaths = ['publish', 'shots']

        root_path = os.path.join(basepaths[toserver], show)
        sub_path = os.path.join(root_path, "_production", subpaths[toshots])

        if show is not None:
            if seq is not None:
                if shot is not None:
                    path = os.path.join(sub_path, seq, shot)
                    if not os.path.isdir(path):
                        print 'Path [%s] does not exist' % path
                        return 1
                    return path

                path = os.path.join(sub_path, seq)
                if not os.path.isdir(path):
                    print 'Path [%s] does not exist' % path
                    return 1
                return path

            path = root_path
            if not os.path.isdir(path):
                print 'Path [%s] does not exist' % path
                return 1
            return path

        path = basepaths[toserver]

        if not os.path.isdir(path):
            print "Path [%s] does not exist" % path
            return 1
        return path

    def envstr(self, var):
        key = '%s' % str(var).upper()
        return key

    def getenv(self, var):
        key = self.envstr(var)
        envvar = os.getenv(key)
        if not envvar:
            raise ValueError, "[%s] Environment Variable does not exist" % key
        return envvar

    def currentUser(self):
        return getpass.getuser()

    def runningprocess(self):
        for a in self.supportedapps():
            value = config.applicationSettings(str(a), self.SHOW)[self.os()]
            for p in psutil.process_iter():
                try:
                    if p.exe() == value:
                        print '%s [%s] @ %s' % (p.name(), p.pid, p.create_time())
                # It's going to lock the user out of most process
                except psutil.Error:
                    pass

    def supportedapps(self):
        apps = config.supportedApplications(self.SHOW)
        return apps

    def allShows(self):
        shows = config.readJson().keys()
        return shows

    def sequences(self):
        seqs = sorted(config.sequences(self.SHOW))
        return seqs

    def shots(self, seq):
        shots = sorted(config.shots(self.SHOW, seq))
        return shots

    def addShot(self, seq, shot):
        key_path = ['definitions', 'sequences', str(seq).lower(), str(shot).lower(), "$ref"]
        value = '#/definitions/shotfolders'
        json_filename = 'folders.%s.json' % str(self.SHOW).lower()
        config.updateJson(key_path, value, filename=json_filename, resolveRef=False)

    def applicationSettings(self, app):
        settings = config.applicationSettings(app, show=self.SHOW)
        return settings

    def stages(self):
        stage_str = 'stages.%s.json' % self.SHOW

        json_data = config.readJson(stage_str)
        stage_list = sorted(json_data.values(), key=itemgetter('id'))

        return stage_list


class Application(object):

    def __init__(self, env, app, uid):
        self.environment = env
        self.app = app

        self.file = None
        self.fileExists = False

        self.project = None
        self.script = None
        self.version = None

        self.arguments = {}

        self.path = config.applicationSettings(self.app, self.environment.SHOW)[self.environment.os()]
        self.pathExists = False
        if os.path.isfile(self.path):
            self.pathExists = True

        self.id = uid
        self.rids = []

    def setpath(self, path=None):
        if path is not None and os.path.isfile(path):
            self.path = path
            self.pathExists = True
            # config.setvalue(self.app.lower(), 'mac', self.path)

    def setfile(self, file=None):
        if file is not None and os.path.isfile(file):
            self.file = file
            self.fileExists = True
        else:
            print('NO FILE SIR')

    def getFile(self, stage='', tag=''):
        base_directory = self.environment.shotdirectory(show=self.environment.SHOW,
                                                        seq=self.environment.SEQ,
                                                        shot=self.environment.SHOT)

        latestFiles = []

        for file_type in self.fileTypes():
            tag_string = tag
            stage_string = stage

            if tag is not '':
                tag_string = '_%s' % tag
            if stage is not '':
                stage_string = '_%s' % stage

            searchString = '*%s%s_*%s' % (stage_string, tag_string, file_type)
            searchPath = os.path.join(base_directory, self.app)
            if self.app == 'maya':
                searchPath = os.path.join(searchPath, 'scenes')
            searchPath = os.path.join(searchPath, searchString)

            files = list(glob.iglob(searchPath))
            if files:
                latest = max(files, key=os.path.getmtime)
                latestFiles.append(latest)

        if latestFiles:
            latest = max(latestFiles, key=os.path.getmtime)
            print latest
            self.file = latest

    def setversion(self, version=None):
        if version is not None:
            self.version = version
            config.setvalue(self.app.lower(), 'version', self.version)

    def instances(self):
        for p in psutil.process_iter():
            try:
                if p.exe() == self.path:
                    env = p.environ()
                    if env.has_key('HASH'):
                        cid = env['HASH']
                        self.rids.append(int(cid))

                        seq_str = self.environment.envstr('SEQ')
                        shot_str = self.environment.envstr('SHOT')

                        print '%s [PID %s] %s %s:%s' % (p.name(), p.pid, cid, env[seq_str], env[shot_str])
                    else:
                        print '%s [PID %s] Was not assigned a hash' % (p.name(), p.pid)
            # It's going to lock the user out of most process
            except psutil.Error:
                pass

    def run(self):
        sid = self.id
        if sid not in self.rids:
            self.rids.append(sid)
        else:
            maxid = max(self.rids)
            sid = maxid + 1
            self.rids.append(sid)

        cenv = os.environ.copy()
        cenv['HASH'] = str(sid)

        show_str = self.environment.envstr('SHOW')
        cenv[show_str] = str(self.environment.SHOW)

        seq_str = self.environment.envstr('SEQ')
        cenv[seq_str] = str(self.environment.SEQ)

        shot_str = self.environment.envstr('SHOT')
        cenv[shot_str] = str(self.environment.SHOT)

        args = self.args()
        if args:
            subprocess.Popen(args, env=cenv)

    def version(self):
        if self.version is None:
            ver = config.applicationSettings(self.app, self.environment.SHOW)['version']
            if ver:
                self.version = ver
                return ver
        return self.version

    def args(self):

        self.arguments = {
            'maya': {'-file': self.file,
                     '-proj': self.project,
                     '-script': self.script},
            'nuke': {'--nukex': True,
                     '-b': True,
                     '--': self.file},
            'houdini': {'-n': self.file}
        }

        args = []

        if self.app is not None:
            if self.app.lower() in self.arguments:
                for key, value in self.arguments[self.app.lower()].iteritems():
                    if value is not None and value is not False:
                        args.append(key)

                        # Don't want to append the True value (has to be true to get this far)
                        # Want to retain the ability to turn singular flags on and off
                        if value is True:
                            continue

                        args.append(value)

        return [self.path] + args

    def fileTypes(self):
        if self.app:
            file_types = config.applicationSettings(self.app, self.environment.SHOW)['filetypes']
            if file_types:
                return file_types
            return 1
        return 1


if __name__ == "__main__":
    environment = Environment()
    setup = Setup(environment)
    setup.createBaseStructure()
    # setup.setShowApps('TESTSHOW')
    # setup.createBaseStructure(server=False)
    #
    # app_maya = Maya(environment)
    # app_maya.getFile()
    # app_maya.run()
    # app_maya.run()
    # app_hou = Application(environment, 'houdini', 1111)
    # app_hou.instances()
    # app_nuke = Nuke(environment)
    # app_nuke.run()

    # app_hou.run()

    # app_hou.setfile("W:\\SRPJ_LAW\\houdini\\texturebaking.hipnc")
    # print app_hou.args()
    # print app_nuke.args()
