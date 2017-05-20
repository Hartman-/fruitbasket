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

        # create large layouts
        layout = QtGui.QVBoxLayout()

        # build warning widgets
        layout_warning = QtGui.QHBoxLayout()
        layout_warning.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label_Status = QtGui.QLabel('Root Paths Exist: True')
        self.btn_Resolve = QtGui.QPushButton('Resolve')
        self.btn_Resolve.pressed.connect(lambda: self.resolveRootPaths(path_results))
        self.btn_Resolve.setVisible(False)

        layout_warning.addWidget(self.label_Status)
        layout_warning.addWidget(self.btn_Resolve)
        layout.addLayout(layout_warning)

        # build show list
        self.list_shows = gui.HListWidget()
        self.shows = core.Environment().allShows()

        self.list_shows.addNewItems(self.shows)

        layout.addWidget(self.list_shows)

        # Build action buttons
        layout_Cmd = QtGui.QHBoxLayout()
        self.btn_Login = QtGui.QPushButton('Login')
        self.btn_Login.clicked.connect(self.parent().login)
        self.btn_AddShow = QtGui.QPushButton('Add Show')
        self.btn_AddShow.clicked.connect(self.addShow)

        layout_Cmd.addWidget(self.btn_Login)
        layout_Cmd.addWidget(self.btn_AddShow)
        layout.addLayout(layout_Cmd)

        self.setLayout(layout)

        # Temporary to enable access to core functionality
        self.tempEnv = core.Environment()
        self.tempSetup = core.Setup(self.tempEnv)

        path_results = self.tempSetup.checkRootPaths()
        self.checkPaths(path_results)

    def addShow(self):
        text, result = QtGui.QInputDialog.getText(self, 'Create New Show', 'Show:')
        if result:
            self.tempSetup.setupShow(text)
            return text

    def checkPaths(self, paths_dict):
        results = sum(paths_dict.values())
        length = len(paths_dict)

        self.label_Status.setText('Root Paths Exist: True')
        self.btn_Resolve.setVisible(False)

        if results < length:
            self.label_Status.setText('Root Paths Exist: False')
            self.btn_Resolve.setVisible(True)

    def getCurrent(self):
        curRow = self.list_shows.currentSelection()
        if curRow > -1:
            return self.shows[curRow]
        return None

    def resolveRootPaths(self, paths_dict):
        for key, value in paths_dict.iteritems():
            print key, value
            if value is False:
                title = 'Set %s Path' % key.upper()
                path = QtGui.QFileDialog.getExistingDirectory(self, str(title))
                if path:
                    self.tempSetup.setRootSetting(['paths', key], path)
                    print path
                    self.checkPaths(self.tempSetup.checkRootPaths())
                    return path
                return None


class LoggedWidget(QtGui.QWidget):
    def __init__(self, show, parent=None):
        super(LoggedWidget, self).__init__(parent)

        self.show = show
        self.env = core.Environment()
        self.setup = core.Setup(self.env)
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
        self.list_seq.currentRowChanged.connect(self.updateShots)
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

        layout_Cmd = QtGui.QHBoxLayout()
        layout_Cmd.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.btn_Logout = QtGui.QPushButton('Logout')
        self.btn_Logout.clicked.connect(self.parent().logout)
        layout_Cmd.addWidget(self.btn_Logout)

        layout.addWidget(grp_Selection)
        layout.addWidget(grp_Filters)

        wrapper.addLayout(gui.TitleLine(self.env.SHOW, self.env.currentUser()))
        wrapper.addLayout(layout)
        wrapper.addLayout(layout_Cmd)
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

    def updateSeq(self):
        self.list_seq.purgeList()
        seq = self.env.sequences()
        self.sequences = seq
        self.list_seq.addNewItems(seq)
        self.list_seq.setCurrentRow(0)
        self.updateShots(0)

    def updateShots(self, row):
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

        grp_Root = gui.GroupBox('Root Paths')
        self.item_serverPath = gui.HLineItem('Server', self.env.rootserver(), width=60, frozen=True)
        self.item_localPath = gui.HLineItem('Local', self.env.rootlocal(), width=60, frozen=True)
        self.list_Paths = gui.HLineList([self.item_serverPath, self.item_localPath])
        grp_Root.addLayout(self.list_Paths)
        wrapper.addWidget(grp_Root)

        grp_Apps = gui.GroupBox('Application Settings')
        app_layout = QtGui.QVBoxLayout()
        app_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        apps = self.env.supportedapps()
        for index, app in enumerate(apps):
            btn_app = QtGui.QPushButton(app)
            btn_app.clicked.connect(self.Button)
            app_layout.addWidget(btn_app)

        grp_Apps.addLayout(app_layout)
        wrapper.addWidget(grp_Apps)

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
        self.setWindowTitle('Settings')

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

        action_CreateShot = QtGui.QAction('&Create Shot...', self)
        action_CreateShot.setStatusTip('Create Seq/Shot')
        action_CreateShot.triggered.connect(self.openShot)

        menubar = self.menuBar()
        menu_File = menubar.addMenu('&File')

        menu_File.addAction(action_Config)
        menu_File.addAction(action_CreateShot)
        menu_File.addAction(action_Exit)

    def login(self):
        show = self.central_widget.currentWidget().getCurrent()
        if show is not None:
            logged_in_widget = LoggedWidget(show, parent=self)
            self.central_widget.addWidget(logged_in_widget)
            self.central_widget.setCurrentWidget(logged_in_widget)
            self.central_widget.currentWidget().setup.createBaseStructure()

    def logout(self):
        login_widget = self.central_widget.widget(0)
        cur_widget = self.central_widget.currentWidget()
        self.central_widget.setCurrentWidget(login_widget)
        self.central_widget.removeWidget(cur_widget)

    def openConfig(self):
        if hasattr(self.central_widget.currentWidget(), 'env'):
            modal = SettingsWindow(self.central_widget.currentWidget().env)
            returncode = modal.exec_()
            if returncode:
                print 'good'

    def openShot(self):
        if hasattr(self.central_widget.currentWidget(), 'env'):
            modal = gui.modal_CreateShot()
            retcode = modal.exec_()
            if retcode:
                values = modal.getValues()
                if values is not None:
                    self.central_widget.currentWidget().env.addShot(values[0], values[1])
                    self.central_widget.currentWidget().updateSeq()
                    self.central_widget.currentWidget().setup.createBaseStructure()

if __name__ == "__main__":

    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    mainGui = MainWindow()
    mainGui.setWindowTitle('FruitBasket LAWncher')

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
