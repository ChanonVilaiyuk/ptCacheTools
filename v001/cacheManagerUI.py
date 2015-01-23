# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'O:\systemTool\python\ptCacheTools\cacheManagerUI.ui'
#
# Created: Thu Oct 17 15:29:51 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_cacheManagerWindow(object):
    def setupUi(self, cacheManagerWindow):
        cacheManagerWindow.setObjectName(_fromUtf8("cacheManagerWindow"))
        cacheManagerWindow.resize(472, 633)
        self.centralwidget = QtGui.QWidget(cacheManagerWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(10, 20, 431, 571))
        self.frame_2.setFrameShape(QtGui.QFrame.Box)
        self.frame_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.cache_pushButton = QtGui.QPushButton(self.frame_2)
        self.cache_pushButton.setGeometry(QtCore.QRect(10, 520, 411, 41))
        self.cache_pushButton.setObjectName(_fromUtf8("cache_pushButton"))
        self.tableWidget = QtGui.QTableWidget(self.frame_2)
        self.tableWidget.setGeometry(QtCore.QRect(10, 100, 411, 361))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(160)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.frame_3 = QtGui.QFrame(self.frame_2)
        self.frame_3.setGeometry(QtCore.QRect(10, 470, 411, 41))
        self.frame_3.setFrameShape(QtGui.QFrame.Box)
        self.frame_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.label_7 = QtGui.QLabel(self.frame_3)
        self.label_7.setGeometry(QtCore.QRect(20, 10, 81, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.comboBox = QtGui.QComboBox(self.frame_3)
        self.comboBox.setGeometry(QtCore.QRect(110, 10, 81, 22))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.overrideOutput_checkBox_2 = QtGui.QCheckBox(self.frame_3)
        self.overrideOutput_checkBox_2.setGeometry(QtCore.QRect(320, 10, 91, 17))
        self.overrideOutput_checkBox_2.setObjectName(_fromUtf8("overrideOutput_checkBox_2"))
        self.label_11 = QtGui.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_11.setFont(font)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.output_lineEdit = QtGui.QLineEdit(self.frame_2)
        self.output_lineEdit.setGeometry(QtCore.QRect(10, 30, 411, 20))
        self.output_lineEdit.setText(_fromUtf8(""))
        self.output_lineEdit.setObjectName(_fromUtf8("output_lineEdit"))
        self.cacheSelected_pushButton_4 = QtGui.QPushButton(self.frame_2)
        self.cacheSelected_pushButton_4.setGeometry(QtCore.QRect(290, 60, 131, 31))
        self.cacheSelected_pushButton_4.setObjectName(_fromUtf8("cacheSelected_pushButton_4"))
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(20, 610, 46, 16))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.status_label = QtGui.QLabel(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(90, 610, 201, 16))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.status_label.setFont(font)
        self.status_label.setObjectName(_fromUtf8("status_label"))
        cacheManagerWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(cacheManagerWindow)
        QtCore.QMetaObject.connectSlotsByName(cacheManagerWindow)

    def retranslateUi(self, cacheManagerWindow):
        cacheManagerWindow.setWindowTitle(QtGui.QApplication.translate("cacheManagerWindow", "PT Cache Manager v.1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.cache_pushButton.setText(QtGui.QApplication.translate("cacheManagerWindow", "Import All Cache", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("cacheManagerWindow", "Cache", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("cacheManagerWindow", "Assign Object", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("cacheManagerWindow", "Check", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("cacheManagerWindow", "Namespace : ", None, QtGui.QApplication.UnicodeUTF8))
        self.overrideOutput_checkBox_2.setText(QtGui.QApplication.translate("cacheManagerWindow", "Selected Only", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("cacheManagerWindow", "Input Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.cacheSelected_pushButton_4.setText(QtGui.QApplication.translate("cacheManagerWindow", "Read", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("cacheManagerWindow", "Status : ", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("cacheManagerWindow", "-", None, QtGui.QApplication.UnicodeUTF8))

