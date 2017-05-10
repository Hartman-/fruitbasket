from PySide import QtGui, QtCore
import sys


class modal_ApplicationInfo(QtGui.QDialog):

    def __init__(self, appName, app_data, show='default', parent=None):
        super(modal_ApplicationInfo, self).__init__(parent)

        self.appName = appName
        self.show = show
        self.app_data = app_data

        layout = QtGui.QVBoxLayout(self)

        app_string = '[APP] %s' % self.appName
        app_name = QtGui.QLabel(app_string)
        show_string = '[SHOW] %s' % self.show
        show_name = QtGui.QLabel(show_string)

        self.info_windowsPath = HLineItem('Windows', self.app_data['windows'], inputtype='dir')
        self.info_windowsPath.searchClicked.connect(
            lambda: self.openFileBrowser(self.info_windowsPath))

        self.info_osxPath = HLineItem('OSX', self.app_data['osx'], inputtype='dir')
        self.info_osxPath.searchClicked.connect(
            lambda: self.openFileBrowser(self.info_osxPath))

        self.info_linuxPath = HLineItem('Linux', self.app_data['linux'], inputtype='dir')
        self.info_linuxPath.searchClicked.connect(
            lambda: self.openFileBrowser(self.info_linuxPath))

        self.info_version = HLineItem('Version', self.app_data['version'])

        items_info = [self.info_windowsPath,
                      self.info_osxPath,
                      self.info_linuxPath,
                      self.info_version]

        if 'subversion' in self.app_data:
            self.info_subversion = HLineItem('Subversion', self.app_data['subversion'])
            items_info.append(self.info_subversion)

        list_info = HLineList(items_info)

        btn_submit = QtGui.QPushButton('Submit')
        btn_submit.clicked.connect(self.submitClose)

        layout.addWidget(app_name)
        layout.addWidget(show_name)
        layout.addLayout(HorizLine())
        layout.addLayout(list_info)
        layout.addWidget(btn_submit)
        self.setWindowTitle('Application Settings')

    def submitClose(self):
        self.accept()

    def getValues(self):
        data = {
            "windows": self.info_windowsPath.input.text(),
            "osx": self.info_osxPath.input.text(),
            "linux": self.info_linuxPath.input.text(),
            "version": self.info_version.input.text()
        }
        if 'subversion' in self.app_data:
            data['subversion'] = self.info_subversion.input.text()

        return data

    def openFileBrowser(self, line_item):
        dialogTitle = 'Path to %s Executable' % line_item.label.text()
        startDir = line_item.input.text()

        fDialog = QtGui.QFileDialog(self)
        fpath = fDialog.getOpenFileName(self, str(dialogTitle), startDir)
        if fpath[0]:
            if fpath[0] != startDir:
                line_item.input.setText(fpath[0])


class HLineItem(QtGui.QHBoxLayout):

    searchClicked = QtCore.Signal(bool)

    def __init__(self, labeltext='PLACEHOLDER', inputtext='PLACEHOLDER', inputtype='string', parent=None):
        super(HLineItem, self).__init__(parent)

        self.label = QtGui.QLabel()
        self.label.setText(labeltext)
        self.label.setFixedWidth(105)
        self.label.setContentsMargins(0, 0, 20, 0)
        self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.addWidget(self.label)

        if inputtype == 'int' and type(int(inputtext)) is int:
            self.spinbox = QtGui.QSpinBox()
            self.spinbox.setRange(0, 9999)
            self.spinbox.setSingleStep(1)
            self.spinbox.setValue(int(inputtext))

            self.addWidget(self.spinbox)

        elif inputtype == 'list' and type(inputtext) is list:
            self.list = QtGui.QComboBox()

            for item in inputtext:
                self.list.addItem(item)

            self.addWidget(self.list)

        elif inputtype == 'btn' and type(inputtext) is str:
            self.btn = QtGui.QPushButton(inputtext)
            self.addWidget(self.btn)

        elif inputtype == 'dir' and type(inputtext) is str:
            self.btn = QtGui.QPushButton("...")
            self.btn.setFixedWidth(25)

            self.input = QtGui.QLineEdit()
            self.input.setText(inputtext)
            self.input.setToolTip(inputtext)

            self.addWidget(self.input)
            self.addWidget(self.btn)

            self.btn.pressed.connect(self.emitClicked)

        else:
            self.input = QtGui.QLineEdit()
            self.input.setText(inputtext)
            self.input.setToolTip(inputtext)
            self.addWidget(self.input)

    def emitClicked(self):
        self.searchClicked.emit(True)


class HLineList(QtGui.QVBoxLayout):
    def __init__(self, itemlist, parent=None):
        super(HLineList, self).__init__(parent)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        for lineitem in itemlist:
            self.addLayout(lineitem)


class HorizLine(QtGui.QHBoxLayout):
    def __init__(self, parent=None):
        super(HorizLine, self).__init__(parent)

        line = QtGui.QFrame()
        line.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        line.setLineWidth(1)
        line.setStyleSheet("color: #777")

        self.addWidget(line)
        self.setContentsMargins(10, 5, 10, 5)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    test_data = {
        "osx": "No/Path/Found",
        "windows": "C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\maya.exe",
        "version": "2016.5",
        "linux": "No/Path",
        "rel_scenepath": "scenes",
        "filetypes": [
            ".ma",
            ".mb"
        ]
    }

    modal = modal_ApplicationInfo('Maya', test_data, 'HONU')
    returncode = modal.exec_()
    if returncode:
        print modal.getValues()
