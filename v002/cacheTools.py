from functools import partial
import maya.cmds as mc
import maya.mel as mm

import os
import subprocess

def batchExport(file, arg = None) : 
	
	currentFile = file.replace('/', '\\')
	mayaCmd = 'removeRig();'
	cmd = '"C:/Program Files/Autodesk/Maya2012/bin/mayabatch.exe" -file %s -command "%s"' % (currentFile,mayaCmd)
	cmdRep = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]

	print cmdRep

class addAttributeCache() : 
	def __init__(self) : 
		self.show()

	def show(self) : 
		if mc.window('cWin', exists = True) : 
			mc.deleteUI('cWin')
			
		mc.window('cWin', t = 'Add Cache')
		mc.columnLayout(adj = 1,rs = 3)
		mc.button(l = 'Add Cache Attribute', h = 30, c = partial(self.addCache))
		mc.button(l = 'Set Cache On', h = 30, c = partial(self.setOn))
		mc.button(l = 'Set Cache Off', h = 30, c = partial(self.setOff))
		mc.showWindow()
		mc.window('cWin', e = True, wh = [140, 100])
		
		
	def addCache(self, arg = None) : 
		objs = mc.ls(sl = True)
		
		for each in objs : 
			if not mc.objExists('%s.cache' % each) : 
				mc.addAttr(each, ln = 'cache', at = 'bool')
				mc.setAttr('%s.cache' % each, 1, e = True, keyable = True)			

	def setOn(self, arg = None) : 
		objs = mc.ls(sl = True)
		
		for each in objs : 
			if mc.objExists('%s.cache' % each) : 
				mc.setAttr('%s.cache' % each, 1)	
				
	def setOff(self, arg = None) : 
		objs = mc.ls(sl = True)
		
		for each in objs : 
			if mc.objExists('%s.cache' % each) : 
				mc.setAttr('%s.cache' % each, 0)



class exportCacheVersion() : 
	def __init__(self) : 
		self.win = 'exportCache'
		self.ui = '%s_win' % self.win

		self.rootGrp = 'SuperRoot_Grp'
		# self.show()

	def show(self) : 
		if mc.window(self.ui, exists = True) : 
			mc.deleteUI(self.ui)
			
		mc.window(self.ui, t = 'Add Cache')
		mc.columnLayout(adj = 1,rs = 3)
		mc.rowColumnLayout(nc = 2, cw = ([1, 50], [2, 100]), cs = ([2, 4]))

		mc.text(l = 'Asset : ', font = 'smallBoldLabelFont', al = 'left')
		mc.text('%s_lb' % self.win, l = '-', al = 'left')

		mc.setParent('..')

		mc.button(l = 'Export', h = 30, c = partial(self.doExportCacheVersion))
		mc.button(l = 'Rivet', h = 30, c = partial(self.runRivet))
		mc.showWindow()
		mc.window(self.ui, e = True, wh = [200, 83])

		self.getAssetName()

	def doExportCacheVersion(self, arg = None) : 
		currentFile = mc.file(q = True, sn = True)

		basePath = currentFile.replace('/%s' % os.path.basename(currentFile), '')
		basename = os.path.basename(currentFile) 
		if 'Render' in basename : 
			cacheFileName = os.path.basename(currentFile).replace('Render', 'Cache')

			saveFile = '%s/%s' % (basePath, cacheFileName)

			# delete constraint
			geo = mc.listRelatives('Geo_Grp', ad = True, f = True)
			mc.delete(geo, constraints = True)

			# delete history Geo_Grp
			geo = mc.listRelatives('Geo_Grp', ad = True, f = True)
			mc.delete(geo, ch = True)

			# delete Rig
			objs = mc.listRelatives(self.rootGrp, ad = True, f = True)
			mc.lockNode(objs, l = False)
			mc.delete(self.rootGrp)

			# freeze tranformation geo grp
			mc.select('Geo_Grp', hi = True)
			geo = mc.ls(sl = True)
			mc.makeIdentity(geo, apply = True)
			mc.select(cl = True)

			# save file
			mc.file( rename=saveFile )
			mc.file( save=True, type='mayaBinary' )

			mm.eval('print "Done";')

		else : 
			print 'This is not a Render version'


	def getAssetName(self) : 
		assetName = str()
		if mc.objExists('Rig_Grp.assetName') : 
			assetName = mc.getAttr('Rig_Grp.assetName')

		else : 
			assetName = mc.getAttr('Rig:Rig_Grp.assetName')

		mc.text('%s_lb' % self.win, e = True, l = assetName)



	def runRivet(self, arg = None) : 
		mm.eval('source "Y:/USERS/Peck/mel/rivetUI.mel";')


	def exportCacheFromCurrentFile(self) : 
		# find Geo_Grp
		geoGrp = 'Geo_Grp'
		tmpGrp = 'Geo_Grp_temp'
		lightGrp = 'Light_Grp'

		currentFile = mc.file(q = True, sn = True)
		dst = self.getRefPath()

		if geoGrp : 

			if mc.objExists(geoGrp) : 
				mc.select(cl = True)

				mc.rename(geoGrp, tmpGrp)


				duplicatedObj = mc.duplicate(tmpGrp)

				mc.rename(duplicatedObj[0], geoGrp)

				# cache cleanup
				result = self.geoCleanup(geoGrp)

				if result : 
					if os.path.exists(dst.replace(os.path.basename(dst), '')) : 
						mc.select(geoGrp, lightGrp)
						mc.file(dst, force = True, options = "v=0", typ = "mayaBinary", es = True)

						mc.select(cl = True)

					else : 
						print 'Path does not exists'

				else : 
					print 'Clean up failed'


				mc.delete(geoGrp)
				mc.rename(tmpGrp, geoGrp)

				return True


	def geoCleanup(self, geoGrp) : 
		# delete constraint
		geo = mc.listRelatives(geoGrp, ad = True, f = True)
		mc.delete(geo, constraints = True)

		# delete history Geo_Grp
		geo = mc.listRelatives('Geo_Grp', ad = True, f = True)
		mc.delete(geo, ch = True)


		# freeze tranformation geo grp
		mc.select('Geo_Grp', hi = True)
		unlockTransform(mc.ls(sl = True))
		geo = mc.ls(sl = True)
		mc.makeIdentity(geo, apply = True)



		mc.select(cl = True)

		return True


	def getRefPath(self) : 
		currentFile = mc.file(q = True, sn = True)
		# P:/Lego_Template/asset/3D/character/main/frd_emmaJuicebar/rig/maya/work/frd_emmaJuicebar_rig_v007_Ta.ma

		eles = currentFile.split('/')
		drive = eles[0]
		project = eles[1]
		assetType = eles[4]
		assetSubType = eles[5]
		assetName = eles[6]
		fileName = '%s_Cache.mb' % assetName

		refPath = ('/').join([drive, project, 'asset', '3D', assetType, assetSubType, assetName, 'ref', fileName])

		return refPath


def unlockTransform(objects) : 

	for each in objects : 
		attrs = mc.listAttr(each, k = True)
		
		if mc.objectType(each, isType = 'transform') : 
			for attr in attrs : 
				mc.setAttr('%s.%s' % (each, attr), l = False)
