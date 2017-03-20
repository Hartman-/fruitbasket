# -*- coding: utf-8 -*-

import os
import sys
import subprocess

if __name__ == "__main__":
    mayapy = 'C:\\Program Files\\Autodesk\\Maya2016.5\\bin\\mayapy.exe'
    imgpath = 'C:/Users/imh29/Desktop/preview'
    prevpath = 'C:\\Users\\imh29\\fruitbasket\\fruitbasket\\RIBArchivePreview.py'
    name = 'eag'
    archivepath = 'C:/Users/imh29/Desktop/RIBArchive_tools/renderman/ribarchives/eagRibArchiveShape.zip'

    args = [mayapy, prevpath, imgpath, name, archivepath]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    e,r = process.communicate()
    print e
