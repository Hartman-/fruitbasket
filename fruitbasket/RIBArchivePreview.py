import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import os
import shutil
import sys


def main(imgpath, imgname, archivepath):
    sys.stdout.write(str(imgpath))
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)

    mel.eval(r' setProject "{}"'.format(imgpath))

    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', str(imgname), type='string')

    cams = cmds.ls(type='camera')
    for cam in cams:
        cmds.setAttr(cam + '.rnd', 0)
    cmds.setAttr('persp.rnd', 1)

    # CREATE BLANK ARCHIVE
    cmds.select(clear=True)
    mel.eval('rmanLoadPlugin();')
    mel.eval('rmanCreateRIBArchivesCmd(0);')

    # POPULATE BLANK ARCHIVE
    mel.eval('setAttr -type "string" %s.filename "%s";' % ('RenderManArchiveShape1', str(archivepath)))

    # Return the Persp camera to its home position
    cmds.viewSet('persp', animate=True, home=True)

    # fit the view to the loaded rib archive
    cmds.viewFit('persp')
    cmds.select(clear=True)

    # cmds.setAttr('defaultRenderGlobals.ren', 'RenderMan', type='string')
    # mel.eval('setCurrentRenderer "RenderMan";')
    # # create a single frame snapshot of the archive
    # mel.eval('render -x 500 -y 500 "persp"')

    filepath = os.path.join(imgpath, 'help.ma')
    cmds.file(rename=filepath)
    cmds.file(save=True, type='mayaAscii')

    # Clean up useless folders and files
    del_paths = [os.path.join(imgpath, 'renderData'), os.path.join(imgpath, 'renderman')]
    del_file = os.path.join(imgpath, 'workspace.mel')
    for p in del_paths:
        shutil.rmtree(p)
    os.remove(del_file)


imgdir = sys.argv[1]
imgname = sys.argv[2]
archivepath = sys.argv[3]
main(imgdir, imgname, archivepath)
