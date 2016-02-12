#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fading between different Pictures
# setFadingDuration() sets the time used for the fading in milliseconds
# addPicture (give a path to the pic, which should be loaded, and a size for it)
# KeepRatio is aktive !



import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FadeWidget(QLabel):

    def __init__(self, old_widget, new_widget, fadingDuration):

        QLabel.__init__(self, new_widget)

        #self.old_pixmap = QPixmap(new_widget.size())
        #old_widget.render(self.old_pixmap)
        #self.old_pixmap = old_widget.pixmap().scaled(new_widget.pixmap().size(), Qt.KeepAspectRatio)
        self.setPixmap(old_widget.pixmap())
        self.setLayoutDirection(Qt.LeftToRight)                  # set Alignment of Picture inside the new Label


        self.pixmap_opacity = 0.9

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(fadingDuration)
        self.timeline.start()
        self.offset = 0
        #self.resize(new_widget.size())
        #self.setMinimumSize(new_widget.size())
        self.setAlignment(Qt.AlignCenter)

        self.show()

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(self.offset,self.offset, self.pixmap())
        painter.end()


    def animate(self, value):

        self.pixmap_opacity = 0.9 - value
        self.setPixmap(self.pixmap().scaled((self.pixmap().width()+1 - (self.pixmap().width() * value)),
                                            self.pixmap().height()+1 - (self.pixmap().height() * value)))

        self.offset = 200 * value

        self.repaint()


class FadingStackedPictureWidget(QStackedWidget):

    def __init__(self, parent = None):
        QStackedWidget.__init__(self, parent)
        self.setFadingDuration(800)

    def setCurrentIndex(self, index):
        if self.widget(index):
            #QStackedWidget.setCurrentIndex(self, index)
            self.fader_widget = FadeWidget(self.currentWidget(), self.widget(index), self.fadingDuration)
            QStackedWidget.setCurrentIndex(self, index)

        else:
            return False, "Got no Pictures to display"

    def showPicture(self, index):
        self.setCurrentIndex(index)

    def setFadingDuration(self, milliseconds):
        self.fadingDuration = milliseconds

    def addPicture(self, path, intX, intY, pathIsPixmapObject=False):
        """
        :param path: path to the picture which should be added
        :param intX: height of picture
        :param intY: width of picture
        :return: Index of the given Picture-Label
        :function: installs the given picture on a QLabel, and add the QLabel(including the picture) to the
        stacked Widget.
        """
        PictureOne = QLabel()
        if pathIsPixmapObject:
            picture_raw = path
        else:
            picture_raw = QPixmap(path)
        #mask = picture_raw.createMaskFromColor(QColor("white"), 0)
        #picture_raw.setMask(mask)
        if picture_raw.height() > self.height() or picture_raw.width() > self.width():
            picture_raw = picture_raw.scaled(intX, intY, Qt.KeepAspectRatio)

        PictureOne.setPixmap(picture_raw)

        PictureOne.setLayoutDirection(Qt.LeftToRight)                  # set Alignment of Picture inside the new Label
        PictureOne.setAlignment(Qt.AlignCenter)
        self.addWidget(PictureOne)

        return self.indexOf(PictureOne)



if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = QWidget()

    stack = FadingStackedPictureWidget()

    stack.setPicture1('/home/matthias/Bilder/test.jpg', 300, 300)                   # first add (index 0)
    stack.setPicture2('/home/matthias/Bilder/fotobuch.png', 300, 300)               # second add (index 1)

    page1Button = QPushButton("Page 1")
    page2Button = QPushButton("Page 2")
    page1Button.clicked.connect(stack.setCurrentIndex, 0)     # you can directelly call the index if you want...
    page2Button.clicked.connect(stack.showPicture2) # or you can call the methode (only works, when pics were added in a row 1 2 3 4

    layout = QGridLayout(window)
    layout.addWidget(stack, 0, 0, 1, 2)
    layout.addWidget(page1Button, 1, 0)
    layout.addWidget(page2Button, 1, 1)

    window.show()

    sys.exit(app.exec_())
