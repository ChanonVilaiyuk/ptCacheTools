import os, sys, sip
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime
from PyQt4 import QtCore, QtGui

import subprocess

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

from ptCacheTools import importUI3 as ui
reload(ui)

from ptCacheTools import exportCache, openNoteCore
reload(exportCache)
reload(openNoteCore)


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
		self.ui = ui.Ui_ImportCacheWindow()
		self.ui.setupUi(self)


		# instance command
		self.cacheCommand = cmd()

		
		# custom variable
		self.heroCacheLog = self.cacheCommand.info()['heroCacheLog']
		self.referenceDBPath = self.cacheCommand.info()['referenceDBPath']
		self.cacheAssets = []
		self.drive = 'P:/'
		self.maxVersion = str()
		self.assetVersion = ['Cache', 'Render']

		self.greenIcon = 'O:/systemTool/mel/icons/green_icon.png'
		self.redIcon = 'O:/systemTool/mel/icons/red_icon.png'
		self.okIcon = 'O:/systemTool/mel/icons/OK_icon.png'

		self.techAnimIcon = 'O:/systemTool/python/ptCacheTools/techAnim_icon.png'


		# run function
		self.fillUI()
		self.initialFunction()
		self.initialConnection()
		self.cacheCommand.loadPlugin()


	def fillUI(self) : 
		info = self.cacheCommand.info()

		self.setProjectComboBox()
		self.setAutoComboBox()
		self.listCacheVersion()
		self.setIconReportProblem_pushButton()
		# self.ui.episode_label.setText(info['episode'])
		# self.ui.sequence_label.setText(info['sequence'])
		# self.ui.shot_label.setText(info['shot'])


	def refreshUI(self) : 
		self.clearTable()
		self.listAssetCacheVersion()
		self.listRebuildVersion()
		self.listCache()
		self.listAsset()
		self.listCacheVersion()
		# self.listSet()
		self.listSetNonCache()
		self.listCamera()


	def clearTable(self) : 
		rows = self.ui.asset_tableWidget.rowCount()
		# self.ui.asset_tableWidget.clear()

		for each in range(rows) : 
			self.ui.asset_tableWidget.removeRow(0)


	def initialConnection(self) : 
		self.ui.removeAsset_pushButton.clicked.connect(self.removeReferenceAction)
		self.ui.refresh_pushButton.clicked.connect(self.refreshUI)
		self.ui.rebuildAsset_pushButton.clicked.connect(self.buildAssetAction)

		self.ui.project_comboBox.currentIndexChanged.connect(self.setEpisodeComboBox)
		self.ui.episode_comboBox.currentIndexChanged.connect(self.setSequenceComboBox)
		self.ui.sequence_comboBox.currentIndexChanged.connect(self.setShotComboBox)
		self.ui.shot_comboBox.currentIndexChanged.connect(self.refreshUI)
		self.ui.showPlayblast_pushButton.clicked.connect(self.showPlayblast)
		self.ui.asset_tableWidget.cellClicked.connect(self.tableAction)

		self.ui.importCache_pushButton.clicked.connect(self.importCacheAction)

		self.ui.buildSet_pushButton.clicked.connect(self.buildAll)
		self.ui.animCurve_pushButton.clicked.connect(self.applyAnimCurve)

		self.ui.getCamera_pushButton.clicked.connect(self.importCamera)
		self.ui.importAsset_pushButton.clicked.connect(self.importAsset)
		self.ui.asset_tableWidget.customContextMenuRequested.connect(self.showMenu)
		self.ui.sg_pushButton.clicked.connect(self.setShotgun)

		self.ui.switchSet_pushButton.clicked.connect(self.runAssetManager)
		self.ui.reportProblem_pushButton.clicked.connect(self.doReportProblem)


	def initialFunction(self) : 
		self.setCacheReadPath()
		self.listCache()
		self.listAsset()
		self.listAssetCacheVersion()
		self.listRebuildVersion()
		# self.listSet()
		self.listSetNonCache()
		self.listCamera()


	def tableAction(self, row, column) : 
		assetName = str(self.ui.asset_tableWidget.item(row, 0).text())

		data = self.cacheCommand.readAssetReferenceFile()

		if assetName in data.keys() : 
			path = data[assetName].split('{')[0]

			# find icon path by replace /ref/ to /images/icon/
			basename = os.path.basename(path)
			iconFile = basename.replace('_Cache.mb', '.png').split('{')[0]
			assetPath = path.replace('/%s' % basename, '')
			iconPath = assetPath.replace('/ref', '/images/icon')
			iconPath = '%s/%s' % (iconPath, iconFile)

			# set preview icon
			if os.path.exists(iconPath) : 
				self.setIcon(iconPath)

			else : 
				mm.eval('warning("No icon %s");' % iconPath)

	def setAutoComboBox(self) : 
		info = self.cacheCommand.info()

		self.setProjectComboBox(info['project'])
		self.setEpisodeComboBox(info['episode'])
		self.setSequenceComboBox(info['sequence'])
		self.setShotComboBox(info['shot'])


	def setProjectComboBox(self, project='') : 
		projects = self.browseProject()
		index = int()
		i = 0

		if projects : 
			self.ui.project_comboBox.clear()

			for each in projects : 
				if each == project : 
					index = i
				self.ui.project_comboBox.addItem(each)

				i+=1

		self.ui.project_comboBox.setCurrentIndex(index)

	def setEpisodeComboBox(self, episode='') : 
		project = str(self.ui.project_comboBox.currentText())
		episodes = self.browseEpisode(project)
		index = int()
		i = 0

		if episodes : 
			self.ui.episode_comboBox.clear()

			for each in episodes : 
				if each == episode : 
					index = i
				self.ui.episode_comboBox.addItem(each)

				i+=1

		self.ui.episode_comboBox.setCurrentIndex(index)

	def setSequenceComboBox(self, sequence='') : 
		project = str(self.ui.project_comboBox.currentText())
		episode = str(self.ui.episode_comboBox.currentText())
		sequences = self.browseSequence(project, episode)
		index = int()
		i = 0

		if sequences : 
			self.ui.sequence_comboBox.clear()

			for each in sequences : 
				if each == sequence : 
					index = i
				self.ui.sequence_comboBox.addItem(each)

				i+=1

		self.ui.sequence_comboBox.setCurrentIndex(index)


	def setShotComboBox(self, shot='') : 
		project = str(self.ui.project_comboBox.currentText())
		episode = str(self.ui.episode_comboBox.currentText())
		sequence = str(self.ui.sequence_comboBox.currentText())
		shots = self.browseShot(project, episode, sequence)
		index = int()
		i = 0

		if shots : 
			self.ui.shot_comboBox.clear()

			for each in shots : 
				if each == shot : 
					index = i
				self.ui.shot_comboBox.addItem(each)

				i+=1

		self.ui.shot_comboBox.setCurrentIndex(index)


	def setCacheReadPath(self) : 
		project = str(self.ui.project_comboBox.currentText())
		episode = str(self.ui.episode_comboBox.currentText())
		sequence = str(self.ui.sequence_comboBox.currentText())
		shot = str(self.ui.shot_comboBox.currentText())

		self.cacheCommand.setPathInfo(project, episode, sequence, shot, 0)

		self.heroCacheLog = self.cacheCommand.info()['heroCacheLog']
		self.referenceDBPath = self.cacheCommand.info()['referenceDBPath']
		self.playblastPath = self.cacheCommand.info()['playblastPath']


	def showPlayblast(self) : 
		playblast = self.playblastPath.replace('/', '\\')
		subprocess.Popen('"C:\Program Files (x86)\QuickTime\QuickTimePlayer.exe" %s' % playblast)


	def showMenu(self, pos) : 
		item = self.getDataFromSelectedRange(0)[0]
		assetType = self.getDataFromSelectedRange(2)[0]
		self.assetMap = {'Render': 'Cache', 'Cache': 'Render'}

		switchingPath = self.cacheCommand.checkSwitchingAsset(item, self.assetMap[assetType])
		animCurve = self.cacheCommand.checkAnimCurve(item)

		if item : 
			menu=QMenu(self)
			subMenu = QMenu('Switch', self)
				

			if not switchingPath : 
				subMenuItem1 = subMenu.addAction('No %s Version' % self.assetMap[assetType])
				
				subMenuItem1.setEnabled(False)

			else : 
				subMenuItem1 = subMenu.addAction('Switch to %s' % self.assetMap[assetType])

			if animCurve : 
				subMenuItem2 = subMenu.addAction('Update Animation')

			else : 
				subMenuItem2 = subMenu.addAction('No Anim Curve')
				subMenuItem2.setEnabled(False)

			subMenu2 = QMenu('Open', self)
			subMenu2.addAction('Open in Explorer')
			subMenu2.addAction('Open Render.mb')	

			menu.addMenu(subMenu)
			menu.addMenu(subMenu2)

			
			menu.popup(self.ui.asset_tableWidget.mapToGlobal(pos))
			result = menu.exec_(self.ui.asset_tableWidget.mapToGlobal(pos))

			if result : 
				# self.menuCommand(result.text(), item)
				self.menuCommand(result.text(), item, result.parentWidget().title())


	def menuCommand(self, command, item, category) : 
		assetName = item
		data = self.cacheCommand.readAssetReferenceFile()
		path = ''
		basePath = ''
		renderAsset = ''

		if assetName in data.keys() : 
			path = data[assetName]
			basename = os.path.basename(path)
			basePath = path.replace(basename, '').replace('/', '\\')
			print basePath
			renderAsset = path.replace('Cache', 'Render')

		if command == 'Open in Explorer' : 
			subprocess.Popen(r'explorer /select,"%s"' % basePath)

		if command == 'Open Render.mb' : 
			mc.file(renderAsset, o = True, f = True)

		if 'Switch to' in command : 
			self.switchReference()

		if command == 'Update Animation' : 
			self.updateAnimationCurve()

			


	def setIcon(self, iconPath) : 
		self.ui.icon_label.setPixmap(QPixmap('%s' % iconPath).scaled(140, 100, QtCore.Qt.KeepAspectRatio))


	def listCache(self) : 

		self.setCacheReadPath()

		lod = str(self.ui.assetVersion_comboBox.currentText())

		if not lod : 
			lod = 'cache'

		# set red color by default / If file exists, will be set to green
		color = [100, 1, 1]

		# read asset info data to get path
		data = self.cacheCommand.readAssetReferenceFile(lod)

		if os.path.exists(self.heroCacheLog) : 
			self.cacheAssets = eval(fileUtils.readFile(self.heroCacheLog))

			for i in range(len(self.cacheAssets)) : 

				# check if file exists

				if self.cacheAssets[i] in data.keys() : 
					path = data[self.cacheAssets[i]].split('{')[0]

					if os.path.exists(path) : 
						# path exists, set to green
						color = [1, 100, 1]

					else : 
						# path not exists, set to red
						color = [100, 1, 1]

				self.insertRow(i, 20)
				self.fillInTable(i, 0, self.cacheAssets[i], color)





	def listAsset(self) : 

		for i in range(len(self.cacheAssets)) : 
			if mc.objExists('%s:Rig_Grp' % self.cacheAssets[i]) : 
				lod = self.getLOD('%s:Rig_Grp' % self.cacheAssets[i])
				self.fillInTable(i, 1, self.cacheAssets[i])
				self.fillInTable(i, 2, lod)

			else : 
				self.fillInTable(i, 1, '')
				self.fillInTable(i, 2, '')


	def getLOD(self, obj) : 
		path = mayaTools.getReferencePath(obj)
		basename = os.path.basename(path)
		lod = basename.split('.')[0].split('_')[-1]

		return lod


	def listAssetCacheVersion(self) : 
		datas = self.cacheCommand.listAllPOReader()
		if datas : 
			assetVersionInfo = dict()
			columnData = []

			for each in self.cacheAssets : 
				if each in datas.keys() : 
					allGeos = datas[each]

					versions = []

					for eachGeo in allGeos : 
						version = allGeos[eachGeo]['version']
						if not version in versions : 
							versions.append(version)

					assetVersionInfo[each] = versions

				columnData = self.getColumnData(1)

			for i in range(len(columnData)) : 

				if columnData[i] in assetVersionInfo.keys() : 
					versionInfo = assetVersionInfo[columnData[i]]

					if len(versionInfo) == 1 : 	
						if versionInfo[0] == self.maxVersion : 		
							# self.fillInTable(i, 3, '%s' % versionInfo[0])
							self.fillInTableIcon(i, 3, '%s' % versionInfo[0], self.greenIcon)

						else : 
							# self.fillInTable(i, 3, '%s' % versionInfo[0])
							self.fillInTableIcon(i, 3, '%s' % versionInfo[0], self.redIcon)

					if len(versionInfo) > 1 : 
						# self.fillInTable(i, 3, '%s +' % versionInfo[0])
						text = (', ').join(versionInfo)
						self.fillInTableIcon(i, 3, '%s' % text, self.redIcon)

		else : 
			columnData = self.getColumnData(1)

			for i in range(len(columnData)) : 
				self.fillInTable(i, 3, '-')


	def listCacheVersion(self) : 
		info = self.cacheCommand.info()
		cachePath = info['heroCachePath']
		versions = []

		if os.path.exists(cachePath) : 
			versions = fileUtils.listFolder(cachePath)

		self.ui.cache_comboBox.clear()

		if versions : 
			count = len(versions)

			for each in versions : 
				self.ui.cache_comboBox.addItem(each)

			self.ui.cache_comboBox.setCurrentIndex(count - 1)

			self.maxVersion = sorted(versions)[-1]

		else : 
			self.ui.cache_comboBox.addItem('No Version Found')


	def listRebuildVersion(self) : 
		self.ui.assetVersion_comboBox.clear()

		for each in self.assetVersion : 
			self.ui.assetVersion_comboBox.addItem(each)


	def removeReferenceAction(self, selectedOnly = False) : 
		assets = []
		if self.ui.all_checkBox.isChecked() : 
			assets = self.getColumnData(1)

		else : 
			assets = self.getDataFromSelectedRange(1)

		if selectedOnly : 
			assets = self.getDataFromSelectedRange(1)

		if assets : 

			for each in assets : 
				obj = '%s:Rig_Grp' % each

				if mc.objExists(obj) : 

					# remove POI nodes
					self.cacheCommand.removePOINode(obj)

					# remove reference
					result = mayaTools.removeReference(obj)

					# clean namespace
					mayaTools.removeNamespace(each)

			# refresh ui
			self.listAsset()


	def buildAssetAction(self) : 
		if self.ui.all_checkBox.isChecked() : 
			# get all rebuild asset
			assets = self.getColumnData(0)

		else : 
			# get selected rebuild asset
			assets = self.getDataFromSelectedRange(0)

		# get existing asset
		existingAsset = self.getColumnData(1)
		rebuildAssets = []
		skip = []
		lod = str(self.ui.assetVersion_comboBox.currentText())

		if assets : 

			for each in assets : 
				# if asset exist, skip..
				if not each in existingAsset : 
					rebuildAssets.append(each)

				else : 
					skip.append(each)

			result = self.cacheCommand.buildAsset(rebuildAssets, lod)

			# refresh UI
			self.listAsset()
			self.listAssetCacheVersion()

			self.setStatusAsset_pushButton()

			# print report
			print '================================================================================'
			# print 'rebuild %s' % rebuildAssets
			print 'File does not exists'
			for each in result : 
				print 'skip %s %s' % (each, result[each])


	def importCacheAction(self, selectedOnly = False) : 
		info = self.cacheCommand.info()
		cachePath = info['heroCachePath']
		version = str(self.ui.cache_comboBox.currentText())

		cacheVersionPath = mayaTools.fixPath(os.path.join(cachePath, version), '/')

		if self.ui.all_checkBox.isChecked() : 
			# get all rebuild asset
			assets = self.getColumnData(0)

		else : 
			# get selected rebuild asset
			assets = self.getDataFromSelectedRange(0)

		if selectedOnly : 
			assets = self.getDataFromSelectedRange(0)

		if assets : 

			self.cacheCommand.applyCache(assets, cacheVersionPath)
			self.listAssetCacheVersion()

			self.setStatusImportCache_pushButton()


	def getColumnData(self, column) : 
		counts = self.ui.asset_tableWidget.rowCount()
		data = []

		for i in range(counts) : 
			item = self.ui.asset_tableWidget.item(i, column)
			if item : 
				data.append(str(item.text()))

		return data 


	def getDataFromSelectedRange(self, columnNumber) : 
		lists = self.ui.asset_tableWidget.selectedRanges()

		if lists : 
			topRow = lists[0].topRow()
			bottomRow = lists[0].bottomRow()
			leftColumn = lists[0].leftColumn()
			rightColumn = lists[0].rightColumn()

			items = []

			for i in range(topRow, bottomRow + 1) : 
				item = str(self.ui.asset_tableWidget.item(i, columnNumber).text())
				items.append(item)


			return items


	def switchReference(self, applyAnimation = True) : 
		info = self.cacheCommand.info()
		item = self.getDataFromSelectedRange(0)[0]
		assetType = self.getDataFromSelectedRange(2)[0]

		switchingPath = self.cacheCommand.checkSwitchingAsset(item, self.assetMap[assetType])
		self.removeReferenceAction(True)

		result = self.cacheCommand.buildAsset([item], self.assetMap[assetType])

		# refresh UI
		self.listAsset()
		self.listAssetCacheVersion()

		# apply animation or cache
		if applyAnimation : 

			# cache version, apply cache
			if self.assetMap[assetType] == 'Cache' : 
				self.importCacheAction(False)


			# Render Version, apply anim curve
			if self.assetMap[assetType] == 'Render' : 
				self.applyRenderAnimCurve(item)


	def updateAnimationCurve(self) : 
		item = self.getDataFromSelectedRange(0)[0]
		self.applyRenderAnimCurve(item)


	# browsw UI ==================================================================

	def browseProject(self) : 
		exception = ['.', '_']
		path = self.drive
		dirs = fileUtils.listFolder(self.drive)
		projects = []

		for each in dirs : 
			if not each[0] in exception : 
				projects.append(each)

		return projects 

	def browseEpisode(self, project) : 
		path = os.path.join(self.drive, project, 'film')
		episodes = fileUtils.listFolder(path)

		return episodes

	def browseSequence(self, project, episode) : 
		path = os.path.join(self.drive, project, 'film', episode)
		sequences = fileUtils.listFolder(path)

		return sequences

	def browseShot(self, project, episode, sequence) : 
		path = os.path.join(self.drive, project, 'film', episode, sequence)
		shots = fileUtils.listFolder(path)

		return shots

	# ==================================================================
	# set section

	def listSet(self) : 
		info = self.cacheCommand.info()
		setPath = info['setPath']

		if os.path.exists(setPath) : 
			baseName = os.path.basename(setPath)

			self.ui.buildSet_pushButton.setEnabled(True)

		else : 
			self.ui.buildSet_pushButton.setEnabled(False)



	# non cache asset section

	def listSetNonCache(self) : 
		info = self.cacheCommand.info()
		nonCachePath = info['nonCachePath'].replace(os.path.basename(info['nonCachePath']), '')
		
		mayaFile = '%s/%s' % (nonCachePath, 'mayaFiles')

		files = fileUtils.listFile(mayaFile)

		if files : 
			self.ui.nonCache_listWidget.clear()

			for each in files : 
				self.ui.nonCache_listWidget.addItem(each.split('.')[0])

				

	# camera section

	def listCamera(self) : 
		info = self.cacheCommand.info()
		cameraPath = info['cameraPath']

		if os.path.exists(cameraPath) : 
			baseName = os.path.basename(cameraPath)

			self.ui.getCamera_pushButton.setEnabled(True)

		else : 
			self.ui.getCamera_pushButton.setEnabled(False)


	def buildAll(self) : 
		info = self.cacheCommand.info()
		nonCachePath = info['nonCachePath'].replace(os.path.basename(info['nonCachePath']), '')
		

		# import all assets
		if self.ui.applyAll_checkBox.isChecked() : 
			assets = self.getAllWidgetItem('nonCache_listWidget')

		else : 
			if self.ui.nonCache_listWidget.selectedItems() : 
				assets = [str(asset.text()) for asset in self.ui.nonCache_listWidget.selectedItems()]

		for each in assets : 

			# check if import from export file or rebuild
			if self.ui.fromExport_checkBox.isChecked() : 
				assetPath = '%s/mayaFiles/%s.ma' % (nonCachePath, each)

				if os.path.exists(assetPath) : 
					if not mc.objExists('%s:Rig_Grp' % each) : 
						try : 
							mc.file(assetPath,  i = True, type = 'mayaAscii', options = 'v=0', pr = True, loadReferenceDepth = 'all')

						except : 
							mm.eval('warning "Cannot import %s\\n";' % assetPath)

					else : 
						mm.eval('warning "%s:Rig_Grp already exists\\n"' % each)

				else : 
					print 'File is missing %s' % assetPath

	def applyAnimCurve(self) : 
		info = self.cacheCommand.info()
		nonCachePath = info['nonCachePath'].replace(os.path.basename(info['nonCachePath']), '')
		

		# import all assets
		if self.ui.applyAll_checkBox.isChecked() : 
			assets = self.getAllWidgetItem('nonCache_listWidget')

		else : 
			if self.ui.nonCache_listWidget.selectedItems() : 
				assets = [str(asset.text()) for asset in self.ui.nonCache_listWidget.selectedItems()]

		for each in assets : 
			animFilePath = '%s/animCurve/%s.anim' % (nonCachePath, each)
			ctrlFilePath = '%s/animCurve/%s.txt' % (nonCachePath, each)

			if os.path.exists(animFilePath) and os.path.exists(ctrlFilePath) : 
				ctrls = eval(fileUtils.readFile(ctrlFilePath))

				# select ctrl
				mc.select(ctrls)

				# apply animImport
				mm.eval('file -import -type "animImport" -ra true -options "targetTime=4;copies=1;option=replace;pictures=0;connect=0;"  -pr -loadReferenceDepth "all" "%s";' % animFilePath)

	

	def applyRenderAnimCurve(self, assetName) : 
		info = self.cacheCommand.info()
		animCurvePath = info['animCurvePath']
		

		animFilePath = '%s/%s.anim' % (animCurvePath, assetName)
		ctrlFilePath = '%s/%s.txt' % (animCurvePath, assetName)

		if os.path.exists(animFilePath) and os.path.exists(ctrlFilePath) : 
			ctrls = eval(fileUtils.readFile(ctrlFilePath))

			# select ctrl
			mc.select(ctrls)

			# apply animImport
			mm.eval('file -import -type "animImport" -ra true -options "targetTime=4;copies=1;option=replace;pictures=0;connect=0;"  -pr -loadReferenceDepth "all" "%s";' % animFilePath)	


	def importNonCacheAsset(self) : 
		info = self.cacheCommand.info()
		setPath = info['nonCachePath']
		mc.file(setPath,  i = True, type = 'mayaAscii', options = 'v=0', pr = True, loadReferenceDepth = 'all')
		# mc.file(setPath, r = True, type = 'mayaAscii', ignoreVersion = True, gl = True, loadReferenceDepth = 'all', namespace = 'nonCache', options = 'v=0')

		self.setStatusBuildNonCacheAsset_pushButton()


	def importCamera(self) : 
		info = self.cacheCommand.info()
		cameraPath = info['cameraPath']
		mc.file(cameraPath,  i = True, type = 'mayaAscii', options = 'v=0', pr = True, loadReferenceDepth = 'all')
		# mc.file(cameraPath, r = True, type = 'mayaAscii', ignoreVersion = True, gl = True, loadReferenceDepth = 'all', namespace = 'camera', options = 'v=0')

		# set resolution
		self.cacheCommand.setRenderResolution()

		mayaTools.fixSequencer()

		# set pushButton stage

		self.setStatusGetCamera_pushButton()

		# set time slier range

		self.cacheCommand.setRange()


	def importAsset(self) : 
		info = self.cacheCommand.info()
		exportAssetPath = info['exportAssetPath']

		if os.path.exists(exportAssetPath) : 
			mc.file(exportAssetPath,  i = True, type = 'mayaAscii', options = 'v=0', pr = True, loadReferenceDepth = 'all')

			self.setStatusImportAsset_pushButton()


	def getAllWidgetItem(self, listWidget) : 
		cmd = 'self.ui.%s.count()' % (listWidget)
		count = int(eval(cmd))
		allItems = []

		for i in range(count) : 
			tmpCmd = 'self.ui.%s.item(%s).text()' % (listWidget, i)
			item = str(eval(tmpCmd))
			allItems.append(item)

		return allItems


	# shotgun section
	def setShotgun(self) : 
		from sg import utils as sgUtils
		reload(sgUtils)

		info = self.cacheCommand.info()
		projName = info['project']
		episode = info['episode']
		sequenceName = info['sequence']
		shotName = info['shot']
		pipeline = 'TechAnim'
		taskName = 'buildScene'
		status = 'aprv'
		result = sgUtils.sgUpdateShotTaskStatus2(projName, episode, sequenceName, shotName, pipeline, taskName, status)

		# save scene
		mc.file(save = True)
		print 'Scene saved.'
		self.setStatusShotgun_pushButton()

		return result


	def doReportProblem(self) : 
		
		reload(openNoteCore)
		if mc.window('OpenNoteWindows', exists = True) : 
			mc.deleteUI('OpenNoteWindows')

		openNoteCore.mode = 'import cache'
		a = openNoteCore.MyForm(openNoteCore.getMayaWindow())
		a.show()


# ==================================================================

	def setStatusAsset_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.rebuildAsset_pushButton.setIcon(icon)
			self.ui.rebuildAsset_pushButton.setText('1. Rebuild Asset')


	def setStatusImportCache_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.importCache_pushButton.setIcon(icon)
			self.ui.importCache_pushButton.setText('2. Import / Update Cache')


	def setStatusBuildSet_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.buildSet_pushButton.setIcon(icon)
			self.ui.buildSet_pushButton.setText('3. Build Set')


	def setStatusBuildNonCacheAsset_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.buildNonCache_pushButton.setIcon(icon)
			self.ui.buildNonCache_pushButton.setText('Build Non Cache Asset')


	def setStatusGetCamera_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.getCamera_pushButton.setIcon(icon)
			self.ui.getCamera_pushButton.setText('4. Get Camera')


	def setStatusShotgun_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.sg_pushButton.setIcon(icon)
			self.ui.sg_pushButton.setText('6. Set Cache Status to "aprv"')


	def setIconReportProblem_pushButton(self) : 
		if os.path.exists(self.techAnimIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.techAnimIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.reportProblem_pushButton.setIcon(icon)
			self.ui.reportProblem_pushButton.setText('')
			self.ui.reportProblem_pushButton.setIconSize(QtCore.QSize(70, 70))


	def setStatusImportAsset_pushButton(self) : 
		if os.path.exists(self.okIcon) : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(self.okIcon),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			self.ui.importAsset_pushButton.setIcon(icon)
			self.ui.importAsset_pushButton.setText('Import Crowd')


# ==================================================================


	def insertRow(self, row, height) : 
		self.ui.asset_tableWidget.insertRow(row)
		self.ui.asset_tableWidget.setRowHeight(row, height)


	def fillInTable(self, row, column, text, color = [1, 1, 1]) : 
		item = QtGui.QTableWidgetItem()
		item.setText(text)
		item.setBackgroundColor(QtGui.QColor(color[0], color[1], color[2]))
		self.ui.asset_tableWidget.setItem(row, column, item)


	def fillInTableIcon(self, row, column, text, iconPath, color = [1, 1, 1]) : 
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)

		item = QtGui.QTableWidgetItem()
		item.setText(str(text))
		item.setIcon(icon)
		item.setBackgroundColor(QtGui.QColor(color[0], color[1], color[2]))
		
		self.ui.asset_tableWidget.setItem(row, column, item)


	def runAssetManager(self) : 
		sys.path.append('O:/systemTool/python/assetManager')
		from assetManager import main as am
		reload(am)
		if mc.window('assetmanagerWindow', exists = True) : 
		    mc.deleteUI('assetmanagerWindow')
		myapp = am.MyForm(am.getMayaWindow())
		myapp.show()




class cmd() : 
	def __init__(self) : 
		self.dbPath = str()
		self.heroCachePath = str()
		self.cachePath = str()
		self.referenceDBPath = str()
		self.referenceDB = dict()

		# custom variable
		self.project = str()
		self.episode = str()
		self.sequence = str()
		self.shot = str()
		self.projectCode = str()
		self.episodeCode = str()
		self.cacheRawPath = str()
		self.backupCache = str()
		self.logPath = str()
		self.heroCacheLog = str()
		self.drive = 'P:/'
		self.setPath = str()
		self.nonCachePath = str()
		self.cameraPath = str()
		self.cameraLogPath = str()
		self.assetLogPath = str()
		self.playblastPath = str()
		self.animCurvePath = str()

		self.setPathInfo()


	def setPathInfo(self, project='', episode='', sequence='', shot='', readFromScene=1) : 
		try : 
			shotLevel = '' 
			currentLevel = ''
			animLevel = ''
			if readFromScene == 1 : 
				shotLevel = getInfo.ptPipelineSceneInfo('shotDirPath')
				currentLevel = os.path.join(shotLevel, 'animClean')
				project = getInfo.ptPipelineSceneInfo('project')
				episode = getInfo.ptPipelineSceneInfo('episode')
				sequence = getInfo.ptPipelineSceneInfo('sequence')
				shot = getInfo.ptPipelineSceneInfo('shot')
				animLevel = os.path.join(shotLevel, 'anim')

			else : 
				shotLevel = os.path.join(self.drive, project, 'film', episode, sequence, shot)
				currentLevel = os.path.join(shotLevel, 'animClean')
				animLevel = os.path.join(shotLevel, 'anim')

			projectInfo = info.project(project)
			projectCode = projectInfo.code()
			episodeInfo = info.episode(project, episode)
			episodeCode = episodeInfo.code()

			dbFile = '%s_%s_%s_%s_assetCache.txt' % (projectCode, episodeCode, sequence, shot)
			heroCacheFile = '%s_%s_%s_%s_heroCache.txt' % (projectCode, episodeCode, sequence, shot)
			referenceDBFile = '%s_%s_%s_%s_referenceDB.txt' % (projectCode, episodeCode, sequence, shot)
			setFile = '%s_%s_%s_%s_set.ma' % (projectCode, episodeCode, sequence, shot)
			cameraFile = '%s_%s_%s_%s_camera.ma' % (projectCode, episodeCode, sequence, shot)
			cameraLogFile = '%s_%s_%s_%s_cameraLog.txt' % (projectCode, episodeCode, sequence, shot)
			assetLogFile = '%s_%s_%s_%s_assetInfo.txt' % (projectCode, episodeCode, sequence, shot)
			nonCacheFile = '%s_%s_%s_%s_nonCache.ma' % (projectCode, episodeCode, sequence, shot)
			playblastFile = '%s_%s_%s_%s_anim.mov' % (projectCode, episodeCode, sequence, shot)
			exportAssetFile = '%s_%s_%s_%s_exportAsset.ma' % (projectCode, episodeCode, sequence, shot)


			dbPath = os.path.join(currentLevel, 'cache', 'data', dbFile)
			heroCachePath = os.path.join(currentLevel, 'cache', 'data', heroCacheFile)
			referenceDBPath = os.path.join(currentLevel, 'cache', 'data', referenceDBFile)
			setPath = os.path.join(currentLevel, 'cache', 'set', setFile)
			nonCachePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'nonCacheAsset', nonCacheFile), '/')
			cameraPath = os.path.join(currentLevel, 'cache', 'camera', cameraFile)
			cameraLogPath = os.path.join(currentLevel, 'cache', 'camera', cameraLogFile)
			assetLogPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'data', assetLogFile), '/')
			playblastPath = mayaTools.fixPath(os.path.join(animLevel, 'playblast', playblastFile), '/')
			animCurvePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'animCurve'), '/')
			exportAssetPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'exportAsset', exportAssetFile), '/')



			self.setPath = setPath
			self.cameraPath = cameraPath

			self.dbPath = dbPath
			self.heroCachePath = heroCachePath
			self.referenceDBPath = referenceDBPath
			self.cameraLogPath = cameraLogPath
			self.assetLogPath = assetLogPath
			self.nonCachePath = nonCachePath
			self.playblastPath = playblastPath
			self.animCurvePath = animCurvePath
			self.exportAssetPath = exportAssetPath




			self.cachePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'publish'), '/')
			self.referenceDB = self.readAssetReferenceFile()

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
					'heroCacheLog': self.heroCachePath, 
					'referenceDBPath': self.referenceDBPath,
					'setPath': self.setPath, 
					'cameraPath': self.cameraPath, 
					'cameraLogPath': self.cameraLogPath, 
					'assetLogPath' : self.assetLogPath, 
					'playblastPath': self.playblastPath, 
					'nonCachePath': self.nonCachePath, 
					'animCurvePath': self.animCurvePath, 
					'exportAssetPath': self.exportAssetPath
		}

		return tmpData


	def readHeroCache(self) : 
		if os.path.exists(self.heroCachePath) : 
			return eval(fileUtils.readFile(self.heroCachePath))

		else : 
			return None

	def readAssetReferenceFile(self, lod = 'Cache') : 
		renderAssets = dict()

		if os.path.exists(self.referenceDBPath) : 
			assetReferences = eval(fileUtils.readFile(self.referenceDBPath))

			for each in assetReferences : 
				path = assetReferences[each]
				basename = os.path.basename(path)
				lodType = basename.split('.')[0].split('_')[-1]

				renderPath = path.replace(lodType, lod)

				renderAssets[each] = renderPath

			return renderAssets

		else : 
			return None


	def readCameraLog(self) : 
		cameraLog = dict()

		if os.path.exists(self.cameraLogPath) : 
			cameraLog = eval(fileUtils.readFile(self.cameraLogPath))

			return cameraLog


	def setRange(self) : 
		cameraLog = self.readCameraLog()
		ranges = []
		min = float()
		max = float()

		if cameraLog : 
			for each in cameraLog : 
				min = cameraLog[each][0]
				max = cameraLog[each][1]

				ranges.append(min)
				ranges.append(max)

			min, max = calculate.minMax(ranges)

			mc.playbackOptions(min = min, max = max)




	def buildAsset2(self, lists) : 
		skip = dict()
		for each in lists : 
			namespace = each
			path = self.referenceDB[each]

			if os.path.exists(path) : 
				result = mc.file(path, reference = True, ignoreVersion = True, gl = True, loadReferenceDepth = 'all', namespace = each, options = 'v=0')

			else : 
				skip[each] = path


	def buildAsset(self, lists, lod = 'cache') : 
		skip = dict()
		assetDB = self.readAssetReferenceFile(lod)

		for each in lists : 
			namespace = each
			path = assetDB[each].split('{')[0]

			if os.path.exists(path) : 
				result = mc.file(path, reference = True, ignoreVersion = True, gl = True, loadReferenceDepth = 'all', namespace = each, options = 'v=0')
				print 'Build %s' % each

			else : 
				skip[each] = path


		return skip 
			

	def applyCache(self, lists, inputCachePath) : 
		skipCache = dict()
		info = self.info()
		assetInfoPath = info['assetLogPath']

		for each in lists : 
			print 'asset %s' % each
			# cachePath = mayaTools.fixPath(os.path.join(self.cachePath, versionDir, each), '/')
			cachePath = mayaTools.fixPath(os.path.join(inputCachePath, each), '/')
			cacheFiles = fileUtils.listFile(cachePath, 'mdd')

			print 'cache path %s' % cachePath

			missingGeo = []

			for eachCache in cacheFiles : 
				basename = eachCache.split('.')[0]

				# get cache path
				cacheFile = os.path.join(cachePath, eachCache)

				# olivia_body.mdd
				# frd_paperA_frd_paper_ply.mmd
				# mesh = basename.replace('%s_' % each, '')
				mesh = mayaTools.replaceString(basename, '%s_' % each, '')

				# olivia:body
				# frd_paperA:frd_paper_ply
				applyMesh = '%s:%s' % (each, mesh)

				# apply PO node

				if mc.objExists(applyMesh) : 
					node, status = self.applyPOReader(applyMesh)
					mc.setAttr('%s.FilePath' % node[0], cacheFile, type = 'string')

				else : 
					# looking in db first 
					assetInfo = eval(fileUtils.readFile(assetInfoPath))
					print 'Cache file %s' % basename

					if basename in assetInfo.keys() : 
						applyMesh = assetInfo[basename]
						print 'apply mesh %s' % applyMesh

						if mc.objExists(applyMesh) : 
							node, status = self.applyPOReader(applyMesh)
							mc.setAttr('%s.FilePath' % node[0], cacheFile, type = 'string')

						# if missing, add to missing list
						else : 
							missingGeo.append(applyMesh)

					# if still missing, declare as missing geo
					else : 

						missingGeo.append(applyMesh)


			skipCache[each] = missingGeo

		# skip apply cache
		print '================================================================================'

		total = 0

		for each in skipCache : 

			for eachGeo in skipCache[each] : 
				print 'skip %s' % eachGeo

				total+=1

		print '================================================================================'
		print 'Geometry not found %s object' % (total)

		if total : 
			for each in skipCache : 
				print '%s cache will not apply' % (each)



	def applyPOReader2(self, obj) : 
		name = '%s_PO_Reader' % obj
		if mc.objExists(name) : 
			mc.delete(name)

			print 'Delete Existing node %s.' % name

		deformer = mc.deformer(obj, type = 'PO_Reader', n = name)
		mc.connectAttr('time1.outTime', '%s.tmd' % deformer[0])

		print 'Apply PO Reader to %s' % obj

		return deformer


	def applyPOReader(self, obj) : 
		# check valid naming, remove | if any
		objName = obj
		if '|' in obj : 
			objName = obj.replace('|', '_').replace(':', '_')

		name = '%s_PO_Reader' % objName
		if not mc.objExists(name) : 
			# mc.delete(name)

		# print 'Delete Existing node %s.' % name

			deformer = mc.deformer(obj, type = 'PO_Reader', n = name)
			mc.connectAttr('time1.outTime', '%s.tmd' % deformer[0])

			print 'Apply PO Reader to %s' % obj

			return deformer, True

		else : 
			print 'Node exists %s ...Updade node' % name 
			return [name], False


	def listAllPOReader(self) : 
		POs = mc.ls(type = 'PO_Reader')
		datas = dict()
		namespaces = []
		nodes = []
		invalidNode = []

		if POs : 
			for each in POs : 
				if ':' in each : 
					namespace = each.split(':')[0]
					poNode = each
					path = mc.getAttr('%s.FilePath' % poNode)
					version = getInfo.findVersionFromPath(path, 'v', 3)

					tmpDict = {each:{'path': path, 'version': version}}

					if namespace in datas.keys() : 		
						datas[namespace][each] = {'path': path, 'version': version}
						# datas[namespace].update({each: {'path': path, 'version': version}})

					else :
						datas[namespace] = tmpDict
						# datas.update({namespace: tmpDict})

				else : 
					invalidNode.append(each)

			return datas

		else : 
			return None


	def removePOINode(self, obj) : 
		# obj = 'frd_genericWomanB:Rig_Grp'
		intermediateObjects = []
		nodes = mc.listRelatives(obj, f = True, ad = True)

		for each in nodes : 
			if mc.objectType(each, isType = 'mesh') : 
				PO_readers = mc.listConnections(each, t = 'PO_Reader')
				
				if PO_readers : 
					for eachNode in PO_readers : 
						mc.delete(eachNode)

				if not mc.referenceQuery(each, inr = True) : 
					if not each in intermediateObjects : 
						intermediateObjects.append(each)

		if intermediateObjects : 
			mc.delete(intermediateObjects)


	def checkSwitchingAsset(self, namespace, refAsset) : 
		rigGrp = '%s:Rig_Grp' % namespace
		assetPath = None

		if mc.objExists(rigGrp) : 
			path = mayaTools.getReferencePath(rigGrp)
			basename = os.path.basename(path)
			assetType = basename.split('.')[0].split('_')[-1]
			refPath = path.replace('/%s' % basename, '')

			# list all assetTypes
			allFiles = fileUtils.listFile(refPath, 'mb')

			for eachFile in allFiles : 
				level = eachFile.split('.')[0].split('_')[-1]

				if level == refAsset : 
					assetPath = '%s/%s' % (refPath, eachFile)

					break

		return assetPath


	def checkAnimCurve(self, namespace) : 
		info = self.info()
		animCurvePath = info['animCurvePath']
		animFile = '%s.anim' % namespace
		selectionFile = '%s.txt' % namespace

		if os.path.exists('%s/%s' % (animCurvePath, animFile)) and os.path.exists('%s/%s' % (animCurvePath, selectionFile)) : 
			return True



	def setRenderResolution(self) : 
		# set to 1080 HD
		mc.setAttr('defaultResolution.width', 1920)
		mc.setAttr('defaultResolution.height', 1080)
		mc.setAttr('defaultResolution.deviceAspectRatio', 1.777)
		mc.setAttr('defaultResolution.pixelAspect', 1)


	def loadPlugin(self) : 
		checkPlugin = ['PO_LWO_IO_v2012_64', 'PO_ParticleExport_v2012_64', 'PO_Reader_v2012_64', 'PO_Import_PSC_v2012_64', 'PO_ScriptTools_v2012_64', 'PO_Baker_v2012_64', 'animImportExport']
		loadPlugins = mc.pluginInfo(q = True, listPlugins = True)

		for each in checkPlugin : 
			if not each in loadPlugins : 

				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_Baker_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_Import_PSC_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_LWO_IO_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_ParticleExport_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_Reader_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "O:/globalMaya/Plugins/PO_ScriptTools_v2012_64.mll"`);')
				mm.eval('catch(`loadPlugin "C:/Program Files/Autodesk/Maya2012/bin/plug-ins/animImportExport.mll"`);')	
				loadPlugins = mc.pluginInfo(q = True, listPlugins = True)