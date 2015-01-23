import os
import maya.cmds as mc

from tools import fileUtils
reload(fileUtils)

from ptCacheTools import importCache
reload(importCache)

def run() : 
	
	


	# check if any PO node in the scene
	PONodes = mc.ls(type = 'PO_Reader')

	# getList of PO node version

	if PONodes : 
		lists = getPONodeVersion(PONodes)
		maxVersion = getPublishVersion()

		if len(lists) == 1 : 
			if lists[0] == maxVersion : 
				print 'Cache version matched %s' % lists[0]

			else : 
				mayaUpdateDialog()

		else : 
			mayaUpdateDialog()

		
def getPublishVersion() : 

	myApp = importCache.cmd()
	info = myApp.info()
	maxVersion = None

	cPath = info['heroCachePath']

	if os.path.exists(cPath) : 
		dirs = fileUtils.listFolder(cPath)
		
		if dirs : 
			maxVersion = sorted(dirs)[-1]

	return maxVersion


def getPONodeVersion(PONodes) : 
	myApp = importCache.cmd()
	info = myApp.info()
	listVersions = []

	cPath = info['heroCachePath']

	for each in PONodes : 
		path = mc.getAttr('%s.FilePath' % each)

		version = path.replace('%s/' % cPath, '').split('/')[0]

		if not version in listVersions : 
			listVersions.append(version)

	return listVersions

def mayaUpdateDialog() : 
	result = mc.confirmDialog( title='Cache need update', 
						message='Cache need update to the latest version', 
						button=['Update','Update Later'], 
						defaultButton='Update', 
						cancelButton='Update Later', 
						dismissString='Update Later' )

	if result == 'Update' : 
		
		if mc.window('ImportCacheWindow', exists = True) : 
			mc.deleteUI('ImportCacheWindow')

		myApp = importCache.MyForm(importCache.getMayaWindow())
		myApp.show()