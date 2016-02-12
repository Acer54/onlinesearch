#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import random
from wand.image import Image
from wand import color

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class crop_area_label(QLabel):

    loadNewPicture = pyqtSignal(str)
    resized = pyqtSignal()
    crop_area_zoom_level = pyqtSignal(int)

    def __init__(self, picturepath=None, parent=None):

        QLabel.__init__(self)
        self.setStyleSheet("border-image: url(:/background.png);")     # set Backgroung for transparent images not white.

        self.loadNewPicture[str].connect(self.connect_loadNewPicture)
        self.clip_rect = QRect(self.rect())
        self.largest_rect = QRect(self.rect())
        self.dragging = None
        self.moving = False
        self.cropBoarder = 10
        self.gridDistance = 3
        self.picture = None

        self.scrollarea = QScrollArea()
        self.scrollarea.setWidget(self)
        self.scrollarea.setWidgetResizable(True)
        self.picturepath = None
        self.setMouseTracking(True)

    def resizeEvent(self, QResizeEvent):
        #self.event(QResizeEvent)
        print("resized...")
        self.resized.emit()

    def connect_loadNewPicture(self,path, height=None, width=None):

        if self.picturepath is not path:
            print("Load new Picture", path)
            self.picturepath = path
            self.currentFile = path
            self.picture_original = QImage(self.picturepath)


        if (height is None) or (width is None):
            self.picture = self.picture_original.scaledToWidth(self.width()/2, Qt.SmoothTransformation)
            print("After Scaling, Zoomlevel is:", self.zoomlevel())
            self.crop_area_zoom_level.emit(self.zoomlevel())

        else:
            #print(height)
            #print(width)
            self.picture = self.picture_original.scaled(width, height)
            #self.crop_area_zoom_level.emit(self.zoomlevel())
            print("After Scaling for specific, Zoomlevel is:", self.zoomlevel())

        self.setFixedSize(self.picture.size())

        self.largest_rect = QRect(self.rect())
        #self.clip_rect = QRect(self.rect())
        #print("clip_rect", self.clip_rect)

    def zoom_image(self, factor=100):

        ratio = float(float(self.picture_original.height()) / float(self.picture_original.width()))
        xBreite_markiert = float(self.clip_rect.width()) / float(self.rect().width())
        #print(xBreite_markiert)  # 0.456102783726 der gesamten Breite ist markiert (45%)

        xStartPunkt_markiert = float(self.clip_rect.x()) / float(self.rect().width())
        #print(xStartPunkt_markiert) #die markierung startet bei 0.316916488223 (31%)

        yStartPunkt_markiert = float(self.clip_rect.y()) / float(self.rect().height())
        #print(yStartPunkt_markiert) #die markierung startet bei 0.316916488223 (31%)

        xEndPunkt_markiert = float(self.clip_rect.topRight().x()) / float(self.rect().width())
        #print(xEndPunkt_markiert)  # bei 0.756102783726 der gesamten Breite ist Markierungsende (75%)

        yEndPunkt_markiert = float(self.clip_rect.bottom()) / float(self.rect().height())
        #print(yEndPunkt_markiert) #die markierung endet bei 0.65....(65%, von oben)
        #height = round(self.picture_original.height() * factor / 100)
        width = round(self.picture_original.width() * factor / 100)
        height = round(width * ratio)
        self.connect_loadNewPicture(self.picturepath, height, width)
        #restore selection rect

        self.clip_rect.setTopLeft(QPoint((round(self.rect().width() * xStartPunkt_markiert)),
                                         (round(self.rect().height() * yStartPunkt_markiert))))

        self.clip_rect.setBottomRight(QPoint((round(self.rect().width() * xEndPunkt_markiert)),
                                             (round(self.rect().height() * yEndPunkt_markiert))))

    @pyqtSlot()
    def _croped_image(self):
        print("save image")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        newPicture = self.picture.copy(self.clip_rect)
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)
        extension = "jpg"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)
        newPicture.save(newFile)
        self.clip_rect = QRect(self.rect())
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile

        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)

        self.repaint()

    @pyqtSlot()
    def _undo(self):
        self.loadNewPicture.emit(self.lastFile)
        self.currentFile = self.lastFile
        self.repaint()

    @pyqtSlot()
    def _blackAndWhite(self):
        print("black and white image")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        newPicture = self.picture.copy()

        progress = QProgressDialog(QString(u"Erzeuge Schwarz/Weiß Bild"),
                                   QString(u"Abbrechen"),
                                   0,
                                   ((newPicture.height() * newPicture.width())-1),
                                   self.parent())
        progress.setWindowModality(Qt.WindowModal)

        #print("TARGET:",newPicture.height() * newPicture.width())
        z = 0
        for i in range(newPicture.width()):
            progress.setValue(z)
            for j in range(newPicture.height()):
                z += 1
                col = newPicture.pixel(i, j)
                gray = qGray(col)
                alpha = qAlpha(col)
                newPicture.setPixel(i, j, qRgba(gray, gray, gray, alpha))

                if progress.wasCanceled():
                    break
            if progress.wasCanceled():
                    newPicture = self.picture.copy()
                    break
            z += 1
        progress.setValue((newPicture.height() * newPicture.width())-1)

        dir = tempfile.gettempdir()
        filename = random.randint(1,900)
        extension = "jpg"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)

        newPicture.save(newFile)
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile


        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)
        self.repaint()
        return True

    @pyqtSlot()
    def _rotateClockwise(self):
        #QImage myImage("c:/myimage.png");
        #QTransform myTransform;
        #myTransform.rotate(180);
        #myImage = myImage.transformed(myTransform);
        print("rotate Clockwise")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        myTransformation = QTransform()
        myTransformation.rotate(90)
        newPicture = self.picture.transformed(myTransformation)
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)

        extension = "jpg"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)

        newPicture.save(newFile)
        self.clip_rect = QRect(self.rect())
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile

        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)

        self.repaint()

    @pyqtSlot()
    def _whiteToTransparent(self):

        print("turn white to transparent")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        ################################################################

        soucrefilepath = self.lastFile

        dir = tempfile.gettempdir()
        filename = random.randint(1,900)

        extension = "png"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)

        ############ Use ImageMagick for turning white to transparent  (including fuzz factor.... ############
        with Image(filename=unicode(soucrefilepath)) as i:
            with color.Color("white") as mycolor:
                i.transparent_color(mycolor, alpha=0.0, fuzz=3000)    # fuzz is factor 100 larger then on command line?
                i.save(filename=newFile)

        #####################################################################################################


        print("Saving changed file to:", newFile)

        self.clip_rect = QRect(self.rect())
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile

        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)

        self.repaint()


    @pyqtSlot()
    def _flipHorizontal(self):
        # QImage::mirrored()
        print("Flip horizontal")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        newPicture = self.picture.mirrored(True, False)
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)

        extension = "jpg"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)

        newPicture.save(newFile)
        self.clip_rect = QRect(self.rect())
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile
        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)

        self.repaint()

    @pyqtSlot()
    def _flipVertical(self):
        # QImage::mirrored()
        print("Flip vertical")
        self.lastFile = self.currentFile
        currentZoomlevel = self.zoomlevel()
        self.zoom_image()
        newPicture = self.picture.mirrored(False, True)
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)

        extension = "jpg"
        if unicode(self.currentFile).lower().endswith(".png"):
            extension = "png"

        newFile = "%s/imagecrop%d.%s" %(dir, filename, extension)

        newPicture.save(newFile)
        self.clip_rect = QRect(self.rect())
        self.loadNewPicture.emit(newFile)
        self.currentFile = newFile
        print("Restoring Zoomlevel", currentZoomlevel)
        self.zoom_image(currentZoomlevel)
        self.crop_area_zoom_level.emit(currentZoomlevel)


        self.repaint()


    def _getCurrentFilename(self):

        return self.currentFile


    def paintEvent(self, event):
        self.largest_rect = event.rect()

        # Keep the selected Area inside the visible Area and a minimum Size while scrolling

        if self.clip_rect.topLeft().x() < self.largest_rect.topLeft().x():
            self.clip_rect.setTopLeft(QPoint(self.largest_rect.topLeft().x(), self.clip_rect.topLeft().y()))
            if (self.clip_rect.left()+self.cropBoarder+2) > (self.clip_rect.right() - self.cropBoarder -2):
                self.clip_rect.setTopRight(QPoint(self.clip_rect.topLeft().x()+(self.cropBoarder * 2) +2,
                                                  self.clip_rect.topRight().y()))

        if self.clip_rect.topLeft().y() < self.largest_rect.topLeft().y():
            self.clip_rect.setTopLeft(QPoint(self.clip_rect.topLeft().x(), self.largest_rect.topLeft().y()))
            if (self.clip_rect.top()+self.cropBoarder+2) > (self.clip_rect.bottom() - self.cropBoarder -2):
                self.clip_rect.setBottomRight(QPoint(self.clip_rect.bottomRight().x(),
                                                     self.clip_rect.topRight().y()+(self.cropBoarder * 2) +2))

        if self.clip_rect.bottomRight().x() > self.largest_rect.bottomRight().x():
            self.clip_rect.setBottomRight(QPoint(self.largest_rect.bottomRight().x(), self.clip_rect.bottomRight().y()))
            if (self.clip_rect.left()+self.cropBoarder+2) > (self.clip_rect.right() - self.cropBoarder -2):
                self.clip_rect.setTopLeft(QPoint(self.clip_rect.topRight().x()-(self.cropBoarder * 2) -2,
                                                  self.clip_rect.topLeft().y()))

        if self.clip_rect.bottomRight().y() > self.largest_rect.bottomRight().y():
            self.clip_rect.setBottomRight(QPoint(self.clip_rect.bottomRight().x(), self.largest_rect.bottomRight().y()))
            if (self.clip_rect.top()+self.cropBoarder+2) > (self.clip_rect.bottom() - self.cropBoarder -2):
                self.clip_rect.setTopLeft(QPoint(self.clip_rect.topLeft().x(),
                                                 self.clip_rect.bottomRight().y()-(self.cropBoarder * 2) -2))


        # Keep distance between corners of selected Area higher than 12 pixels (self.cropBoarder + 2) while dragging

        if (self.clip_rect.left()+self.cropBoarder+2) > (self.clip_rect.right() - self.cropBoarder -2):
            if self.dragging == 0 or self.dragging == 2:
                self.clip_rect.setTopRight(QPoint(self.clip_rect.topLeft().x()+(self.cropBoarder * 2) +2,
                                                  self.clip_rect.topRight().y()))
            if self.dragging == 1 or self.dragging == 3:
                self.clip_rect.setTopLeft(QPoint(self.clip_rect.topRight().x()-(self.cropBoarder * 2) -2,
                                                  self.clip_rect.topLeft().y()))

        if (self.clip_rect.top()+self.cropBoarder+2) > (self.clip_rect.bottom() - self.cropBoarder -2):
            if self.dragging == 0 or self.dragging == 1:
                self.clip_rect.setBottomRight(QPoint(self.clip_rect.bottomRight().x(),
                                                     self.clip_rect.topRight().y()+(self.cropBoarder * 2) +2))
            if self.dragging == 2 or self.dragging == 3:
                self.clip_rect.setTopLeft(QPoint(self.clip_rect.topLeft().x(),
                                                 self.clip_rect.bottomRight().y()-(self.cropBoarder * 2) -2))


        if self.picture is None:
            return
        if self.clip_rect.height() > event.rect().height(): # or self.clip_rect.width() > event.rect().width():
            #print("adjusting Rect")
            self.clip_rect = event.rect()
            #print("my event.rect for adjusting is:", event.rect())
            #print("maybe I should use my self.rect...??:", self.rect())

            #print("my clipRect after adjusting is:", self.clip_rect)

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawImage(self.rect(), self.picture)
        # fill none-selected area with gray overlayer...
        mypath = QPainterPath()
        mypath.moveTo(self.clip_rect.topLeft())
        mypath.lineTo(event.rect().topLeft())
        mypath.lineTo(event.rect().topRight())
        mypath.lineTo(event.rect().bottomRight())
        mypath.lineTo(event.rect().bottomLeft())
        mypath.lineTo(event.rect().topLeft())
        mypath.lineTo(self.clip_rect.topLeft())
        mypath.lineTo(self.clip_rect.bottomLeft())
        mypath.lineTo(self.clip_rect.bottomRight())
        mypath.lineTo(self.clip_rect.topRight())
        mypath.lineTo(self.clip_rect.topLeft())
        mypath.closeSubpath()

        painter.fillPath(mypath, QBrush(QColor(0x33, 0x33, 0x33, 0xcc)))

        topRightX = self.clip_rect.x() + self.clip_rect.width()
        bottomY = self.clip_rect.y() + self.clip_rect.height()

        #show gridLines

        if self.dragging is not None:
            painter.setPen(QPen(Qt.lightGray, 1))

            f = 1.0 / self.gridDistance
            wsize = self.clip_rect.width() * f
            hsize = self.clip_rect.height() * f

            gridlines = QPainterPath()

            for i in range(1, self.gridDistance):
                y = self.clip_rect.y() + i * hsize
                gridlines.moveTo(self.clip_rect.x(), y)
                gridlines.lineTo(topRightX, y)


                for j in range(1, self.gridDistance):
                    x = self.clip_rect.x() + j * wsize
                    gridlines.moveTo(x, self.clip_rect.y())
                    gridlines.lineTo(x, bottomY)

            painter.drawPath(gridlines)


        # Draw Corners
        painter.setPen(QPen(Qt.cyan, 3))

        cropRect = QPainterPath()

        #top Left Corner
        cropRect.moveTo(self.clip_rect.topLeft())
        cropRect.lineTo(self.clip_rect.x() + self.cropBoarder, self.clip_rect.y())
        cropRect.moveTo(self.clip_rect.topLeft())
        cropRect.lineTo(self.clip_rect.x(), self.clip_rect.y() + self.cropBoarder)

        #top Right Corner
        cropRect.moveTo(self.clip_rect.topRight())
        cropRect.lineTo(topRightX - self.cropBoarder, self.clip_rect.y())
        cropRect.moveTo(self.clip_rect.topRight())
        cropRect.lineTo(topRightX, self.clip_rect.y() + self.cropBoarder)

        #bottom right corner
        cropRect.moveTo(self.clip_rect.bottomRight())
        cropRect.lineTo(topRightX - self.cropBoarder, bottomY)
        cropRect.moveTo(self.clip_rect.bottomRight())
        cropRect.lineTo(topRightX, bottomY - self.cropBoarder)

        #bottom left corner
        cropRect.moveTo(self.clip_rect.bottomLeft())
        cropRect.lineTo(self.clip_rect.x() + self.cropBoarder, bottomY)
        cropRect.moveTo(self.clip_rect.bottomLeft())
        cropRect.lineTo(self.clip_rect.x(), bottomY - self.cropBoarder)

        painter.drawPath(cropRect)

        painter.end()

    def corner(self, number):

        if number == 0:
            return QRect(self.clip_rect.topLeft() - QPoint(8, 8), QSize(16, 16))
        elif number == 1:
            return QRect(self.clip_rect.topRight() - QPoint(8, 8), QSize(16, 16))
        elif number == 2:
            return QRect(self.clip_rect.bottomLeft()  - QPoint(8, 8), QSize(16, 16))
        elif number == 3:
            return QRect(self.clip_rect.bottomRight() - QPoint(8, 8), QSize(16, 16))

    def mousePressEvent(self, event):
        print(event.pos())
        self.lastMousePosition = event.pos()

        for i in range(4):
            rect = self.corner(i)
            if rect.contains(event.pos()):
                self.dragging = i
                self.drag_offset = rect.topLeft() - event.pos()
                break
            else:
                self.dragging = None

        if self.clip_rect.contains(event.pos()) and self.dragging is None:
            self.moving = True
        else:
            self.moving = False

    def mouseMoveEvent(self, event):

        #if self.dragging is None:
        #    return
        pos = event.pos()
        left = self.largest_rect.left()
        right = self.largest_rect.right()
        top = self.largest_rect.top()
        bottom = self.largest_rect.bottom()

        point = event.pos() #+ self.drag_offset
        point.setX(max(left, min(point.x(), right)))
        point.setY(max(top, min(point.y(), bottom)))

        if self.dragging == 0:
            self.clip_rect.setTopLeft(point)
        elif self.dragging == 1:
            self.clip_rect.setTopRight(point)
        elif self.dragging == 2:
            self.clip_rect.setBottomLeft(point)
        elif self.dragging == 3:
            self.clip_rect.setBottomRight(point)

        if self.dragging is None and not self.moving:
            #print("Looking")
            self.currentMousePosition = pos
            for i in range(4):
                rect = self.corner(i)

                if rect.contains(pos):
                    corner = i
                    if i == 0 or i == 3:
                        self.setCursor(Qt.SizeFDiagCursor)
                        break
                    elif i == 1 or i == 2:
                        self.setCursor(Qt.SizeBDiagCursor)
                        break

                elif self.clip_rect.contains(pos):
                    self.setCursor(Qt.OpenHandCursor)

                else:
                    self.unsetCursor()

        if self.moving:
            self.setCursor(Qt.ClosedHandCursor)
            offset = event.pos() - self.lastMousePosition
            self.lastMousePosition = event.pos()
            #print(offset.y())
            #print(offset.x())
            self.clip_rect.setTopLeft(self.clip_rect.topLeft()+offset)
            self.clip_rect.setBottomRight(self.clip_rect.bottomRight()+offset)

        self.repaint()

    def mouseReleaseEvent(self, event):

        if self.moving:
            self.setCursor(Qt.OpenHandCursor)
            self.moving = None

        self.dragging = None
        self.repaint()

    def zoomlevel(self):

        # calculate zoomfactor
        area_Normal = self.picture_original.width()
        area_showen = self.picture.width()
        print("original height:", area_Normal)
        print("was adjusted to:", area_showen)
        zoomlevel = (area_showen * 100) / (area_Normal)
        print("Zoomlevel:", zoomlevel)
        return zoomlevel

