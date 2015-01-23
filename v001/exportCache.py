import os, sys, sip
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime
from PyQt4 import QtCore, QtGui

#Import GUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#Custom import modules
from tools import fileUtils, mayaTools, getInfo, info, calculate
reload(fileUtils)

reload(mayaTools)

reload(getInfo)
reload(info)
reload(calculate)

from ptCacheTools import exportUI as ui
reload(ui)


# If inside Maya open Maya GUI
def getMayaWindow() : 
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

import maya.OpenMayaUI as mui
getMayaWindow()


class MyForm(QtGui.QMainWindow) : 
	def __init__(self, parent=None) : 

		# Setup Window
		QtGui.QWidget.__init__(self, parent)
		self.ui = ui.Ui_ExportCacheWindow()
		self.ui.setupUi(self)

		# instance cmd
		self.cacheCommand = cmd()


		# custom variables

		self.cacheAssetList = []
		self.okIcon = 'O:/systemTool/mel/icons/OK_icon.png'

		# run function
		self.fillUI()

		self.initConnection()

	def initConnection(self) : 
		self.ui.manual_checkBox.stateChanged.connect(self.setManualCacheState)
		self.ui.overrideOutput_checkBox.stateChanged.connect(self.overrideOutputUI)
		self.ui.cacheSelected_pushButton.clicked.connect(self.exportSelectedCache)
		self.ui.cache_pushButton.clicked.connect(self.exportCacheAction)
		self.ui.publishHero_pushButton.clicked.connect(self.publishCache)

		self.ui.updateSet_pushButton.clicked.connect(self.listSetUI)
		self.ui.exportSet_pushButton.clicked.connect(self.exportSet)

		self.ui.add_pushButton.clicked.connect(self.addNonCacheUI)
		self.ui.remove_pushButton.clicked.connect(self.clearCacheUI)
		self.ui.exportNonCache_pushButton.clicked.connect(self.exportNonCache)

		self.ui.exportCamera_pushButton.clicked.connect(self.exportCamera)
		self.ui.buildScene_pushButton.clicked.connect(self.prepareBuildScene)

		self.ui.all_checkBox.stateChanged.connect(self.listCameraUI)


	def fillUI(self) : 
		info = self.cacheCommand.info()

		self.ui.project_label.setText(info['project'])
		self.ui.episode_label.setText(info['episode'])
		self.ui.sequence_label.setText(info['sequence'])
		self.ui.shot_label.setText(info['shot'])

		self.listAssetUI()
		self.listSetUI()
		self.listNonCacheUI()
		self.listCameraUI()
		self.ui.cache_label.setText('Cache Version : %s' % info['cacheVersion'])
		self.ui.output_lineEdit.setText(info['cachePath'])
		self.ui.output_lineEdit.setEnabled(False)

		if self.cacheCommand.pipelineStatus : 
			self.ui.status_label.setText('<font color="green">Ready</font>')

		if not self.cacheCommand.pipelineStatus : 
			self.ui.status_label.setText('<font color="red">Wrong pipeline, Manual mode only.</font>')

		# self.ui.backupHero_checkBox.setCheckState(True)


	def listAssetUI(self) : 
		assets = self.cacheCommand.listAsset()

		self.ui.asset_listWidget.clear()

		for each in assets : 
			self.ui.asset_listWidget.addItem(each)


	def setManualCacheState(self) : 
		if self.ui.manual_checkBox.isChecked() : 
			self.ui.cache_pushButton.setText('Export Selected Geometry')

		if not self.ui.manual_checkBox.isChecked() : 
			self.ui.cache_pushButton.setText('Cache All')


	def overrideOutputUI(self) : 

		path = self.cacheCommand.info()

		if self.ui.overrideOutput_checkBox.isChecked() : 
			self.ui.output_lineEdit.setEnabled(True)

		if not self.ui.overrideOutput_checkBox.isChecked() : 
			self.ui.output_lineEdit.setEnabled(False)
			self.ui.output_lineEdit.setText(path['cachePath'])

	def exportCacheAction(self) : 

		# set range time line
		# self.setCacheRange()

		if self.ui.manual_checkBox.isChecked() : 
			self.manualCache()

		if not self.ui.manual_checkBox.isChecked() : 
			result = self.cacheAll()
			self.exportLog()

			if result : 
				self.setStatusCache_pushButton()


	def exportSelectedCache(self) : 
		self.cacheSelected()
		self.exportLog()


	def getAllWidgetItem(self, listWidget) : 
		cmd = 'self.ui.%s.count()' % (listWidget)
		count = int(eval(cmd))
		allItems = []

		for i in range(count) : 
			tmpCmd = 'self.ui.%s.item(%s).text()' % (listWidget, i)
			item = str(eval(tmpCmd))
			allItems.append(item)

		return allItems


	def exportLog(self) : 
		# export cachable asset in the scene
		self.cacheCommand.exportAssetDB()

		# export asset list in hero dir and file path
		self.cacheCommand.exportReferenceDB(self.cacheAssetList)

		# export log for each cache
		self.cacheCommand.createLog(self.cacheAssetList)

		# export camera log
		# self.cacheCommand.exportCameraLog()


	def cacheSelected(self) : 
		currentItems = self.ui.asset_listWidget.selectedItems()
		selectedItems = []
		selectedGeometry = []

		# convert to list
		for each in currentItems : 
			selectedItems.append(str(each.text()))

		# assign selected list to log
		self.cacheAssetList = selectedItems


		# make selection

		for each in selectedItems : 
			tmp = self.cacheCommand.selectGeometry(each)
			selectedGeometry+=tmp


		# clean view port
		mayaTools.isolateObj(True)

		# select cache geo
		mc.select(selectedGeometry)

		# collect object name full path into database
		self.cacheCommand.checkAssetName()

		# export cache
		self.exportCache()

		# bring back view port
		mayaTools.isolateObj(False)

		# # fix cache name
		# self.cacheCommand.exportAssetInfo()


	def cacheAll(self) : 
		items = self.getAllWidgetItem('asset_listWidget')
		selectedGeometry = []

		# assign selected asset to log
		self.cacheAssetList = items

		for each in items : 
			tmp = self.cacheCommand.selectGeometry(each)
			selectedGeometry+=tmp

		# clean view port
		mayaTools.isolateObj(True)

		# select cache geo
		mc.select(selectedGeometry)

		# collect object name full path into database
		self.cacheCommand.checkAssetName()

		# export cache
		self.exportCache()

		# bring back view port
		mayaTools.isolateObj(False)

		return True


	def exportCache(self) : 
		if not self.ui.overrideOutput_checkBox.isChecked() : 
			result = self.cacheCommand.cache('default', '')


		if self.ui.overrideOutput_checkBox.isChecked() : 
			path = str(self.ui.output_lineEdit.text())
			path = mayaTools.fixPath(path, '/')

			result = self.cacheCommand.cache('manual', path)



	def manualCache(self) : 
		if mc.ls(sl = True) : 
			self.exportCache()


	def publishCache(self) : 
		if self.ui.backupHero_checkBox.isChecked() : 
			self.cacheCommand.backupCacheAction()

		result = self.cacheCommand.publishCacheData()

		if result : 
			self.setStatusPublish_pushButton()


	def prepareBuildScene(self) : 
		result = self.cacheCommand.createScene()

		if result : 
			self.setStatusBuildScene_pushButton()
			mm.eval('print "Build Scene Done\\n";')

		else : 
			mm.eval('warning "Scene Exists\\n";')


	def setCacheRange(self) : 
		shots = self.getAllItem('camera_listWidget')
		min = float()
		max = float()
		sequences = []

		if shots : 
			for each in shots : 
				startFrame = float(mc.getAttr('%s.startFrame' % each))
				endFrame = float(mc.getAttr('%s.endFrame' % each))

				sequences.append(startFrame)
				sequences.append(endFrame)

			min, max = calculate.minMax(sequences)

			mc.playbackOptions(min = min, max = max)


	def listSetUI(self) : 
		setVariable = 'set'
		if mc.objExists(setVariable) : 
			sets = mc.listRelatives(setVariable)

			if sets : 
				self.ui.set_listWidget.clear()

				for each in sets : 
					self.ui.set_listWidget.addItem(each)


	def listNonCacheUI(self) : 
		# read from file
		info = self.cacheCommand.info()
		logPath = info['nonCacheLogPath']
		basename = os.path.basename(logPath)
		dir = logPath.replace('/%s' % basename, '')

		if not os.path.exists(logPath) :
			os.makedirs(dir) 
			fileUtils.writeFile(logPath, '[]')

		data = eval(fileUtils.readFile(logPath))

		self.ui.nonCache_listWidget.clear()

		for each in data : 
			self.ui.nonCache_listWidget.addItem(each)


	def addNonCacheUI(self) : 
		sels = mc.ls(sl = True)

		# read from file
		info = self.cacheCommand.info()
		logPath = info['nonCacheLogPath']
		data = eval(fileUtils.readFile(logPath))

		for each in sels : 
			if not each in data : 
				self.ui.nonCache_listWidget.addItem(each)
				data.append(each)

		# write back
		fileUtils.writeFile(logPath, str(data))



	def clearCacheUI(self) : 
		self.ui.nonCache_listWidget.clear()

		info = self.cacheCommand.info()
		logPath = info['nonCacheLogPath']
		fileUtils.writeFile(logPath, '[]')



	def exportSet(self) : 
		exportSetVar = 'set'
		if mc.objExists(exportSetVar) : 
			result = self.cacheCommand.exportSetCmd(exportSetVar)

			if result : 
				self.setStatusSet_pushButton()


	def exportNonCache(self) : 
		items = self.getAllWidgetItem('nonCache_listWidget')

		allItems = len(items)
		existItem = 0

		for eachItem in items : 
			if mc.objExists(eachItem) : 
				existItem+=1

		if allItems == existItem : 
			result = self.cacheCommand.exportNonCacheCmd(items)

			if result : 
				self.setStatusNonCache_pushButton()


	def listCameraUI(self) : 
		info = self.cacheCommand.info()
		shots = []
		if self.ui.all_checkBox.isChecked() : 
			shots = self.cacheCommand.listCamera()

		else : 
			if info['shot'] in self.cacheCommand.listCamera() : 
				shots.append(info['shot'])

		if shots : 
			self.ui.camera_listWidget.clear()

			for each in shots : 
				self.ui.camera_listWidget.addItem(each)	

		# set time slider shot ranger

		self.setCacheRange()


	def exportCamera(self) : 
		shots = self.getAllItem('camera_listWidget')
		result = self.cacheCommand.exportCameraCmd(shots)

		if result : 
			self.setStatusCamera_pushButton()


	def getAllItem(self, listWidget) : 
		countCmd = 'self.ui.%s.count()' % listWidget
		count = eval(countCmd)
		items = []

		for i in range(count) : 
			cmd = 'str(self.ui.%s.item(%s).text())' % (listWidget, i)
			item = eval(cmd)
			items.append(item)

		return items


	def setStatusSet_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.exportSet_pushButton.setIcon(icon)
			self.ui.exportSet_pushButton.setText('1. Export Set')


	def setStatusNonCache_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.exportNonCache_pushButton.setIcon(icon)
			self.ui.exportNonCache_pushButton.setText('1. Export Non Cache (Optional)')


	def setStatusCamera_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.exportCamera_pushButton.setIcon(icon)
			self.ui.exportCamera_pushButton.setText('2. Export Camera')


	def setStatusCache_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.cache_pushButton.setIcon(icon)
			self.ui.cache_pushButton.setText('3. Export Cache')


	def setStatusPublish_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.publishHero_pushButton.setIcon(icon)
			self.ui.publishHero_pushButton.setText('4. Publish Hero Cache')


	def setStatusBuildScene_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.buildScene_pushButton.setIcon(icon)
			self.ui.buildScene_pushButton.setText('5. Prepare Build Scene')


class cmd() : 
	def __init__(self) : 
		self.dbPath = str()
		self.cachePath = str()
		self.cacheRawPath = str()
		self.backupCache = str()
		self.heroCachePath = str()
		self.referenceDBPath = str()
		self.heroAsset = []
		self.logPath = str()
		self.setPath = str()
		self.nonCachePath = str()
		self.cameraPath = str()
		self.cameraLogPath = str()
		self.nonCacheLogPath = str()
		self.buildScenePath = str()

		self.project = '-'
		self.episode = '-'
		self.sequence = '-'
		self.shot = '-'
		self.projectCode = str()
		self.episodeCode = str()
		self.cacheVersion = str()

		self.pipelineStatus = self.setPathInfo()


	def setPathInfo(self) : 
		try : 
			currentLevel = getInfo.ptPipelineSceneInfo('animFilePath')

			# always cache in animClean
			if not '/animClean' in currentLevel : 
				currentLevel = currentLevel.replace('/anim', '/animClean')

			project = getInfo.ptPipelineSceneInfo('project')
			episode = getInfo.ptPipelineSceneInfo('episode')
			sequence = getInfo.ptPipelineSceneInfo('sequence')
			shot = getInfo.ptPipelineSceneInfo('shot')

			projectInfo = info.project(project)
			projectCode = projectInfo.code()
			episodeInfo = info.episode(project, episode)
			episodeCode = episodeInfo.code()

			dbFile = '%s_%s_%s_%s_assetCache.txt' % (projectCode, episodeCode, sequence, shot)
			heroCacheFile = '%s_%s_%s_%s_heroCache.txt' % (projectCode, episodeCode, sequence, shot)
			referenceDBFile = '%s_%s_%s_%s_referenceDB.txt' % (projectCode, episodeCode, sequence, shot)
			setFile = '%s_%s_%s_%s_set.ma' % (projectCode, episodeCode, sequence, shot)
			nonCacheFile = '%s_%s_%s_%s_nonCache.ma' % (projectCode, episodeCode, sequence, shot)
			cameraFile = '%s_%s_%s_%s_camera.ma' % (projectCode, episodeCode, sequence, shot)
			cameraLogFile = '%s_%s_%s_%s_cameraLog.txt' % (projectCode, episodeCode, sequence, shot)
			assetLogFile = '%s_%s_%s_%s_assetInfo.txt' % (projectCode, episodeCode, sequence, shot)
			nonCacheLogFile = '%s_%s_%s_%s_nonCacheLog.txt' % (projectCode, episodeCode, sequence, shot)
			buildSceneFile = '%s_%s_%s_%s_buildCache.ma' % (projectCode, episodeCode, sequence, shot)


			dbPath = os.path.join(currentLevel, 'cache', 'data', dbFile)
			heroCachePath = os.path.join(currentLevel, 'cache', 'data', heroCacheFile)
			referenceDBPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'data', referenceDBFile), '/')
			logPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'log'), '/')
			setPath = os.path.join(currentLevel, 'cache', 'set', setFile)
			nonCachePath = os.path.join(currentLevel, 'cache', 'nonCacheAsset', nonCacheFile)
			cameraPath = os.path.join(currentLevel, 'cache', 'camera', cameraFile)
			cameraLogPath = os.path.join(currentLevel, 'cache', 'camera', cameraLogFile)
			assetLogPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'data', assetLogFile), '/')
			nonCacheLogPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'data', nonCacheLogFile), '/')
			buildScenePath = mayaTools.fixPath(os.path.join(currentLevel, 'scenes', 'work', buildSceneFile), '/')

			self.dbPath = dbPath
			self.heroCachePath = heroCachePath
			self.referenceDBPath = referenceDBPath
			self.logPath = logPath
			self.setPath = setPath
			self.nonCachePath = nonCachePath
			self.cameraPath = cameraPath
			self.cameraLogPath = cameraLogPath
			self.assetLogPath = assetLogPath
			self.nonCacheLogPath = nonCacheLogPath
			self.buildScenePath = buildScenePath

			self.cacheRawPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'raw'), '/')
			self.cachePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'publish'), '/')
			self.backupCache = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'backup'), '/')

			self.project = project
			self.episode = episode
			self.sequence = sequence
			self.shot = shot
			self.projectCode = projectCode
			self.episodeCode = episodeCode

			return True

		except : 
			return False


	def info(self) : 
		tmpData = {
					'project': self.project, 
					'episode': self.episode, 
					'sequence': self.sequence, 
					'shot': self.shot, 
					'projectCode': self.projectCode, 
					'episodeCode': self.episodeCode, 
					'cachePath': self.cacheRawPath, 
					'heroCachePath': self.cachePath, 
					'backupCachePath': self.backupCache, 
					'logPath': self.logPath, 
					'setPath': self.setPath, 
					'nonCachePath': self.nonCachePath, 
					'cameraPath': self.cameraPath,
					'cacheVersion': self.getVersionDir(self.cachePath), 
					'cameraLogPath': self.cameraLogPath, 
					'nonCacheLogPath': self.nonCacheLogPath, 
					'buildScenePath': self.buildScenePath
		}

		return tmpData


	def listAsset(self) : 
		caches = []
		assets = mc.ls('*:Rig_Grp')

		for each in assets : 
			if mc.objExists('%s.cache' % each) : 
				status = mc.getAttr('%s.cache' % each)

				if status : 
					namespace = mayaTools.getNamespace(each)

					if not namespace in caches : 
						caches.append(namespace)


		return caches


	# export text file data  ================================================================

	def exportAssetDB(self) : 
		dbFile = self.dbPath
		data = str(self.listAsset())

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)

		fileUtils.writeFile(dbFile, data)


	def exportReferenceDB(self, lists) : 
		db = dict()
		dbFile = self.referenceDBPath
		print dbFile

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)
			fileUtils.writeFile(dbFile, '{}')

		db = eval(fileUtils.readFile(dbFile))

		for eachAsset in lists : 
			rigGrp = '%s:Rig_Grp' % eachAsset

			if mc.objExists(rigGrp) : 
				path = mayaTools.getReferencePath(rigGrp)
				db[eachAsset] = path

		data = str(db)

		fileUtils.writeFile(dbFile, data)


	def exportHeroCacheDB(self) : 
		dbFile = self.heroCachePath
		newData = self.heroAsset

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)
			fileUtils.writeFile(dbFile, '[]')

		data = eval(fileUtils.readFile(dbFile))

		for eachAsset in newData : 
			if not eachAsset in data : 
				data.append(eachAsset)


		fileUtils.writeFile(dbFile, str(data))


	def exportCameraLog(self, lists) : 
		info = dict()
		data = str()

		for each in lists : 
			min = mc.getAttr('%s.startFrame' % each)
			max = mc.getAttr('%s.endFrame' % each)

			info[each] = [min, max]

		dbFile = self.cameraLogPath
		data = str(info)

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)

		fileUtils.writeFile(dbFile, data)


	def exportAssetInfo(self, data) : 
		dbFile = self.assetLogPath

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)
			fileUtils.writeFile(dbFile, '{}')

		fileUtils.writeFile(dbFile, data)
		print 'file created %s' % dbFile


	def createLog(self, lists) : 
		logDir = self.logPath
		dateInfo = str(datetime.now())
		date = dateInfo.split(' ')[0]
		time = '(%s)' % dateInfo.split(' ')[-1].split('.')[0].replace(':', '-')

		logFileName = '%s_%s.txt' % (date, time)

		logFile = os.path.join(logDir, logFileName)

		data = str(lists)

		if not os.path.exists(logFile) : 
			fileUtils.createFile(logFile)

		fileUtils.writeFile(logFile, data)


	def selectGeometry(self, obj) : 
		cacheGeo = []

		if mc.objExists('%s:Geo_Grp' % obj) : 
			# mc.select('%s:Geo_Grp' % obj, hi = True)
			# objs = mc.ls(sl = True, l = True)
			objs = mc.listRelatives('%s:Geo_Grp' % obj, ad = True, f = True)
			mc.select(cl = True)

			# find only mesh 
			for each in objs : 
				if mc.objectType(each, isType = 'mesh') : 

					# get only first transform found
					transform = mc.listRelatives(each, p = True, f = True)[0]

					# add to cache geometry
					cacheGeo.append(transform)

		return cacheGeo


	# cache section  ================================================================


	def cache(self, mode = 'default', path = '') : 

		if mode == 'default' : 
			cachePath = self.cacheRawPath

		if mode == 'manual' : 
			cachePath = path
		print 'Start Caching ...\n'

		try : 

			self.cacheCmd(cachePath)

			print 'Cache Complete  ================================================================================'

			return True

		except : 

			return False



	def cacheCmd(self, dst) : 
		# cache command from modifying poCreateUI.mel
		# source "O:/systemTools/mel/poCreateUI.mel"

		mm.eval('source "poCreateUI"')

		if not os.path.exists(dst) : 
			os.makedirs(dst)

		mm.eval('POBAKECmd("%s")' % dst)


	# publish cache  ================================================================

	def publishCacheData(self) : 
		cache = self.cacheRawPath
		assets = self.listAsset()
		log = dict()
		publishAsset = []

		cacheFiles = fileUtils.listFile(cache, 'mdd')
		versionDir = self.getVersionDir(self.cachePath)

		print 'Start publishing ...\n'
		print 'assets %s' % assets

		for each in assets : 
			assetTmp = []

			for eachCache in cacheFiles : 
				if each in eachCache : 

					assetDir = os.path.join(self.cachePath, versionDir, each)

					if not os.path.exists(assetDir) : 
						os.makedirs(assetDir)

					src = os.path.join(cache, eachCache)
					dst = os.path.join(assetDir, eachCache)

					print 'Publish %s \n-> %s \n' % (src, dst)

					fileUtils.copy(src, dst)
					assetTmp.append(eachCache)

			log[each] = assetTmp

		# export hero cache text file data

		for each in log : 
			publishAsset.append(each)

		self.heroAsset = sorted(publishAsset)
		self.exportHeroCacheDB()

		# print report 
		print 'Summary ================================================================================'
		print 'version %s' % versionDir
		for each in log : 
			print '%s' % (each)
			print '-%s files\n' % (len(log[each]))


		print 'Publish complete ================================================================================'

		return log


	def backupCacheAction(self) : 
		src = self.cachePath
		dst = self.backupCache

		if os.path.exists(self.cachePath) : 

			print ('backup hero cache\n %s \n-> %s \n' % (src, dst))

			try : 

				fileUtils.copyTree(src, dst)

				print ('Backup Complete  ================================================================================')

				return True

			except : 

				return False


	def getVersionDir(self, src) : 
		version = 'v001'
		if os.path.exists(src) : 
			dirs = fileUtils.listFolder(src)
			prefix = 'v'
			padding = 3
			version = str()

			if dirs : 
				version = getInfo.incrementVersionDir(dirs, prefix, padding)

		return version


	def exportSetCmd(self, obj) : 
		if mc.objExists(obj) : 
			info = self.info()
			path = info['setPath']

			mc.select(obj)

			dir = path.replace(os.path.basename(path), '')

			if not os.path.exists(dir) : 
				os.makedirs(dir)

			mc.file(path, force = True, options = 'v=0', type = 'mayaAscii', pr = True, es = True)

			mc.select(cl = True)

			print 'export set complete  ===='

			return True

		else : 
			print 'Cannot Export. Set does not exist'

			return False


	def exportNonCacheCmd(self, objs) : 
		allExists = 0
		objSize = len(objs)
		notExists = []

		for eachObj in objs : 
			if mc.objExists(eachObj) : 
				allExists+=1

			else : 
				notExists.append(eachObj)

		if allExists == objSize : 
			info = self.info()
			path = info['nonCachePath']

			mc.select(objs)

			dir = path.replace(os.path.basename(path), '')

			if not os.path.exists(dir) : 
				os.makedirs(dir)

			mc.file(path, force = True, options = 'v=0', type = 'mayaAscii', pr = True, es = True)

			mc.select(cl = True)

			print 'export non cache complete  ===='

			return True

		else : 
			print 'Cannot Export'

			for each in notExists : 
				print each

			print 'does not exist'

			return False


	def listCamera(self) : 
		shots = mc.ls(type = 'shot')
		validNameCamera = []
		for each in shots : 
			if each[0] == 's' and each[-4:].isdigit() : 
				validNameCamera.append(each)

		return validNameCamera


	def exportCameraCmd(self, shots) : 
		# shots = self.listCamera()

		info = self.info()

		if shots : 
			path = info['cameraPath']
			cameraPath = path.replace(os.path.basename(path), '')

			if not os.path.exists(cameraPath) : 
				os.makedirs(cameraPath)

			mc.select(shots)
			mc.file(path, force = True, options = 'v=0', type = 'mayaAscii', pr = True, es = True)

			print 'export camera complete  ===='

			# export log

			self.exportCameraLog(shots)

			return True

		else : 
			print 'Shots does not exists'

			return False


	def checkAssetName(self) : 
		# collect all selected object
		selObjs = mc.ls(sl = True)

		# read previous data
		nameInfo = dict()
		nameInfo = self.readAssetInfo()

		dupName = []

		# see if | in name
		for each in selObjs : 
			if '|' in each : 
				if not each in dupName : 
					dupName.append(each)
					convertName = each.replace('|', '_').replace(':', '_')
					nameInfo[convertName] = each
			
			
		# for each in nameInfo : 
		# 	print nameInfo[each]	

		# create log
		self.exportAssetInfo(str(nameInfo))

		return nameInfo


	def readAssetInfo(self) : 
		dbFile = self.assetLogPath

		if os.path.exists(dbFile) : 

			data = eval(fileUtils.readFile(dbFile))
			
			return data

		else : 
			return dict()


	def createScene(self) : 
		getInfo = self.info()
		dst = getInfo['buildScenePath']
		src = 'O:/systemTool/template/maya/emptyScene.ma'

		if not os.path.exists(dst) : 
			result = fileUtils.copy(src, dst)

			return result

	# def fixCacheName(self) : 
	# 	# cache path
	# 	info = self.info()
	# 	path = info['cachePath']

	# 	files = fileUtils.listFile(path)

	# 	checkFile = self.checkAssetName()

	# 	if checkFile : 

	# 		for eachFile in files : 
	# 			if eachFile in checkFile.keys() : 
	# 				print 'file %s' % checkFile[eachFile]
			