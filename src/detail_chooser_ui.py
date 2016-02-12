# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'detail_chooser.ui'
#
# Created: Sat Sep 20 12:30:49 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from crop_area_label import crop_area_label as crop_area_label

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

class Ui_widget(object):
    def setupUi(self, widget):
        widget.setObjectName(_fromUtf8("widget"))
        widget.resize(451, 506)
        self.horizontalLayout_4 = QtGui.QHBoxLayout(widget)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.crop_area = crop_area_label(parent=self)
        self.crop_area.setScaledContents(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.crop_area.sizePolicy().hasHeightForWidth())
        self.crop_area.setSizePolicy(sizePolicy)
        self.crop_area.setFrameShape(QtGui.QFrame.StyledPanel)
        self.crop_area.setObjectName(_fromUtf8("crop_area"))

        self.scrollarea = QtGui.QScrollArea()
        self.scrollarea.setWidget(self.crop_area)
        self.scrollarea.setWidgetResizable(True)

        #self.verticalLayout_2.addWidget(self.crop_area)
        self.verticalLayout_2.addWidget(self.scrollarea)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.sldr_zoom = QtGui.QSlider(widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sldr_zoom.sizePolicy().hasHeightForWidth())
        self.sldr_zoom.setSizePolicy(sizePolicy)
        self.sldr_zoom.setMinimumSize(QtCore.QSize(40, 20))
        self.sldr_zoom.setMaximumSize(QtCore.QSize(16777214, 20))
        self.sldr_zoom.setMinimum(10)
        self.sldr_zoom.setMaximum(200)
        self.sldr_zoom.setOrientation(QtCore.Qt.Horizontal)
        self.sldr_zoom.setObjectName(_fromUtf8("sldr_zoom"))
        self.horizontalLayout_2.addWidget(self.sldr_zoom)
        #spacerItem99 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.horizontalLayout_2.addSpacerItem(spacerItem99)
        self.lcd_zoom = QtGui.QLCDNumber(widget)
        self.lcd_zoom.setMinimumSize(QtCore.QSize(50, 20))
        self.lcd_zoom.setMaximumSize(QtCore.QSize(50, 20))
        self.lcd_zoom.setObjectName(_fromUtf8("lcd_zoom"))
        #self.spinBox = QtGui.QSpinBox()
        #self.spinBox.setMaximum(200)
        #self.spinBox.setMinimum(10)

        self.horizontalLayout_2.addWidget(self.lcd_zoom)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tB_crop = QtGui.QToolButton(widget)
        self.tB_crop.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_crop.setObjectName(_fromUtf8("tB_crop"))
        self.verticalLayout.addWidget(self.tB_crop)
        self.tB_undo = QtGui.QToolButton(widget)
        self.tB_undo.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_undo.setObjectName(_fromUtf8("tB_undo"))
        self.verticalLayout.addWidget(self.tB_undo)
        self.tB_bnw = QtGui.QToolButton(widget)
        self.tB_bnw.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_bnw.setObjectName(_fromUtf8("tB_bnw"))
        self.verticalLayout.addWidget(self.tB_bnw)

        self.tB_rotate = QtGui.QToolButton(widget)
        self.tB_rotate.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_rotate.setObjectName(_fromUtf8("tB_rotate"))
        self.verticalLayout.addWidget(self.tB_rotate)
        self.tB_flipH = QtGui.QToolButton(widget)
        self.tB_flipH.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_flipH.setObjectName(_fromUtf8("tB_flipH"))
        self.verticalLayout.addWidget(self.tB_flipH)
        self.tB_flipV = QtGui.QToolButton(widget)
        self.tB_flipV.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_flipV.setObjectName(_fromUtf8("tB_flipV"))
        self.verticalLayout.addWidget(self.tB_flipV)
        self.tB_whiteToTransparent = QtGui.QToolButton(widget)
        self.tB_whiteToTransparent.setMinimumSize(QtCore.QSize(30, 30))
        self.tB_whiteToTransparent.setObjectName(_fromUtf8("tB_flipV"))
        self.verticalLayout.addWidget(self.tB_whiteToTransparent)

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pB_ok = QtGui.QPushButton(widget)
        self.pB_ok.setObjectName(_fromUtf8("pB_ok"))
        self.horizontalLayout.addWidget(self.pB_ok)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pB_nok = QtGui.QPushButton(widget)
        self.pB_nok.setObjectName(_fromUtf8("pB_nok"))
        self.horizontalLayout.addWidget(self.pB_nok)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.retranslateUi(widget)
        QtCore.QObject.connect(self.sldr_zoom, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.lcd_zoom.display)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        widget.setWindowTitle(_translate("widget", "Detail-Chooser", None))
        self.crop_area.setText(_translate("widget", "TextLabel", None))
        self.tB_crop.setText(_translate("widget", "crop", None))
        self.tB_undo.setText(_translate("widget", "undo", None))
        self.tB_bnw.setText(_translate("widget", "BnW", None))
        self.pB_ok.setText(_translate("widget", "Fertig", None))
        self.pB_nok.setText(_translate("widget", "Abbrechen", None))
