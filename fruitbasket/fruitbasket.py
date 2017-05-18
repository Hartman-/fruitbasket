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

        self.list_shows = gui.HListWidget()
        self.shows = core.Environment().allShows()

        self.list_shows.addNewItems(self.shows)

        layout.addWidget(self.button)
        layout.addWidget(self.list_shows)

        self.setLayout(layout)
        self.button.clicked.connect(self.parent().login)

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

        self.sequences = self.env.sequences()
        self.shots = self.env.shots(self.sequences[0])

        wrapper = QtGui.QVBoxLayout()
        layout = QtGui.QHBoxLayout()

        grp_Selection = gui.GroupBox('Shot Select')
        sel_wrapper = QtGui.QVBoxLayout()

        sel_layout = QtGui.QHBoxLayout()
        sel_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.list_seq = gui.HListWidget()
        self.list_seq.addNewItems(self.sequences)
        self.list_seq.setCurrentRow(0)
        self.list_seq.currentRowChanged.connect(self.update)
        sel_layout.addWidget(self.list_seq)

        self.list_shot = gui.HListWidget()
        self.list_shot.addNewItems(self.shots)
        self.list_shot.setCurrentRow(0)
        sel_layout.addWidget(self.list_shot)

        sel_wrapper.addLayout(sel_layout)
        self.btn_launch = QtGui.QPushButton('Launch')
        self.btn_launch.clicked.connect(self.currentShot)
        sel_wrapper.addWidget(self.btn_launch)

        grp_Selection.addLayout(sel_wrapper)

        grp_Filters = gui.GroupBox('Filters')
        filter_wrapper = QtGui.QVBoxLayout()

        self.chk_UseUsername = QtGui.QCheckBox('Username')
        filter_wrapper.addWidget(self.chk_UseUsername)

        self.filter_stages = gui.HLineItem('Stage', ['dicks', 'booty'], inputtype='list', width=40)
        self.filter_tags = gui.HLineItem('Tag', ['dicks', 'titssobigthatyoumamadied'], inputtype='list', width=40)

        self.list_filters = gui.HLineList([self.filter_stages, self.filter_tags])
        filter_wrapper.addLayout(self.list_filters)

        grp_Filters.addLayout(filter_wrapper)

        layout.addWidget(grp_Selection)
        layout.addWidget(grp_Filters)

        wrapper.addLayout(gui.TitleLine(self.env.SHOW, self.env.currentUser()))
        wrapper.addLayout(layout)
        self.setLayout(wrapper)

    def currentShot(self):
        curSeq = self.list_seq.currentSelection()
        curShot = self.list_shot.currentSelection()
        if curSeq > -1:
            seq = self.sequences[curSeq]
            if curShot > -1:
                shot = self.shots[curShot]
                print '%s-%s' % (seq, shot)
                # return [seq, shot]
            # return [seq, None]
        # return [None, None]

    def update(self, row):
        self.list_shot.purgeList()
        shots = self.env.shots(self.sequences[row])
        self.shots = shots
        self.list_shot.addNewItems(shots)
        self.list_shot.setCurrentRow(0)


class SettingsWindow(QtGui.QDialog):
    def __init__(self, env, parent=None):
        super(SettingsWindow, self).__init__(parent)

        self.env = env

        wrapper = QtGui.QVBoxLayout()

        app_layout = QtGui.QVBoxLayout()
        app_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        label_Apps = QtGui.QLabel('Application Settings:')
        app_layout.addWidget(label_Apps)

        apps = self.env.supportedapps()
        for index, app in enumerate(apps):
            btn_app = QtGui.QPushButton(app)
            btn_app.clicked.connect(self.Button)
            app_layout.addWidget(btn_app)

        wrapper.addLayout(app_layout)

        layout_Cmd = QtGui.QHBoxLayout()
        layout_Cmd.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.btn_Accept = QtGui.QPushButton('Ok')
        self.btn_Cancel = QtGui.QPushButton('Cancel')

        self.btn_Accept.pressed.connect(self.submitClose)
        # Close & toss changes
        self.btn_Cancel.pressed.connect(self.close)

        layout_Cmd.addWidget(self.btn_Accept)
        layout_Cmd.addWidget(self.btn_Cancel)

        wrapper.addLayout(layout_Cmd)
        self.setLayout(wrapper)

    def submitClose(self):
        self.accept()

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

        self.initMenuBar()

        # Open the window upon instantiation
        self.show()

    def initMenuBar(self):
        action_Exit = QtGui.QAction('&Exit', self)
        action_Exit.setShortcut('Ctrl-Q')
        action_Exit.setStatusTip('Exit Fruitbasket')
        action_Exit.triggered.connect(self.close)

        action_Config = QtGui.QAction('&Settings...', self)
        action_Config.setStatusTip('Manage Config of Fruitbasket')
        action_Config.triggered.connect(self.openConfig)

        menubar = self.menuBar()
        menu_File = menubar.addMenu('&File')

        menu_File.addAction(action_Config)
        menu_File.addAction(action_Exit)

    def login(self):
        show = self.central_widget.currentWidget().getCurrent()
        if show is not None:
            logged_in_widget = LoggedWidget(show)
            self.central_widget.addWidget(logged_in_widget)
            self.central_widget.setCurrentWidget(logged_in_widget)

    def openConfig(self):
        if hasattr(self.central_widget.currentWidget(), 'env'):
            modal = SettingsWindow(self.central_widget.currentWidget().env)
            returncode = modal.exec_()
            if returncode:
                print 'good'

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
