import os, sys, sip
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime
from PyQt4 import QtCore, QtGui

#Import GUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#Custom import modules
from tools import fileUtils, mayaTools, getInfo, info
reload(fileUtils)

reload(mayaTools)

reload(getInfo)
reload(info)

from ptCacheTools import cacheManagerUI as ui
reload(ui)


# If inside Maya open Maya GUI
def getMayaWindow() : 
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

import maya.OpenMayaUI as mui
getMayaWindow()


class MyForm(QtGui.QMainWindow, cmd) : 
	def __init__(self, parent=None) : 

		# Setup Window
		QtGui.QWidget.__init__(self, parent)
		self.ui = ui.Ui_cacheManagerWindow()
		self.ui.setupUi(self)

		# instance cmd
		self.cacheCommand = cmd()


		# custom variables

		self.cacheAssetList = []

		# run function
		self.fillUI()

		self.initConnection()

	def initConnection(self) : 
		self.ui.manual_checkBox.stateChanged.connect(self.setManualCacheState)
		self.ui.overrideOutput_checkBox.stateChanged.connect(self.overrideOutputUI)
		self.ui.cacheSelected_pushButton.clicked.connect(self.exportSelectedCache)
		self.ui.cache_pushButton.clicked.connect(self.exportCacheAction)
		self.ui.publishHero_pushButton.clicked.connect(self.publishCache)


	def fillUI(self) : 
		info = self.cacheCommand.info()

		self.ui.project_label.setText(info['project'])
		self.ui.episode_label.setText(info['episode'])
		self.ui.sequence_label.setText(info['sequence'])
		self.ui.shot_label.setText(info['shot'])

		self.listAssetUI()
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

		if self.ui.manual_checkBox.isChecked() : 
			self.manualCache()

		if not self.ui.manual_checkBox.isChecked() : 
			self.cacheAll()
			self.exportLog()


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

		# select cache geo
		mc.select(selectedGeometry)

		# export cache
		self.exportCache()


	def cacheAll(self) : 
		items = self.getAllWidgetItem('asset_listWidget')
		selectedGeometry = []

		# assign selected asset to log
		self.cacheAssetList = items

		for each in items : 
			tmp = self.cacheCommand.selectGeometry(each)
			selectedGeometry+=tmp

		# select cache geo
		mc.select(selectedGeometry)

		# export cache
		self.exportCache()


	def exportCache(self) : 
		if not self.ui.overrideOutput_checkBox.isChecked() : 
			self.cacheCommand.cache('default', '')

		if self.ui.overrideOutput_checkBox.isChecked() : 
			path = str(self.ui.output_lineEdit.text())
			path = mayaTools.fixPath(path, '/')

			self.cacheCommand.cache('manual', path)


	def manualCache(self) : 
		if mc.ls(sl = True) : 
			self.exportCache()


	def publishCache(self) : 
		if self.ui.backupHero_checkBox.isChecked() : 
			self.cacheCommand.backupCacheAction()

		self.cacheCommand.publishCacheData()






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

		self.project = '-'
		self.episode = '-'
		self.sequence = '-'
		self.shot = '-'
		self.projectCode = str()
		self.episodeCode = str()


		self.pipelineStatus = self.setPathInfo()


	def setPathInfo(self) : 
		try : 
			currentLevel = getInfo.ptPipelineSceneInfo('animFilePath')
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


			dbPath = os.path.join(currentLevel, 'cache', 'data', dbFile)
			heroCachePath = os.path.join(currentLevel, 'cache', 'data', heroCacheFile)
			referenceDBPath = os.path.join(currentLevel, 'cache', 'data', referenceDBFile)
			logPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'log'), '/')

			self.dbPath = dbPath
			self.heroCachePath = heroCachePath
			self.referenceDBPath = referenceDBPath
			self.logPath = logPath

			self.cacheRawPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'raw'), '/')
			self.cachePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'hero'), '/')
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
					'logPath': self.logPath
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
		for eachAsset in lists : 
			rigGrp = '%s:Rig_Grp' % eachAsset

			if mc.objExists(rigGrp) : 
				path = mayaTools.getReferencePath(rigGrp)
				db[eachAsset] = path

		dbFile = self.referenceDBPath
		data = str(db)

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)

		fileUtils.writeFile(dbFile, data)


	def exportHeroCacheDB(self) : 
		dbFile = self.heroCachePath
		data = str(self.heroAsset)

		if not os.path.exists(dbFile) : 
			fileUtils.createFile(dbFile)

		fileUtils.writeFile(dbFile, data)


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
			mc.select('%s:Geo_Grp' % obj, hi = True)
			objs = mc.ls(sl = True, l = True)
			mc.select(cl = True)

			# find only mesh 
			for each in objs : 
				if mc.objectType(each, isType = 'mesh') : 

					# get only first transform found
					transform = mc.listRelatives(each, p = True)[0]

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

		self.cacheCmd(cachePath)

		print 'Cache Complete  ================================================================================'



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

		print 'Start publishing ...\n'

		for each in assets : 
			assetTmp = []

			for eachCache in cacheFiles : 
				if each in eachCache : 

					assetDir = os.path.join(self.cachePath, each)

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

			fileUtils.copyTree(src, dst)

			print ('Backup Complete  ================================================================================')

