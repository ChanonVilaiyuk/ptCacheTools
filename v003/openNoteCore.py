import os, sys, sip, subprocess, shutil
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime
from PyQt4 import QtCore, QtGui

#Import GUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#Custom import modules
from tools import fileUtils, mayaTools, getInfo, info, calculate, emailUtil

reload(fileUtils)
reload(emailUtil)

reload(mayaTools)

reload(getInfo)
reload(info)
reload(calculate)

from ptCacheTools import cacheOpenNote as ui
reload(ui)


# If inside Maya open Maya GUI
def getMayaWindow() : 
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

import maya.OpenMayaUI as mui
getMayaWindow()

mode = 'export cache'


class MyForm(QtGui.QMainWindow) : 
	def __init__(self, parent=None) : 

		# Setup Window
		QtGui.QWidget.__init__(self, parent)
		self.ui = ui.Ui_OpenNoteWindows()
		self.ui.setupUi(self)

		#custom variable

		# 72 = pipeline
		self.userID = 72


		# send email to TA, OB, Nong
		self.receivers = 'ta,ob'
		self.receiver_emails = 'ta@picturethisanimation.com,ob@picturethisanimation.com'
		
		if mode == 'export cache' : 
			self.sender = 'Export Cache Problem'
			self.problemList = ['Last time Maya crash', 
								'Error Publish', 
								'Shotgun Error', 
								"I don't know", 
								'Other Problems'
								]

			self.actionList = ['Let techAnim fix', 
								'Need techAnim downstair' 
								]

			self.priorityList = ['No rush', 'Need it next week', 'Need it tomorrow!', 'Need it now!!', 'Need it YESTERDAY!!!']
			self.task = 'cache'
			self.subject = 'Export Cache problem'


		if mode == 'import cache' : 
			self.sender = 'Build Scene Problem'
			self.problemList = ['No Cache Asset', 
								'Vertex Explode', 
								'Cache not move', 
								'Cannot switch set', 
								'Wrong animation',
								"I don't know", 
								'Other Problems'
								]

			self.actionList = ['Let techAnim fix', 
								'Need techAnim downstair' 
								]

			self.priorityList = ['No rush', 'Need it next week', 'Need it tomorrow!', 'Need it now!!', 'Need it YESTERDAY!!!']
			self.task = 'buildScene'
			self.subject = 'Import Cache problem'


		self.fillUI()
		self.initConnection()


	def fillUI(self) : 

		self.fillProjectInfo()
		self.fillComboBox()
		self.getUser()
		self.ui.cache_label.setText(self.task)
		self.ui.openNote_plainTextEdit.appendPlainText('No Detail')


	def initConnection(self) : 
		self.ui.submit_pushButton.clicked.connect(self.submit)


	def fillProjectInfo(self) : 

		info = getInfo.shot()
		self.project = info.project()
		self.episode = info.episode()
		self.sequence = info.sequence()
		self.shot = info.shot()
		self.department = info.department()

		self.ui.project_label.setText(self.project)
		self.ui.episode_label.setText(self.episode)
		self.ui.sequence_label.setText(self.sequence)
		self.ui.shot_label.setText(self.shot)


	def getUser(self) : 
		user = mc.optionVar(q = 'PTuser')
		self.ui.from_lineEdit.setText(user)


	def fillComboBox(self) : 

		for each in self.problemList : 
			self.ui.problem_comboBox.addItem(each)


		for each in self.actionList : 
			self.ui.action_comboBox.addItem(each)


		for each in self.priorityList : 
			self.ui.priority_comboBox.addItem(each)



	def submit(self) : 
		problem = str(self.ui.problem_comboBox.currentText())
		action = str(self.ui.action_comboBox.currentText())
		priority = str(self.ui.priority_comboBox.currentText())
		note = str(self.ui.openNote_plainTextEdit.toPlainText())

		technicalInfo = self.getTechnicalInfo()
		user = str(self.ui.from_lineEdit.text())
		subject = '%s:%s' % (self.subject, priority)
		emailSubject = '%s:%s on %s-%s-%s-%s' % (self.subject, priority, self.project, self.episode, self.sequence, self.shot)
		body = self.arrangeNote(problem, action, priority, note, user, technicalInfo)


		# print problem, action, priority, note, user

		result = self.messageBox('Confirm Submit', 'You are about to submit the following message \n%s' % body)

		if result == QMessageBox.Ok : 

			# shotgun openNote
			if self.ui.shotgun_checkBox.isChecked() : 
				self.shotgunNote(self.project, self.episode, self.sequence, self.shot, self.task, self.userID, subject, body) 

			# send email
			if self.ui.email_checkBox.isChecked() : 
				self.sendEmail(self.sender, '', self.receivers, self.receiver_emails, emailSubject, body)

			self.completeDialog('Complete', 'Open Note successfully submited to Shotgun')


	def getTechnicalInfo(self) : 
		currentScene = mc.file(q = True, sn = True)
		refs = mayaTools.getAllReferences()

		data = '%s\n' % currentScene
		data += '%s\n' % str(refs)

		return data


	def shotgunNote(self, projName, episode, sequenceName, shotName, taskName, userID, subject, body) : 
		from sg import utils as sgUtils
		reload(sgUtils) 

		result = sgUtils.sgCreateShotNote(projName, episode, sequenceName, shotName, taskName, userID, subject, body)

		return result


	def sendEmail(self, sender, senderEmail, receivers, receiver_emails, subject, message) : 
		emailUtil.sendEmail(sender, senderEmail, receivers, receiver_emails, subject, message)

		return True


	def arrangeNote(self, problem, action, priority, note, user, technicalInfo) : 
		body = '%s\n' % priority
		body += '==================\n'
		body += '%s need techAnim to fix\n' % user
		body += '%s, ' % self.project
		body += '%s, ' % self.episode
		body += '%s, ' % self.sequence
		body += '%s \n' % self.shot
		body += '==================\n'
		body += 'Problem is : %s\n' % problem
		body += 'Details : \n'
		body += '%s\n' % note
		body += '==================\n'
		body += 'TechnicalInfo : \n%s' % technicalInfo
		body += '==================\n'

		return body


	def completeDialog(self, title, description) : 
		result = QtGui.QMessageBox.information(self, title, description ,QMessageBox.AcceptRole, QMessageBox.Ok)

		return result

	def messageBox(self, title, description) : 
		result = QtGui.QMessageBox.warning(self,title,description ,QMessageBox.AcceptRole, QMessageBox.Ok, QMessageBox.Cancel)

		return result