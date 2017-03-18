import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as cmds
import maya.mel as mel
import os
import sys


def main(imgpath, imgname):
    sys.stdout.write(str(imgpath))
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)

    mel.eval(r' setProject "{}"'.format(imgpath))

    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', str(imgname), type='string')

    cams = cmds.ls(type='camera')
    for cam in cams:
        cmds.setAttr(cam + '.rnd', 0)
    cmds.setAttr('persp.rnd', 1)

    cmds.polyCube()
    # Return the Persp camera to its home position
    cmds.viewSet('persp', animate=True, home=True)
    # fit the view to the loaded rib archive
    cmds.viewFit('persp')
    cmds.select(clear=True)
    # create a single frame snapshot of the archive
    # cmds.playblast(cf=path, fmt='image', fr=[1], p=100, qlt=100, wh=[500, 500], v=False)
    cmds.render('persp', xresolution=500, yresolution=500)

imgdir = sys.argv[1]
imgname = sys.argv[2]
main(imgdir, imgname)
