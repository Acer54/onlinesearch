#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
#################detail_chooser.py#####################################
######################################################################
# Input = Path to a picture
# Return = Path to the reworked picture
######################################################################

#######################################################################
# Open Issues:
#
#######################################################################

import sys
import res

from detail_chooser_ui import Ui_widget as ui

from PyQt4.QtCore import *
from PyQt4.QtGui import *



def main(argv):
    app = QApplication(argv)
    print(argv[1])
    mainwindow = detail_chooser_DLG(argv[1])               # eigene Window-Klasse
    mainwindow.show()
    sys.exit(app.exec_())


class detail_chooser_DLG(QDialog, ui):

    __version__ = "0.1.1"

    def __init__(self, picturepath=None, parent=None):
        super(detail_chooser_DLG, self).__init__(parent)
        self.setupUi(self)
        self.sldr_zoom.setPageStep(1)
        self.sldr_zoom.setSingleStep(1)
        self.tB_crop.setIcon(QIcon(":/crop.png"))
        self.tB_crop.setToolTip(u"Zuschneiden")

        self.tB_undo.setIcon(QIcon(":/undo.png"))
        self.tB_undo.setEnabled(False)
        self.tB_undo.setToolTip(u"Rückgängig")

        self.tB_bnw.setIcon(QIcon(":/blackwhite.png"))
        self.tB_bnw.setToolTip(u"in Schwarz / Weiß Bild umwandeln")

        self.tB_rotate.setIcon(QIcon(":/rotate.png"))
        self.tB_rotate.setToolTip(u"Bild um 90′ drehen")

        self.tB_flipV.setIcon(QIcon(":/flip-vertical.png"))
        self.tB_flipV.setToolTip(u"Bild vertikal spiegeln")

        self.tB_flipH.setIcon(QIcon(":/flip-horizontal.png"))
        self.tB_flipH.setToolTip(u"Bild horizontal spiegeln")

        self.tB_whiteToTransparent.setIcon(QIcon(":/white_to_transparent.png"))
        self.tB_whiteToTransparent.setToolTip(u"Wandelt Weiß zu Transparenz")


        #setup connections
        self.tB_crop.clicked.connect(self.onCrop)
        self.tB_undo.clicked.connect(self.onUndo)
        self.tB_bnw.clicked.connect(self.onBnW)
        self.tB_rotate.clicked.connect(self.onRotate)
        self.tB_flipV.clicked.connect(self.onFlipV)
        self.tB_flipH.clicked.connect(self.onFlipH)
        self.tB_whiteToTransparent.clicked.connect(self.onWhiteToTransparent)

        self.crop_area.crop_area_zoom_level.connect(self.setSliderposition)
        self.scrollarea.horizontalScrollBar().valueChanged.connect(self.crop_area.update)  #avoid some display problems
        self.scrollarea.verticalScrollBar().valueChanged.connect(self.crop_area.update)

        self.crop_area.resized.connect(self.adjustScrollbarH)
        self.crop_area.resized.connect(self.adjustScrollbarV)


        self.crop_area.loadNewPicture.emit(picturepath)
        #self.crop_area.detectFace(self.crop_area.picture)

        self.sldr_zoom.valueChanged.connect(self.crop_area.zoom_image)
        self.pB_ok.clicked.connect(self.onFertig)
        self.pB_nok.clicked.connect(self.onAbbrechen)

    def setSliderposition(self, value):
        """
        :param value: persentage of Zoom-Factor (10 - 200)
        :return: Nothing
        :result: sets the magnification slider to the given value
        """
        print("Setting Zoom-Level Slider to:", value)
        self.sldr_zoom.setValue(value)

    def adjustScrollbarH(self):
        """
        :result: Sets the horizontal scrollbar to the middle of the selected area in the picture (keep it visible)
        """
        total_width = self.crop_area.rect().width()
        visible_width = self.scrollarea.width()
        selected_height_start = self.crop_area.clip_rect.topLeft().x()
        selected_height_end = self.crop_area.clip_rect.topRight().x()


        verfahrweg= round((self.scrollarea.horizontalScrollBar().maximum() *
                           ((float(total_width - (total_width-selected_height_end) -
                                  ((selected_height_end - selected_height_start) /2)) / float(total_width)))))


        self.scrollarea.horizontalScrollBar().setValue(int(verfahrweg))

    def adjustScrollbarV(self):
        """
        :result: Sets the vertical scrollbar to the middle of the selected area in the picture (keep it visible)
        """
        total_height = self.crop_area.rect().height()
        selected_height_start = self.crop_area.clip_rect.topLeft().y()
        selected_height_end = self.crop_area.clip_rect.bottomLeft().y()

        verfahrweg= round((self.scrollarea.verticalScrollBar().maximum() *
                           ((float(total_height - (total_height-selected_height_end) -
                                  ((selected_height_end - selected_height_start) /2)) / float(total_height)))))

        self.scrollarea.verticalScrollBar().setValue(int(verfahrweg))

    def onCrop(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._croped_image()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def onUndo(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._undo()
        self.tB_undo.setEnabled(False)
        QApplication.restoreOverrideCursor()

    def onBnW(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._blackAndWhite()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def onRotate(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._rotateClockwise()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def onWhiteToTransparent(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._whiteToTransparent()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()


    def onFlipV(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._flipVertical()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def onFlipH(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.crop_area._flipHorizontal()
        self.tB_undo.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def onFertig(self):
        """
        :return: the path of the current viewed picture
        """
        print("Fertig")
        self.onCrop()
        self.accept()
        return self.crop_area._getCurrentFilename()

    def onAbbrechen(self):
        """
        :return: False if, the user interupts.
        """
        print("Abbrechen")
        self.reject()
        return False


if __name__ == "__main__":
    main(sys.argv)


