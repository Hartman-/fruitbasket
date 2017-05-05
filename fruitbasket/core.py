import glob
import os
import platform
import psutil
import sys
import subprocess

import configparser as config
import folderbuild

'''
- Simply pass the env variables in a list with the Popen

thinking about structuring the pipe as a Proj in PROJ

SHOW
    > _production
        > DELIVERABLES
        > HOUDINI
        > NUKE
        > EDIT
        > SHOTS
            > SEQ
                > SHOT
                    > NUKE
                    > HOUDINI
                    > MAYA
                        > When the user saves, give them the option of stage (layout, anim, lighting, render, etc)
                        > Two tag system, one denotes the stage (integer value, pulled from defintions file), other identifies contents (ex. ABC_010_anim_blockIn_v0001_imh29.ma
        > SOURCE
            > PLATES
            > ELEMENTS
        > LIBRARY
            > CATEGORIES
        > PUBLISHED
            > SEQ
                > SHOT
                    > NUKE
                    > HOUDINI
                    > MAYA
    > OTHER
'''


class Setup(object):
    def __init__(self, environment):
        self.env = environment

    def createBaseStructure(self, server=True):
        root = environment.rootserver()
        if server is not True:
            root = environment.rootlocal()

        folderbuild.createBaseStructure(self.env.SHOW, root)


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
        print curos
        return curos

    def rootlocal(self, path=None):
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'localdir', str(path))
                return 0
            return 1

        localdir = config.value('root', 'localdir')
        if not os.path.isdir(localdir):
            raise ValueError, "[%s] Local Directory does not exist." % localdir
        return localdir

    def rootserver(self, path=None):
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'serverdir', str(path))
                return 0
            return 1

        serverdir = config.value('root', 'serverdir')
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

    def runningprocess(self):
        for a in self.supportedapps():
            value = config.value(str(a), 'win')
            for p in psutil.process_iter():
                try:
                    if p.exe() == value:
                        print '%s [%s] @ %s' % (p.name(), p.pid, p.create_time())
                # It's going to lock the user out of most process
                except psutil.Error:
                    pass

    def supportedapps(self):
        apps = config.get_sections()
        return apps


class Application(object):

    def __init__(self, env):
        self.app = None

        self.file = None
        self.fileExists = False

        self.project = None
        self.script = None
        self.version = None

        self.arguments = {}

        self.path = None
        self.pathExists = False

        self.id = 0000
        self.rids = []

        self.environment = env

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
        base_directory = environment.shotdirectory(show=environment.SHOW, seq=environment.SEQ, shot=environment.SHOT)

        latestFiles = []

        for file_type in self.filetypes():
            tag_string = tag
            stage_string = stage

            if tag is not '':
                tag_string = '_%s' % tag
            if stage is not '':
                stage_string = '_%s' % stage

            searchString = '*%s%s_*%s' % (stage_string, tag_string, file_type)
            searchPath = os.path.join(base_directory, self.app, searchString)
            print searchPath

            files = list(glob.iglob(searchPath))
            if files:
                latest = max(files, key=os.path.getmtime)
                latestFiles.append(latest)

        if latestFiles:
            latest = max(latestFiles, key=os.path.getmtime)
            print latest

    def setversion(self, version=None):
        if version is not None:
            self.version = version
            config.setvalue(self.app.lower(), 'version', self.version)

    def instances(self):
        value = config.value(str(self.app), 'win')
        for p in psutil.process_iter():
            try:
                if p.exe() == value:
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
        print sid
        cenv['HASH'] = str(sid)

        show_str = self.environment.envstr('SHOW')
        cenv[show_str] = self.environment.SHOW

        seq_str = self.environment.envstr('SEQ')
        cenv[seq_str] = self.environment.SEQ

        shot_str = self.environment.envstr('SHOT')
        cenv[shot_str] = self.environment.SHOT

        args = self.args()
        if args:
            subprocess.Popen(args, env=cenv)

    def version(self):
        if self.version is None:
            ver = config.value(self.app, 'version')
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

    def filetypes(self):
        if self.app:
            files = config.value(self.app, 'types')
            if files:
                filearray = files.split(';')
                return filearray
            return 1
        return 1

    def test(self):
        print self.environment.SHOW


class Maya(Application):

    def __init__(self, env):
        super(Maya, self).__init__(env)

        self.app = 'maya'
        self.path = config.value(self.app, 'win')

        self.id = 1111

        self.instances()


class Nuke(Application):

    def __init__(self, env):
        super(Nuke, self).__init__(env)

        self.app = 'nuke'
        self.path = config.value(self.app, 'win')

        self.id = 2222

        self.instances()


class Houdini(Application):

    def __init__(self, env):
        super(Houdini, self).__init__(env)

        self.app = 'houdini'
        self.path = config.value(self.app, 'win')

        self.id = 3333

        self.instances()


if __name__ == "__main__":
    environment = Environment()

    setup = Setup(environment)

    app_maya = Maya(environment)
    app_maya.getFile()
    # app_maya.run()
    # app_maya.run()
    app_hou = Houdini(environment)
    app_nuke = Nuke(environment)
    # app_nuke.run()

    # app_hou.run()

    # app_hou.setfile("W:\\SRPJ_LAW\\houdini\\texturebaking.hipnc")
    # print app_hou.args()
    # print app_nuke.args()
