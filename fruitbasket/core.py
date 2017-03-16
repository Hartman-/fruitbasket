import os
import sys
import subprocess
import configparser as config


class Application(object):
    """
    Class to define individual applications
    Include funtions:
    - run
    - version / build data
    """
    def __init__(self, app=None):
        self.app = app
        self.file = None
        self.project = None
        self.script = None
        self.version = None

        self.arguments = {}

        self.path = None

    def setpath(self, path=None):
        if path is not None:
            self.path = path
            config.setvalue(self.app.lower(), 'mac', self.path)

    def setfile(self, file=None):
        if file is not None:
            self.file = file

    def setversion(self, version=None):
        if version is not None:
            self.version = version
            config.setvalue(self.app.lower(), 'version', self.version)

    def run(self):
        args = self.args()
        subprocess.Popen(args)

    def version(self):
        if self.version is None:
            self.version = config.value(self.app, 'version')

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


class Maya(Application):

    def __init__(self, parent=None):
        super(Maya, self).__init__(parent)

        self.path = config.value('maya', 'win')
        self.app = 'maya'


class Nuke(Application):

    def __init__(self, parent=None):
        super(Nuke, self).__init__(parent)

        self.path = config.value('nuke', 'win')
        self.app = 'nuke'


class Houdini(Application):

    def __init__(self, parent=None):
        super(Houdini, self).__init__(parent)

        self.path = config.value('houdini', 'win')
        self.app = 'houdini'


if __name__ == "__main__":
    # app_maya = Maya()
    # app_maya.run()
    app_hou = Houdini()
    app_nuke = Nuke()
    print app_hou.args()
    print app_nuke.args()
