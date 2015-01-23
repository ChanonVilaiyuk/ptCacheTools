import os, sys
import maya.mel as mm
import maya.cmds as mc

from tools import fileUtils
reload(fileUtils)

# run from modifying poCreateUI


# source "O:/systemTools/mel/poCreateUI.mel"
mm.eval('source "poCreateUI"')

def cacheCmd(dst) : 
	if not os.path.exists(dst) : 
		os.makedirs(dst)

	mm.eval('POBAKECmd("%s")' % dst)

def organizeCacheFile(src, dst) : 
	print src, dst

def getAsset() : 
	# get asset by collecting selected namespaces

	objs = mc.ls(sl = True)
	namespaces = []

	for each in objs : 
		if ':' in each : 
			ns = each.split(':')[0]
			if not ns in namespaces : 
				namespaces.append(ns)

	return namespaces

# def exportAssetDB(file, data) : 
# 	if not os.path.exists(file) : 
# 		fileUtils.createFile(file)

# 	fileUtils.writeFile(file, data)