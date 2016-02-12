# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_v3.ui'
#
# Created: Wed Jan  6 11:02:25 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(12)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeView = LM_TreeView(self.splitter)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.groupBox = QtGui.QGroupBox(self.splitter)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.lE_Anzeigename = QtGui.QLineEdit(self.groupBox)
        self.lE_Anzeigename.setObjectName(_fromUtf8("lE_Anzeigename"))
        self.verticalLayout.addWidget(self.lE_Anzeigename)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.lE_Link = QtGui.QLineEdit(self.groupBox)
        self.lE_Link.setObjectName(_fromUtf8("lE_Link"))
        self.verticalLayout_2.addWidget(self.lE_Link)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tB_Screenshot = QtGui.QToolButton(self.groupBox)
        self.tB_Screenshot.setObjectName(_fromUtf8("tB_Screenshot"))
        self.horizontalLayout.addWidget(self.tB_Screenshot)
        self.tB_Openpath = QtGui.QToolButton(self.groupBox)
        self.tB_Openpath.setObjectName(_fromUtf8("tB_Openpath"))
        self.horizontalLayout.addWidget(self.tB_Openpath)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.lbl_PreviewPic = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_PreviewPic.sizePolicy().hasHeightForWidth())
        self.lbl_PreviewPic.setSizePolicy(sizePolicy)
        self.lbl_PreviewPic.setMinimumSize(QtCore.QSize(200, 200))
        self.lbl_PreviewPic.setScaledContents(False)
        self.lbl_PreviewPic.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_PreviewPic.setObjectName(_fromUtf8("lbl_PreviewPic"))
        self.verticalLayout_3.addWidget(self.lbl_PreviewPic)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addWidget(self.splitter)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.pB_NOK = QtGui.QPushButton(self.centralwidget)
        self.pB_NOK.setObjectName(_fromUtf8("pB_NOK"))
        self.horizontalLayout_5.addWidget(self.pB_NOK)
        self.pB_OK = QtGui.QPushButton(self.centralwidget)
        self.pB_OK.setObjectName(_fromUtf8("pB_OK"))
        self.horizontalLayout_5.addWidget(self.pB_OK)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox.setTitle(_translate("MainWindow", "Details:", None))
        self.label.setText(_translate("MainWindow", "Anzeigename:", None))
        self.label_2.setText(_translate("MainWindow", "Link:", None))
        self.tB_Screenshot.setText(_translate("MainWindow", "...", None))
        self.tB_Openpath.setText(_translate("MainWindow", "...", None))
        self.lbl_PreviewPic.setText(_translate("MainWindow", "Bild", None))
        self.pB_NOK.setText(_translate("MainWindow", "Abbrechen", None))
        self.pB_OK.setText(_translate("MainWindow", "Fertig!", None))

from src.LM_classes import LM_TreeView
