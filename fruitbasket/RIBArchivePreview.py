import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import os
import platform
import shutil
import sys
import subprocess


def renderpath():
    osdict = {'windows': 'C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\Render.exe',
              'darwin': '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/Render',
              'linux': '/usr/autodesk/maya20116.5-x64/bin/render'}
    curos = platform.system().lower()
    return osdict[curos]


def main(imgpath, imgname, archivepath):
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)

    mel.eval(r' setProject "{}"'.format(imgpath.replace('\\', '\\\\')))
    cmds.loadPlugin('RenderMan_for_Maya.mll', quiet=True)

    cmds.setAttr('defaultRenderGlobals.currentRenderer', l=False)
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'renderManRIS', type='string')

    # if cmds.window('unifiedRenderGlobalsWindow', exists=True):
    #     cmds.deleteUI('unifiedRenderGlobalsWindow')
    #
    # mel.eval('unifiedRenderGlobalsWindow')
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', str(imgname), type='string')
    cmds.setAttr('defaultResolution.width', 500)
    cmds.setAttr('defaultResolution.height', 500)

    # CREATE BLANK ARCHIVE
    cmds.select(clear=True)
    mel.eval('rmanCreateRIBArchivesCmd(0);')

    # POPULATE BLANK ARCHIVE
    mel.eval('setAttr -type "string" %s.filename "%s";' % ('RenderManArchiveShape1', str(archivepath)))

    bbox = cmds.xform(q=True, bb=True)

    xsize = bbox[3] - bbox[0]
    ysize = bbox[4] - bbox[1]
    zsize = bbox[5] - bbox[2]

    maxside = max(xsize, ysize, zsize)

    cmds.xform(cp=True)
    pivot = cmds.xform(q=True, ws=True, rp=True)

    camName = cmds.camera()
    camShape = camName[1]

    orthopos = maxside * 1.5

    cmds.viewPlace(camShape, eye=(orthopos, orthopos, orthopos))
    cmds.viewPlace(camShape, la=pivot)

    cmds.select('RenderManArchive1')
    cmds.viewFit('camera1')

    cmds.select(clear=True)

    cams = cmds.ls(type='camera')
    for cam in cams:
        cmds.setAttr(cam + '.rnd', 0)
    cmds.setAttr('camera1.rnd', 1)

    # # create a single frame snapshot of the archive
    # mel.eval('render -x 500 -y 500 "camera1"')

    filepath = os.path.join(imgpath, 'previewRender.ma').replace('\\', '\\\\')
    cmds.file(rename=filepath)
    cmds.file(save=True, type='mayaAscii')

    subprocess.call('"%s" -renderer rman -fnc name.ext -res 500 500 -of Tiff8 -im %s -rd "%s" "%s"' % (renderpath(), imgname, os.path.join(imgpath, 'images'), filepath))

    # Clean up useless folders and files
    os.path.join(imgpath, 'renderData'),
    del_paths = [os.path.join(imgpath, 'renderman')]
    del_files = [os.path.join(imgpath, 'workspace.mel'), os.path.join(imgpath, 'previewRender.ma')]
    for p in del_paths:
        shutil.rmtree(p)
    for f in del_files:
        os.remove(f)


imgdir = sys.argv[1]
imgname = sys.argv[2]
archivepath = sys.argv[3]
main(imgdir, imgname, archivepath)
