# -*- coding: utf-8 -*-


import subprocess
import platform
import os
import sys

from PySide import QtGui, QtCore

import core
from ui import classes as gui


class SubLayout(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SubLayout, self).__init__(parent)

        self.env = core.Environment()

        self.label = QtGui.QLabel('[SHOW] %s' % self.env.SHOW)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainlayout = SubLayout()
        self.initUI()

    def initUI(self):

        self.setCentralWidget(self.mainlayout)
        self.show()


if __name__ == "__main__":

    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    gui.setWindowTitle('Main Window')

    sys.exit(app.exec_())

    # mayapy = '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/mayapy'
    # imgpath = '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager'
    # prevpath = '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/RIBArchivePreview.py'
    # name = 'helpme'
    # archivepath = '/Users/ianhartman/Documents/maya/projects/Qarnot_Project/renderman/ribarchives/helpmeRibArchiveShape.zip'

    # args = [mayapy, prevpath, imgpath, name, archivepath]
    # process = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    # e,r = process.communicate()
    # print e
    # print r

    # sup = subprocess.call([
    #     '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/Render',
    #     '-r',
    #     'rman',
    #     '-fnc',
    #     'name.ext',
    #     '-res',
    #     '500',
    #     '500',
    #     '-of',
    #     'Tiff8',
    #     '-im',
    #     'helpme',
    #     '-rd',
    #     '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/images',
    #     '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/previewRender.ma'
    # ])
