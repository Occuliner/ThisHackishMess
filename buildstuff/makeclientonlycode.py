"""This script traverses a directory duplicating files excluding any lines of text between 
and including the strings ##--HOST ONLY START and ##--HOST ONLY END."""

import sys, os


folder = sys.argv[1]
newFolder = "client_only_modules"
os.mkdir(newFolder)
for dirpath, dirnames, filenames in os.walk(folder):
    for eachDir in dirnames:
        os.mkdir(os.path.join(newFolder, eachDir))
    for eachFile in filenames:
        openCount = 0
        closeCount = 0
        addBool = True
        filePath = os.path.join( dirpath, eachFile )
        print filePath[len(folder):]
        newPath = os.path.join( newFolder, filePath[len(folder):] )
        fileInput = open(os.path.join(dirpath, eachFile), 'r')
        dest = open(newPath, 'w')
        resLines = []
        for eachLine in fileInput.xreadlines():
            if "##--HOST ONLY START" in eachLine:
                addBool = False
                openCount += 1
            elif "##--HOST ONLY END" in eachLine:
                addBool = True
                closeCount += 1
            elif addBool:
                resLines.append(eachLine)

        assert openCount == closeCount, "Open and Cose tag counts not equal."
            
        dest.writelines(resLines)
        dest.flush()
        dest.close()
        fileInput.close()

