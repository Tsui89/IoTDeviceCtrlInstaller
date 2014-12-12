__author__ = 'IBM-cuiwc'

import os
import shutil

import globalvalue

def CleanLogFile():
    path = os.getcwd()
    workdir = path + os.path.sep + globalvalue.LogPath
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    print 'clean log'

def EnviromentClean():
    CleanLogFile()