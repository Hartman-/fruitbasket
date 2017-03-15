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
    def __init__(self, app=None, path=None):
        self.app = app
        self.file = None
        self.project = None
        self.script = 0

        self.arguments = {}

        self.path = None
        self.setpath(path)

    def setpath(self, path=None):
        if path is not None:
            self.path = path

    def setfile(self, file=None):
        if file is not None:
            self.file = file

    def run(self):
        args = [self.path] + self.args()
        print args
        subprocess.Popen(args)

    def version(self):
        pass

    def args(self):

        self.arguments = {
            'maya': {'-file': self.file,
                     '-proj': self.project,
                     '-script': self.script},
            'nuke': {'--nukex': self.file}
        }

        args = []

        if self.app is not None:
            if self.app.lower() in self.arguments:
                for key, value in self.arguments[self.app.lower()].iteritems():
                    if value is not None:
                        args.append(key)
                        args.append(value)

        return args


class Maya(Application):

    def __init__(self, parent=None):
        super(Maya, self).__init__(parent)
        self.path = config.value('maya', 'win')


class Nuke(Application):

    def __init__(self, parent=None):
        super(Nuke, self).__init__(parent)
        self.path = config.value('nuke', 'win')


class Houdini(Application):

    def __init__(self, parent=None):
        super(Houdini, self).__init__(parent)
        self.path = config.value('houdini', 'win')


if __name__ == "__main__":
    app_maya = Application(app='Maya')
    app_maya.setpath("C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\maya.exe")
    app_maya.setfile("C:\\Users\\IanHartman\\Desktop\\shaderbuilder.ma")
    app_maya.run()
