#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import tempfile
import random
import os
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AreaSelector(QWidget):
    """
    This class maskes the whole screen with a semi-transparent background.
    If the user clicks the screen and draggs a rect for selecting an area, the area selected is completely
    transparent.
    When the user releases the mousebutton, the overloaded signal "screenshot_ready(QString) will be emitted.
    The QString contains the path to the file which is stored in the systems temp-folder.
    If the user interupts the operation with pressing the <esc> button, the signal "screenshot_aborted()" will
    be emitted.

    Connect to both signals with:
    self.connect(self, SIGNAL("screenshot_ready(QString)"), self.on_accept)
    self.connect(self, SIGNAL("screenshot_aborted()"), self.on_reject)
    and handle the results.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.hide()
        self.mousePressed = False
        self.screenshotTaken = False
        self.originPressed = QPoint(0,0)
        self.timer = QTimer()
        self.secondArea = None

        self.connect(self, SIGNAL("screenshot()"), self.onScreenshot)

    def resetOpazity(self):
        """
        set window Opacity which is used for the white background
        """
        self.setWindowOpacity(.40)

    def show_selection_area(self):
        """
        This is the main-function of this tool, it shows the whole Desktop with a semi-transparent layer.
        Sets the cursor to a cross and is waiting for a click.

        """
        #TODO: Offset between 2 screens is not calculated.
        if QDesktopWidget().screenCount() == 2: #2 if two screens are connected
            #need a extended window....

            geo = QApplication.desktop().screenGeometry(1)  # screen = -1 (default)  >> QRect(0,0,1280,1024) == defaultscreen !!!
            offsetx = geo.top()  #0
            offsety = QDesktopWidget().screenGeometry(0).width() + 2  #1280
            self.secondArea = AreaSelector_Extendet(offsetx, offsety, QDesktopWidget().screen(1), self)  # 0  1280
            self.connect(self.secondArea, SIGNAL("screenshot_ready(QString)"), self.retweet)
            self.secondArea.show_selection_area()

        self.setParent(QApplication.desktop().screen())
        print("show primary")
        # activate the window and use the full screen
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowState(Qt.WindowFullScreen | Qt.WindowActive)
        #self.setWindowState(Qt.WindowActive)
        self.move(0,0)
        #self.setGeometry(0,0,QApplication.desktop().screen().width(), QApplication.desktop().screen().height())
        self.resize(QDesktopWidget().screenGeometry(0).width(),
                    QDesktopWidget().screenGeometry(0).height())
        #self.resize(totalwidth, totalhight)
        self.resetOpazity()
        # use a cross as mouse cursor
        self.setCursor(Qt.CrossCursor)
        #reset the clip_rect
        self.clip_rect = QRect(0,0,0,0)
        # and make it all visible
        self.show()

    def shotScreen(self, delay=0):
        time.sleep(delay)

        completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        return completeScreenPixmap

    def retweet(self, filename):
        self.emit(SIGNAL("screenshot_ready(QString)"), filename)
        self.screenshotTaken = True     # this flag is only evaluated during "closeEvent"
        self.close()

    def paintEvent(self, event):
        #print("Painting 1")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

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

        painter.fillPath(mypath, QBrush(QColor("white")))

        # make it a little bit more ... hm.. blue :-)
        myClipPath = QPainterPath()
        myClipPath.moveTo(self.clip_rect.topLeft())
        myClipPath.lineTo(self.clip_rect.topLeft())
        myClipPath.lineTo(self.clip_rect.bottomLeft())
        myClipPath.lineTo(self.clip_rect.bottomRight())
        myClipPath.lineTo(self.clip_rect.topRight())
        myClipPath.lineTo(self.clip_rect.topLeft())

        painter.setPen(QPen(QColor(Qt.blue), 3))
        painter.drawPath(myClipPath)


        painter.end()

    def mousePressEvent(self, event):
        #print("Start Rubberbandselection at:", event.pos())
        self.mousePressed = True
        self.originPressed = QPoint(event.pos())

    def mouseMoveEvent(self, event):
        #print("Selection")
        if self.mousePressed:
            firstpoint = self.originPressed
            secondpoint = event.pos()
            topLeft = firstpoint
            botRight = secondpoint

            #catch different selection-directions
            if firstpoint.x() < secondpoint.x():
                #moved right
                if firstpoint.y() < secondpoint.y():
                    #moved lower
                    topLeft = firstpoint
                    botRight = secondpoint
                else:
                    #moved higher
                    topLeft = QPoint(firstpoint.x(), secondpoint.y())
                    botRight = QPoint(secondpoint.x(), firstpoint.y())

            else:
                #moved left
                if secondpoint.y() < firstpoint.y():
                    #moved higher
                    topLeft = secondpoint
                    botRight = firstpoint
                else:
                    #moved lower
                    topLeft = QPoint(secondpoint.x(), firstpoint.y())
                    botRight = QPoint(firstpoint.x(), secondpoint.y())

            self.clip_rect.setTopLeft(topLeft)
            self.clip_rect.setBottomRight(botRight)

            self.update()

    def mouseReleaseEvent(self, event):
        #print("Finish Rubberbandselection and make Screenshot of Area")
        self.mousePressed = False
        print("Screenshot at:", self.clip_rect)
        self.cheese()
        self.emit(SIGNAL("screenshot()"))
        self.update()

    def cheese(self):
        """
        this function is only simulating the "flash" of an camera when the screenshot was sucessfully taken,
        to ensure the user, that the operation was sucessfull.
        Flash = setting the opacity to nealy 100% (completely NOT transparent) and reset it to the "normal" (0.40)
        """
        self.setWindowOpacity(0.99)
        self.update()
        self.timer.singleShot(150, self.resetOpazity)

    def onScreenshot(self):
        """
        this function is called when ever the mousebutton is released (a selection is finished)
        it took a screenshot of the selected area and save it to a temp-file.

        :return: emit the signal "screenshot_ready(QString)" --> The QString contains the path, where the
                 tempfile is located.
        """
        if self.secondArea is not None:
            self.secondArea.close()
        # restore "normal" mouse-pointer
        self.unsetCursor()
        # Garbage collect any existing image first.
        self.hide()
        time.sleep(1)
        self.completeScreenPixmap = None
        #geo = QApplication.desktop().screenGeometry()


        #self.completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().winId(),
        #                                              geo.left(), geo.top(),
        #                                               geo.width(), geo.height())  # the whole screen as Pixmap
        self.completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        try:  # Ducktyping, if clip_rect is existing id not.
            mapped_clip_rect=QRect(self.mapToGlobal(self.clip_rect.topLeft()),
                                   self.mapToGlobal(self.clip_rect.bottomRight()))
            self.selectedAreaPixmap = self.completeScreenPixmap.copy(mapped_clip_rect)        # the selection as Pixmap
        except:
            self.selectedAreaPixmap = self.completeScreenPixmap
        # create the path and a random filename for the Image
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)
        extension = "png"

        filename = os.path.join(dir, "{0}.{1}".format(filename, extension))
        # Store Pixmap to file
        self.selectedAreaPixmap.save(filename)

        self.emit(SIGNAL("screenshot_ready(QString)"), filename)
        print("Screenshot was successfully saved:", filename)
        self.screenshotTaken = True     # this flag is only evaluated during "closeEvent"
        self.close()                    # close after screenshot was taken

    def keyPressEvent(self, QKeyEvent):
        """
        :param QKeyEvent: QKeyEvent
        :return: Close Application if <ESC> is pressed
        """
        if QKeyEvent.key() == Qt.Key_Escape:
            if self.secondArea is not None:
                self.secondArea.close()
            self.close()

    @pyqtSlot()                                # process close Event and post-actions
    def closeEvent(self, QCloseEvent):
        """
        Check if a screenshot was taken or not, emit a special signal, if the operation was aborted
        Also the closeEvent can be triggered by pressing <ESC> Key
        """

        if not self.screenshotTaken:
            self.emit(SIGNAL("screenshot_aborted()"))
            print("Aborted")
        self.hide()
        QCloseEvent.ignore()



class AreaSelector_Extendet(QWidget):
    """
    This class maskes the whole screen with a semi-transparent background.
    If the user clicks the screen and draggs a rect for selecting an area, the area selected is completely
    transparent.
    When the user releases the mousebutton, the overloaded signal "screenshot_ready(QString) will be emitted.
    The QString contains the path to the file which is stored in the systems temp-folder.
    If the user interupts the operation with pressing the <esc> button, the signal "screenshot_aborted()" will
    be emitted.

    Connect to both signals with:
    self.connect(self, SIGNAL("screenshot_ready(QString)"), self.on_accept)
    self.connect(self, SIGNAL("screenshot_aborted()"), self.on_reject)
    and handle the results.
    """

    def __init__(self, offsetx, offsety, parent=None, caller=None):
        QWidget.__init__(self, parent)
        self.screen = parent
        self.setParent(parent)
        self.caller=caller
        self.hide()
        self.mousePressed = False
        self.screenshotTaken = False
        self.originPressed = QPoint(0,0)
        self.timer = QTimer()
        self.offsetx = offsetx
        self.offsety = offsety

        self.connect(self, SIGNAL("screenshot()"), self.onScreenshot)

    def resetOpazity(self):
        """
        set window Opacity which is used for the white background
        """
        self.setWindowOpacity(.40)

    def show_selection_area(self):
        """
        This is the main-function of this tool, it shows the whole Desktop with a semi-transparent layer.
        Sets the cursor to a cross and is waiting for a click.

        """
        print("start secondary")
        # activate the window and use the full screen
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowState(Qt.WindowFullScreen | Qt.WindowActive)

        RectScreen1 = QApplication.desktop().screenGeometry(1)  #PyQt4.QtCore.QRect(1366, 0, 1280, 1024)
        self.move(RectScreen1.left(),RectScreen1.top())
        #self.move(0,0)
        print("Move to:", RectScreen1.left(),RectScreen1.top())
        self.resize(RectScreen1.width(), RectScreen1.height())
        print("Resizing to:", RectScreen1.width(), RectScreen1.height())
        self.resetOpazity()
        # use a cross as mouse cursor
        self.setCursor(Qt.CrossCursor)
        #reset the clip_rect
        self.clip_rect = QRect(0,0,0,0)
        # and make it all visible
        print("Showing extendet...")
        self.show()

    def paintEvent(self, event):
        #print("Painting 1")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

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

        painter.fillPath(mypath, QBrush(QColor("white")))

        # make it a little bit more ... hm.. blue :-)
        myClipPath = QPainterPath()
        myClipPath.moveTo(self.clip_rect.topLeft())
        myClipPath.lineTo(self.clip_rect.topLeft())
        myClipPath.lineTo(self.clip_rect.bottomLeft())
        myClipPath.lineTo(self.clip_rect.bottomRight())
        myClipPath.lineTo(self.clip_rect.topRight())
        myClipPath.lineTo(self.clip_rect.topLeft())

        painter.setPen(QPen(QColor(Qt.blue), 3))
        painter.drawPath(myClipPath)

        painter.end()

    def mousePressEvent(self, event):
        #print("Start Rubberbandselection at:", event.pos())
        self.mousePressed = True
        self.originPressed = QPoint(event.pos())

    def mouseMoveEvent(self, event):
        #print("Selection")
        if self.mousePressed:
            firstpoint = self.originPressed
            secondpoint = event.pos()
            topLeft = firstpoint
            botRight = secondpoint

            #catch different selection-directions
            if firstpoint.x() < secondpoint.x():
                #moved right
                if firstpoint.y() < secondpoint.y():
                    #moved lower
                    topLeft = firstpoint
                    botRight = secondpoint
                else:
                    #moved higher
                    topLeft = QPoint(firstpoint.x(), secondpoint.y())
                    botRight = QPoint(secondpoint.x(), firstpoint.y())

            else:
                #moved left
                if secondpoint.y() < firstpoint.y():
                    #moved higher
                    topLeft = secondpoint
                    botRight = firstpoint
                else:
                    #moved lower
                    topLeft = QPoint(secondpoint.x(), firstpoint.y())
                    botRight = QPoint(firstpoint.x(), secondpoint.y())

            self.clip_rect.setTopLeft(topLeft)
            self.clip_rect.setBottomRight(botRight)

            self.update()

    def mouseReleaseEvent(self, event):
        #print("Finish Rubberbandselection and make Screenshot of Area")
        self.mousePressed = False
        print("Screenshot at2:", self.clip_rect)
        self.cheese()
        self.emit(SIGNAL("screenshot()"))
        self.update()

    def cheese(self):
        """
        this function is only simulating the "flash" of an camera when the screenshot was sucessfully taken,
        to ensure the user, that the operation was sucessfull.
        Flash = setting the opacity to nealy 100% (completely NOT transparent) and reset it to the "normal" (0.40)
        """
        self.caller.hide()
        self.hide()
        time.sleep(1)
        self.setWindowOpacity(0.99)
        self.update()
        self.timer.singleShot(100, self.resetOpazity)

    def onScreenshot(self):
        """
        this function is called when ever the mousebutton is released (a selection is finished)
        it took a screenshot of the selected area and save it to a temp-file.

        :return: emit the signal "screenshot_ready(QString)" --> The QString contains the path, where the
                 tempfile is located.
        """

        # restore "normal" mouse-pointer
        self.unsetCursor()
        # Garbage collect any existing image first.
        self.completeScreenPixmap = None
        prim = self.screen.screenGeometry(0)
        geo = self.screen.screenGeometry(1)

        #self.completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().winId(),
        #                                               prim.width() + self.clip_rect.left(), prim.top() + self.clip_rect.top(),
        #                                               self.clip_rect.width(), prim.top() + self.clip_rect.height())  # the whole screen as Pixmap
        #self.completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().screen(1).winId())
        #self.selectedAreaPixmap = self.completeScreenPixmap.copy(self.clip_rect)        # the selection as Pixmap
        #self.selectedAreaPixmap = self.completeScreenPixmap
        self.completeScreenPixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        mapped_clip_rect=QRect(self.mapToGlobal(self.clip_rect.topLeft()),
                               self.mapToGlobal(self.clip_rect.bottomRight()))
        self.selectedAreaPixmap = self.completeScreenPixmap.copy(mapped_clip_rect)        # the selection as Pixmap

        # create the path and a random filename for the Image
        dir = tempfile.gettempdir()
        filename = random.randint(1,900)
        extension = "png"

        filename = os.path.join(dir, "{0}.{1}".format(filename, extension))
        # Store Pixmap to file
        self.selectedAreaPixmap.save(filename)
        self.emit(SIGNAL("screenshot_ready(QString)"), filename)
        print("Screenshot was successfully saved:", filename)
        self.screenshotTaken = True     # this flag is only evaluated during "closeEvent"
        self.close()                    # close after screenshot was taken

    def keyPressEvent(self, QKeyEvent):
        """
        :param QKeyEvent: QKeyEvent
        :return: Close Application if <ESC> is pressed
        """
        if QKeyEvent.key() == Qt.Key_Escape:
            self.caller.close()
            self.close()


    @pyqtSlot()                                # process close Event and post-actions
    def closeEvent(self, QCloseEvent):
        """
        Check if a screenshot was taken or not, emit a special signal, if the operation was aborted
        Also the closeEvent can be triggered by pressing <ESC> Key
        """

        if not self.screenshotTaken:
            self.emit(SIGNAL("screenshot_aborted()"))
            print("Aborted")
        QCloseEvent.accept()


# USAGE:

def main():
    app = QApplication(sys.argv)
    mywindow = AreaSelector()
    mywindow.show_selection_area()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()