import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

import os
from glob import glob

from PySide import QtCore, QtGui

from shiboken import wrapInstance

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


import subprocess


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QMainWindow)


# Load RenderMan
# mel.eval('rmanLoadPlugin;')


# Rough function to determine if it is a group
def is_group(node):
    children = cmds.listRelatives(node, c=True)
    for child in children:
        if cmds.nodeType(child) != 'transform':
            return False
    return True


def archive():
    sel = cmds.ls(selection=True, transforms=True)
    if not is_group(sel):
        print('Not a group')
        return 1

    mel.eval('rmanCreateRibArchivesOptions(0);')


def allArchives():
    projpath = cmds.workspace(q=True, rd=True)
    archivepath = os.path.join(projpath, 'renderman/ribarchives')

    search = os.path.join(archivepath, '*.zip')

    archivedict = {}
    template = {'name': '',
                'loaded': False,
                'fullpath': '',
                'relpath': ''}
    archives = sorted(glob(search))

    for i, a in enumerate(archives):
        t = template.copy()
        name = os.path.splitext(os.path.basename(a))[0]
        exists = cmds.objExists(name)

        t['name'] = name
        t['fullpath'] = cmds.workspace(en=a)  # Cleans up the full file path
        t['relpath'] = cmds.workspace(pp=a)  # Relative path to the archive file, if possible (full if not)
        t['loaded'] = exists

        archivedict[i] = t

    return archivedict


def loadArchive(adict):
    # CREATE BLANK ARCHIVE
    cmds.select(clear=True)
    mel.eval('rmanCreateRIBArchivesCmd(0);')

    name = cmds.rename(str(adict['name'] + '1'))
    shapename = cmds.listRelatives(shapes=True)[0]

    # POPULATE BLANK ARCHIVE
    path = adict['fullpath']
    mel.eval('setAttr -type "string" %s.filename "%s";' % (shapename, path))


# loadArchive(allArchives()[1])


def updateArchive(adict):
    if not adict['loaded']:
        # Return if the archive is not in the scene
        print('%s: Not in scene' % adict['name'])
        return 1

    print('updating')
    cmds.select(adict['name'])
    mel.eval('rmanCreateRIBArchivesOptions(1);')


# updateArchive(allArchives()[0])

# CREATE & WRITE ARCHIVE
# mel.eval('rmanCreateRIBArchivesOptions(0);')

# --- Only need to load this in if rman isn't loaded
# mel.eval('rmanLoadPlugin;')

# ----------------------------------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------------------------------

class ManagerWindow(MayaQWidgetDockableMixin, QtGui.QDialog):
    toolName = 'archiveManager'

    def __init__(self, parent=None):
        # Delete any previous instances that is detected. Do this before parenting self to main window!
        self.deleteInstances()

        super(self.__class__, self).__init__(parent=parent)
        self.mayaMainWindow = maya_main_window()
        self.setObjectName(self.__class__.toolName)  # Make this unique enough if using it to clear previous instance!

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('RIB Archive Manager')
        self.resize(200, 200)

        # Create a button and stuff it in a layout
        self.label = QtGui.QLabel("RIBArchive Manager")
        self.btn_refresh = QtGui.QPushButton("Refresh")
        self.btn_refresh.pressed.connect(self.updateList)

        self.list = ArchiveListWidget()

        self.list.addNewItems(allArchives())

        self.list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list.connect(self.list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                          self.list.listItemRightClicked)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.btn_refresh)
        self.mainLayout.addWidget(self.list)
        self.setLayout(self.mainLayout)

    # If it's floating or docked, this will run and delete it self when it closes.
    # You can choose not to delete it here so that you can still re-open it through the right-click menu, but do disable any callbacks/timers that will eat memory
    def dockCloseEventTriggered(self):
        self.deleteInstances()

    # Delete any instances of this class
    def deleteInstances(self):
        mayaMainWindow = maya_main_window()  # Important that it's QMainWindow, and not QWidget/QDialog

        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            if type(obj) == maya.app.general.mayaMixin.MayaQDockWidget:
                # if obj.widget().__class__ == self.__class__: # Alternatively we can check with this, but it will fail if we re-evaluate the class
                if obj.widget().objectName() == self.__class__.toolName:  # Compare object names
                    # If they share the same name then remove it
                    print 'Deleting instance {0}'.format(obj)
                    mayaMainWindow.removeDockWidget(
                        obj)  # This will remove from right-click menu, but won't actually delete it! ( still under mainWindow.children() )
                    # Delete it for good
                    obj.setParent(None)
                    obj.deleteLater()

                    # Show window with docking ability

    def run(self):
        self.show(dockable=True)

    def updateList(self):
        self.list.refreshList(allArchives())


class ArchiveListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(ArchiveListWidget, self).__init__(parent)
        pass

    def addNewItems(self, adict):
        for key, value in adict.iteritems():
            itemN = QtGui.QListWidgetItem()
            widg = ListItem(value)

            itemN.setSizeHint(widg.sizeHint())

            self.addItem(itemN)
            self.setItemWidget(itemN, widg)
        	# self.addItem("%s: %s" % (key, value['name']))

    def purgeList(self):
        self.clear()

    def refreshList(self, adict):
        print("ArchiveManager: Reloading")
        self.purgeList()
        self.addNewItems(adict)

    def listItemRightClicked(self, QPos):
        self.listMenu = QtGui.QMenu()

        menu_import = self.listMenu.addAction("Import")
        self.connect(menu_import, QtCore.SIGNAL("triggered()"), self.menuImportClicked)

        menu_update = self.listMenu.addAction("Update")
        self.connect(menu_update, QtCore.SIGNAL("triggered()"), self.menuUpdateClicked)

        menu_preview = self.listMenu.addAction("Preview")
        self.connect(menu_preview, QtCore.SIGNAL("triggered()"), self.menuPreviewClicked)

        menu_remove = self.listMenu.addAction("Remove Item")
        self.connect(menu_remove, QtCore.SIGNAL("triggered()"), self.menuRemoveClicked)

        parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def menuImportClicked(self):
        currentItemName = str(allArchives()[int(self.currentRow())]['name'])
        print('Import: %s' % currentItemName)
        loadArchive(allArchives()[int(self.currentRow())])
        self.refreshList(allArchives())

    def menuUpdateClicked(self):
        currentItemName = str(allArchives()[int(self.currentRow())]['name'])
        print('Update: %s' % currentItemName)
        updateArchive(allArchives()[int(self.currentRow())])
        self.refreshList(allArchives())

    def menuPreviewClicked(self):
        currentItemName = str(allArchives()[int(self.currentRow())]['name'])
        print('Preview: %s' % currentItemName)

        cmd = '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/mayapy'
        args = ['/Users/ianhartman/fruitbasket/fruitbasket/RIBArchivePreview.py', '/Users/ianhartman/Desktop/images']

        process = QtCore.QProcess()
        process.start(cmd, args)

        self.refreshList(allArchives())

    def menuRemoveClicked(self):
        currentItemName = str(allArchives()[int(self.currentRow())]['name'])
        print('Remove: %s' % currentItemName)
        self.refreshList(allArchives())


class ListItem(QtGui.QWidget):
    def __init__(self, adict, parent=None):
        super(ListItem, self).__init__(parent)

        archiveName = str(adict['name'].replace('RibArchiveShape', ""))
        isLoaded = False

        title = QtGui.QLabel(archiveName)
        label_count = QtGui.QLabel('Count: %s' % str(self.count(adict['fullpath'])))

        if int(label_count.text().replace("Count: ", "")) > 0:
            isLoaded = True
        label_loaded = QtGui.QLabel('Loaded: %s' % str(isLoaded))


        layout = QtGui.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(label_loaded)
        layout.addWidget(label_count)
        layout.addStretch()

        layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(layout)

    def count(self, opath):
        count = 0
        prevfile = ''
        archiveNodes = cmds.ls(type='RenderManArchive')

        for i, n in enumerate(archiveNodes):
            fnode = cmds.getAttr('%s.filename' % n)
            fpath = cmds.workspace(en=fnode)
            if opath ==  fpath:
                count += 1

        return count




myWin = ManagerWindow()
myWin.run()
