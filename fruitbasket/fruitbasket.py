# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

if __name__ == "__main__":
    mayapy = '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/mayapy'
    imgpath = '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager'
    prevpath = '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/RIBArchivePreview.py'
    name = 'helpme'
    archivepath = '/Users/ianhartman/Documents/maya/projects/Qarnot_Project/renderman/ribarchives/helpmeRibArchiveShape.zip'

    # args = [mayapy, prevpath, imgpath, name, archivepath]
    # process = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    # e,r = process.communicate()
    # print e
    # print r

    sup = subprocess.call([
        '/Applications/Autodesk/maya2016.5/Maya.app/Contents/bin/Render',
        '-r',
        'rman',
        '-fnc',
        'name.ext',
        '-res',
        '500',
        '500',
        '-of',
        'Tiff8',
        '-im',
        'helpme',
        '-rd',
        '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/images',
        '/Users/ianhartman/Library/Preferences/Autodesk/maya/scripts/RIBArchiveManager/previewRender.ma'
    ])
