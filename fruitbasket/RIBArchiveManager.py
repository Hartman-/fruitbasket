import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

import os
from glob import glob

from PySide import QtCore, QtGui

from shiboken import wrapInstance

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


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
        # self.deleteInstances()

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

        self.select_size = QtGui.QComboBox()
        self.select_size.addItem('Small Icon')
        self.select_size.addItem('Medium Icon')
        self.select_size.addItem('Large Icon')
        self.select_size.addItem('Extra Large Icon')

        self.list = ArchiveListWidget()

        self.list.addNewItems(allArchives())

        self.list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list.connect(self.list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                          self.list.listItemRightClicked)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.select_size)
        self.mainLayout.addWidget(self.btn_refresh)
        self.mainLayout.addWidget(self.list)
        self.setLayout(self.mainLayout)

    '''
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
    '''
    def run(self):
        self.show(dockable=True)

    def updateList(self):
        self.list.refreshList(allArchives(), self.select_size.currentIndex())


class ArchiveListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(ArchiveListWidget, self).__init__(parent)
        self.currentimgsize = 0

    def addNewItems(self, adict, isize=0):
        if isize != self.currentimgsize:
            self.currentimgsize = isize

        for key, value in adict.iteritems():
            itemN = QtGui.QListWidgetItem()
            widg = ListItem(value, isize=self.currentimgsize)

            itemN.setSizeHint(widg.sizeHint())

            self.addItem(itemN)
            self.setItemWidget(itemN, widg)

    def purgeList(self):
        self.clear()

    def refreshList(self, adict, isize=None):
        print("ArchiveManager: Reloading")

        imgsize = 0
        if isize != self.currentimgsize:
            imgsize = isize
        else:
            imgsize = self.currentimgsize

        self.purgeList()
        self.addNewItems(adict, isize=int(imgsize))

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

        # store the images relative to the location of the file
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        rel_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RIBArchivePreview.py')

        archive_path = allArchives()[int(self.currentRow())]['fullpath']

        app_path = '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/mayapy'
        exe_path = 'C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\mayapy.exe'

        cmd = exe_path
        args = [rel_path,
                dir_path,
                currentItemName.replace('RibArchiveShape', ""),
                archive_path]
        process = QtCore.QProcess(self)
        process.start(cmd, args)
        process.waitForFinished()
        print(process.readAll())

        process.finished.connect(self.postPreview)

    def menuRemoveClicked(self):
        currentItemName = str(allArchives()[int(self.currentRow())]['name'])
        print('Remove: %s' % currentItemName)
        self.refreshList(allArchives())

    def postPreview(self):
        self.refreshList(allArchives())


class ListItem(QtGui.QWidget):
    def __init__(self, adict, isize, parent=None):
        super(ListItem, self).__init__(parent)

        # Image sizes
        width = [25, 50, 100, 200]

        archiveName = str(adict['name'].replace('RibArchiveShape', ""))
        isLoaded = False

        title = QtGui.QLabel(archiveName)
        label_count = QtGui.QLabel('Count: %s' % str(self.count(adict['fullpath'])))

        self.img_path = self.findmap(adict['name'].replace('RibArchiveShape', ''))

        self.label_img = QtGui.QLabel()
        self.pixmap = QtGui.QPixmap(self.img_path)
        self.pixmap = self.pixmap.scaled(width[isize], width[isize], QtCore.Qt.KeepAspectRatio)
        self.label_img.setPixmap(self.pixmap)

        if int(label_count.text().replace("Count: ", "")) > 0:
            isLoaded = True
        label_loaded = QtGui.QLabel('Loaded: %s' % str(isLoaded))

        wrapper = QtGui.QHBoxLayout()
        wrapper.setAlignment(QtCore.Qt.AlignLeft)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(label_loaded)
        layout.addWidget(label_count)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        wrapper.addWidget(self.label_img)
        wrapper.addLayout(layout)

        layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(wrapper)

    def count(self, opath):
        count = 0
        archiveNodes = cmds.ls(type='RenderManArchive')

        for i, n in enumerate(archiveNodes):
            fnode = cmds.getAttr('%s.filename' % n)
            fpath = cmds.workspace(en=fnode)
            if opath ==  fpath:
                count += 1

        return count

    def findmap(self, name):
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
        search = os.path.join(base_path, '*.tif')
        images = sorted(glob(search))
        for i, img in enumerate(images):
            filename = os.path.basename(img)
            if filename == name+'.tif':
                return img
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/placeholder.jpg')


def main():
    myWin = ManagerWindow()
    myWin.run()
