# -*- coding: utf-8 -*-
import subprocess
import platform
import os
import sys

from PySide import QtGui, QtCore

import core
from ui import classes as gui


class LoginShowWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginShowWidget, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        self.button = QtGui.QPushButton('Login')

        self.list_shows = gui.ShowListWidget()
        self.shows = core.Environment().allShows()

        self.list_shows.addNewItems(self.shows)

        layout.addWidget(self.button)
        layout.addWidget(self.list_shows)

        self.setLayout(layout)
        self.button.clicked.connect(self.parent().login)
        # you might want to do self.button.click.connect(self.parent().login) here

    def getCurrent(self):
        curRow = self.list_shows.currentSelection()
        if curRow > -1:
            return self.shows[curRow]
        return None


class LoggedWidget(QtGui.QWidget):
    def __init__(self, show, parent=None):
        super(LoggedWidget, self).__init__(parent)

        self.show = show
        self.env = core.Environment()
        self.env.setShow(self.show)

        layout = QtGui.QHBoxLayout()

        sel_layout = QtGui.QVBoxLayout()
        sel_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.label = QtGui.QLabel('[SHOW] %s' % self.show)
        sel_layout.addWidget(self.label)

        app_layout = QtGui.QVBoxLayout()
        app_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        label_Apps = QtGui.QLabel('Application Settings:')
        app_layout.addWidget(label_Apps)

        apps = self.env.supportedapps()
        for index, app in enumerate(apps):
            btn_app = QtGui.QPushButton(app)
            btn_app.clicked.connect(self.Button)
            app_layout.addWidget(btn_app)


        layout.addLayout(sel_layout)
        layout.addLayout(app_layout)
        self.setLayout(layout)

    def Button(self):
        sender = self.sender()
        settings = self.env.applicationSettings(sender.text())

        modal = gui.modal_ApplicationInfo(sender.text(), settings, self.env.SHOW)
        returncode = modal.exec_()
        if returncode:
            print modal.getValues()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        login_widget = LoginShowWidget(self)
        self.central_widget.addWidget(login_widget)

        # Open the window upon instantiation
        self.show()

    def login(self):
        show = self.central_widget.currentWidget().getCurrent()
        if show is not None:
            logged_in_widget = LoggedWidget(show)
            self.central_widget.addWidget(logged_in_widget)
            self.central_widget.setCurrentWidget(logged_in_widget)


if __name__ == "__main__":

    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    mainGui = MainWindow()
    mainGui.setWindowTitle('Main Window')

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
