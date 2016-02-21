#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import random
import urllib2
import time
from PyQt4 import uic          # generate UI in runtime... directelly out of an ".ui" File
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from src.detail_chooser import detail_chooser_DLG as detailChooser            # Version 0.1.1
from src.area_selector import AreaSelector as areaSelector
from src.LM_classes import SearchEngine, LM_EDITORDelegate_Tree, LM_EDITORModel_Tree, TreeItem
import res.res
import res.resources
from ui.settings_v3_ui import Ui_MainWindow

cwd = os.path.dirname(os.path.realpath(__file__))      # gives the path, where the script is located

__author__ = 'matthias laumer, matthias.laumer@web.de'
__version__ = "0.0.3"

def main(argv):
    app = QApplication(argv)                 # das hier braucht "argumente" ... hmmm...
    qt_translator = QTranslator()
    qt_translator.load("qt_" + QLocale.system().name(),
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    mainwindow = settings_dlg(os.path.join(cwd,"engines.csv"))               # eigene Window-Klasse
    mainwindow.show()
    sys.exit(app.exec_())                   # wenn die QApplication "app" beendet wird, wird das Programm geschlossen


class settings_dlg(QMainWindow, Ui_MainWindow):    # , settings.UiForm

    def __init__(self, filepath, parent=None):
        super(settings_dlg, self).__init__(parent)
        self.parent = parent
        #self.ui = uic.loadUi(("%s/settings_v3.ui" % cwd), self)    # load UI file during runtime
        self.setupUi(self)                                          # # load UI from py file
        self.installEventFilter(self)
        self.setWindowTitle("Engines verwalten:")
        self.__moveCenter()               # places the window in the middle of the screen
        self.filepath = filepath

        self.numberOfNextNewEntry = 1
        self.defaultPicture = ":/kombo-search-icon.png"               # das default-Bild, speziell für neue Einträge...
        self.dialogsActive = False
        self.dialogWASActive = False
        self.OkToContinue = True

        self.__createActions()
        self.__createMenus()
        self.__createToolBars()
        self.__setupItems()
        self.__setupLineEdits()
        self.__setupConnections()

        status = self.model.loadDatabase(self.filepath)
        if not status:
            if os.path.isfile(self.filepath):  # if file exits, but model returned False
                ret = self.askQuestion("Fehler:",
                                       "<b style='color:red;'>Beim laden der Konfigurationsdatei '{0}' "
                                       "ist ein Fehler aufgetreten</b>".format(os.path.basename(self.filepath)),
                                       "Ok",
                                       "Die Datei scheint Fehler zu enthalten, oder ist falsch formatiert."
                                       "Wenn Sie fortfahren wird diese Datei überschrieben","Abbrechen")
                if ret == 0:
                    pass    # on yes, do nothing
                else:
                    self.deleteLater()  # if user have not chosen yes, delete myself.
            else:
                ret = self.askQuestion("Hinweis:", "Es konnte keine bestehende Konfigurationsdatei gefunden werden.",
                                       "Weiter",
                                       "Es wird eine neue Datei angelegt.","Abbrechen")
                if ret == 0:
                    pass   # on yes, do nothing
                else:
                    self.deleteLater()  # if user have not chosen yes, delete myself.

        self.checkActions()
        self.on_selection_changed()

    def __moveCenter(self):
        """
        Placing the windows in the middle of the screen
        """
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def __createActions(self):
        """
        Create Actions which are used in Toolbar, Menue and context-menues
        """
        self.ACTnewPos = QAction(QIcon(':/add_row.png'), u"&Neue Position",self,
                                 shortcut=QKeySequence.AddTab,
                                 statusTip=u"Erstellt eine neue Position in der aktuellen Kalkulation",
                                 triggered=self.addPosition)

        self.ACTremovePos = QAction(QIcon(':/remove_row.png'), u"&Position entfernen",self,
                                 shortcut=QKeySequence.Delete,
                                 statusTip=u"Entfernt die markierten Positionen",
                                 triggered=self.removePosition)

        self.ACTcollapseAll = QAction(QIcon(':/collapse_all.png'), u"&Alles zuklappen",self,
                                 statusTip=u"klappt alle geöffneten Knoten einer Datenbankansicht zu",
                                 triggered=lambda : self.on_expandall(False))

        self.ACTexpandAll = QAction(QIcon(':/expand_all.png'), u"&Alles aufklappen",self,
                                 statusTip=u"klappt alle Knoten einer Datenbankansicht auf",
                                 triggered=lambda : self.on_expandall(True))

        self.ACTaddParent = QAction(QIcon(':/add_parent.png'), u"&Neue Kategorie",self,
                                 statusTip=u"Erstellt eine neue Kategorie",
                                 triggered=self.on_newParentInDatebase)

        self.ACTundo = QAction(QIcon.fromTheme("undo"), u"&Rückgängig",self,
                                 shortcut=QKeySequence.Undo,
                                 statusTip=u"Macht die letzte Änderung rückgängig",
                                 triggered=self.on_undo)

        self.ACTredo = QAction(QIcon.fromTheme("redo"), u"&Wiederholen",self,
                                 shortcut=QKeySequence.Redo,
                                 statusTip=u"Stellt die rückgängig gemachte Aktion wieder her",
                                 triggered=self.on_redo)

    def __createMenus(self):
        """
        Create the Mainwindow meneu   " Bearbeiten  "
        :return:
        """

        self.editMenu = self.menuBar().addMenu("&Bearbeiten")
        self.editMenu.addAction(self.ACTundo)
        self.editMenu.addAction(self.ACTredo)
        self.editMenu.addAction(self.ACTaddParent)
        self.editMenu.addAction(self.ACTnewPos)
        self.editMenu.addAction(self.ACTremovePos)
        self.editMenu.addAction(self.ACTcollapseAll)
        self.editMenu.addAction(self.ACTexpandAll)

    def __createToolBars(self):
        """
        A single Toolbar is used.
        """
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.ACTundo)
        self.fileToolBar.addAction(self.ACTredo)
        self.fileToolBar.addAction(self.ACTaddParent)
        self.fileToolBar.addAction(self.ACTnewPos)
        self.fileToolBar.addAction(self.ACTremovePos)
        self.fileToolBar.addAction(self.ACTexpandAll)
        self.fileToolBar.addAction(self.ACTcollapseAll)

    def __setupItems(self):
        #self.treeView = QTreeView()
        self.treeView.setDragDropMode(QAbstractItemView.InternalMove)
        self.model = LM_EDITORModel_Tree()
        self.treeView.setModel(self.model)
        self.treeView.setItemDelegate(LM_EDITORDelegate_Tree(self.treeView))
        self.treeView.header().setResizeMode(0, QHeaderView.Stretch)             # category
        self.treeView.header().setResizeMode(1, QHeaderView.Stretch)             # description
        self.treeView.header().setDefaultSectionSize(40)
        self.treeView.header().setStretchLastSection(False)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(0, 0)       # Qt::AscendingOrder	0

        self.lbl_PreviewPic.installEventFilter(self)
        self.lbl_PreviewPic.setFrameStyle(QFrame.StyledPanel)
        self.lbl_PreviewPic.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lbl_PreviewPic.setAcceptDrops(True)
        self.setAcceptDrops(True)


        self.tB_Openpath.setIcon(QIcon(":/fromFile.png"))
        self.tB_Screenshot.setIcon(QIcon(":/fromScreen.png"))

        self.areaSelector = areaSelector()

        self.pathOfPictures = os.path.join(cwd,"Logos")

        self.dialogsActive = False
        self.dialogWASActive = False

        self.lE_Link_is_dirty = False
        self.lE_Anzeigename_diry = False

    def __setupLineEdits(self):

        #create Validator for "Anzeigename" : starts with "@", at minimum 2 letters or digits following...

        #rx = QRegExp('@([A-Za-z0-9-_]{2,})[\S]*') #@[A-Za-z0-9-_]{2,}
        rx = QRegExp('@([\S]{2,})[\S]*')
        self.validation_Anzeigename = QRegExpValidator(rx)

        #rx2 = QRegExp('http://www.{1,1}(.+)%s{1,1}(.*)[\S]*')
        #rx2 = QRegExp('(^(https?|ftp|file)://)?(www.)?[-A-Za-z0-9+&@#/%?=~_|!:,.;]+(%s)+.*')
        rx2 = QRegExp('^(((https?)://www\.)|(www\.))?'          # es muss entweder http://www. oder www. vorkommen
                      '[-A-Za-z0-9+&@#/%?=~_|!:,.;]+'           # dann kommt alles mögliche
                      '(%s)'                                    # dann ein %s
                      '.*')                                     # und dann wieder alles...
        #rx2.setMinimal(True)

        #rx2 = QRegExp('.*')
        self.validation_Link = QRegExpValidator(rx2)

    def __setupConnections(self):

        # Connections for the cool TreeView-Model-Delegate Combo
        self.treeView.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.connect(self.treeView, SIGNAL("customContextMenuRequested(QPoint)"), self.createContextMenue)
        self.connect(self.lbl_PreviewPic, SIGNAL("customContextMenuRequested(QPoint)"), self.createContextMenueLogo)
        self.connect(self.model, SIGNAL("check_dirty()"), self.check_dirty)
        self.connect(self.model, SIGNAL("askQuestion(QString, QString, QString)"), self.askQuestion)
        self.connect(self.model, SIGNAL("database_changed()"), self.on_database_changed)
        self.connect(self.model, SIGNAL("set_current_row(PyQt_PyObject)"), self.on_set_current_row)
        self.connect(self.model, SIGNAL("save_expansion()"), self.treeView.save_expansion)
        self.connect(self.model, SIGNAL("restore_expansion()"), self.treeView.restore_expansion)
        self.connect(self.model, SIGNAL("expand(QString)"), self.treeView.expandCategory)
        self.connect(self.model, SIGNAL("select(QString, QString)"), self.treeView.selectArticle)
        self.connect(self.model, SIGNAL("addToUndoStack(QString)"), self.treeView.addToUndoStack)
        self.connect(self.treeView, SIGNAL("checkActions()"), self.checkActions)
        self.connect(self, SIGNAL("addToUndoStack(QString)"), self.treeView.addToUndoStack)
        self.connect(self, SIGNAL("reread_articles()"), self.model.on_reread_articles)
        self.connect(self.tB_Openpath, SIGNAL("clicked()"), self.setNewPictureFromFile)
        self.connect(self.tB_Screenshot, SIGNAL("clicked()"), self.setNewPictureFromScreen)
        self.connect(self.pB_OK, SIGNAL("clicked()"), lambda: self.onFinish(True))
        self.connect(self.pB_NOK, SIGNAL("clicked()"), lambda: self.onFinish(False))


        self.lE_Anzeigename.editingFinished.connect(self.processChanges)
        self.lE_Anzeigename.textChanged.connect(lambda : self.dirty_lE_Anzeigename(True))
        self.lE_Link.editingFinished.connect(self.processChanges)
        self.lE_Link.textChanged.connect(lambda : self.dirty_lE_Link(True))
        self.connect(self.areaSelector, SIGNAL("screenshot_ready(QString)"), self.setPicture)
        self.connect(self.areaSelector, SIGNAL("screenshot_aborted()"), self.ensureVisible)

    def setNewPictureFromScreen(self):
        print("Screenshot...")
        if self.parent is not None:
            print("hide Parent")
            self.parent.setWindowOpacity(0.00)
        self.setWindowOpacity(0.00)
        time.sleep(0.5) # wait until the window is REALY hidden...

        self.areaSelector.show_selection_area()

    def ensureVisible(self):
        print("Ensure Visible")
        if self.parent is not None:
            print("Show Main again")
            self.parent.setWindowOpacity(1.0)
        self.setWindowOpacity(1.0)

    def setNewPictureFromFile(self):
        print("Setting new Pic from File")
        self.setPicture()

    def setPicture(self, inputfile=None):                                # take input path
        print("setPicture is called with", inputfile)
        self.ensureVisible()
        if isinstance(inputfile, QString):
            inputfile = unicode(inputfile)
            self.mydialog = detailChooser(inputfile)
            decission = self.mydialog.exec_()

            if decission is 1:
                picturepath = str(self.mydialog.onFertig())
                inputfile = picturepath
            else:
                #print("Es wurde ABBRECHEN geklickt")
                return

        if (inputfile is not None) and (inputfile is not False):
            print("Picture is given %s" % inputfile)
            if os.path.exists(inputfile) and os.path.isfile(inputfile):        #check if given path is valid, and file exists
                basename = os.path.basename(inputfile)
                if self.pathOfPictures == "" or not os.path.exists(self.pathOfPictures):
                    OpenPath = QFileDialog.getExistingDirectory(self, "Geben Sie den Ort an, indem sei Logos ablegen wollen")
                    if OpenPath.isEmpty():
                        return
                    self.pathOfPictures = OpenPath
                    #print("die Bilder werden in %s gespeichert" % self.pathOfPictures)

                if os.path.exists(os.path.join(self.pathOfPictures,basename)):         #check if filename is already existing in specific folder
                    print("Picture is already in %s" % self.pathOfPictures)
                    #print(tempfile.gettempdir())
                    if inputfile.startswith(tempfile.gettempdir()):
                        print("Overwriting the file os.path.join(self.pathOfPictures,basename)in my own folder because ist in temp..maybe newer")
                        self.pathOfPicture = os.path.join(self.pathOfPictures,basename)
                        img = QPixmap(inputfile)
                        if img.width() > 280 or img.height() > 200:
                            img = img.scaled(280,200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.save("%s" % self.pathOfPicture)
                    else:

                        self.pathOfPicture = os.path.join(self.pathOfPictures,basename)    #set new filepath
                else:
                    try:
                        print("Try to copy file into my own folder... because it is in a different one")
                        self.pathOfPicture = os.path.join(self.pathOfPictures,basename)
                        img = QPixmap(inputfile)
                        if img.width() > 280 or img.height() > 200:
                            img = img.scaled(280,200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.save("%s" % self.pathOfPicture)

                    except IOError, e:
                        #print("something went wrong ..", e)
                        self.askQuestion("Beim Erstellen des Logos ist folgender Fehler aufgetreten:", "Ok", "'%s'" % e)
                        self.pathOfPicture = ':/contactpicempty.png'                 #if file cant be copied, set default picture
            else:
                #this is the case, when default pic is set... it cames from the resources-file.. not from a path which is callable
                #print("given File is not a file... setting from resources.")
                self.pathOfPicture = inputfile                  #given picture is not existing

        elif inputfile is None:


            path = os.path.dirname(os.path.realpath(__file__))      # gives the path, where the script is located
            picturepath = QFileDialog.getOpenFileName(self,
                                                      self.tr("Waehlen Sie die die Bilddatei"),
                                                      path,
                                                      self.tr("Image-Datei (*.jpg *.png *.bmp *.JPG *.PNG *.BMP *.jpeg *.JPEG"))
            if picturepath.isEmpty():
               return
            #picturepath = str(picturepath)

            if os.path.exists(picturepath) and os.path.isfile(picturepath):        #check if given path is valid, and file exists

                self.mydialog = detailChooser(picturepath)
                decission = self.mydialog.exec_()

                if decission is 1:
                    picturepath = str(self.mydialog.onFertig())
                else:
                    #print("Es wurde ABBRECHEN geklickt")
                    return

                basename = os.path.basename(picturepath)
                #print("File exists and is a file")

                if self.pathOfPictures == "" or not os.path.exists(self.pathOfPictures):
                    OpenPath = QFileDialog.getExistingDirectory(self, "Geben Sie den Ort an, indem sei Logos ablegen wollen")
                    if OpenPath.isEmpty():
                        return
                    self.pathOfPictures = OpenPath
                    #print("die Bilder werden in %s gespeichert" % self.pathOfPictures)

                if os.path.exists(os.path.join(self.pathOfPictures,basename)):         #check if filename is already existing in specific folder
                    print("Picture is already %s" % self.pathOfPictures)
                    self.pathOfPicture = os.path.join(self.pathOfPictures,basename)    #set new filepath
                else:
                    try:
                        print("Try to copy file into my own folder...")
                        self.pathOfPicture = os.path.join(self.pathOfPictures,basename)
                        print("Filename=",self.pathOfPicture)
                        img = QPixmap(picturepath)
                        if img.width() > 280 or img.height() > 200:
                            img = img.scaled(280,200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.save("%s" % self.pathOfPicture)

                    except IOError, e:
                        print("something went wrong ..", e)
                        self.askQuestion("Beim Erstellen des Logos ist folgender Fehler aufgetreten:", "Ok", "'%s'" % e)
                        self.pathOfPicture = ':/kombo-search-icon.png'   # if file cant be copied, set default picture
            else:
                #this is the case, when default pic is set... it cames from the resources-file.. not from a path which is callable
                #print("given File is not a file... setting default pic.")
                self.pathOfPicture = ':/kombo-search-icon.png'                  #given picture is not existing

        elif inputfile == "":
            self.pathOfPicture = ':/kombo-search-icon.png'
        else:
            print("Setting Fallback-Picture")
            self.pathOfPicture = ':/kombo-search-icon.png'


        engine, category = self.treeView.getCurrentSelectedArticleAndItsParent()

        if os.path.isfile(self.pathOfPicture) and (os.path.dirname(self.pathOfPicture) == self.pathOfPictures):
            relativePath = os.path.join("Logos",os.path.basename(self.pathOfPicture))
            self.pathOfPicture = relativePath

        engine.imagepath = self.pathOfPicture
        self.update_Preview_Pixmap()

        return self.pathOfPicture

    @pyqtSlot()               # caller : self.treeView, SIGNAL("checkActions()")
    def checkActions(self):
        print("Check Actions")
        self.ACTundo.setEnabled(True if self.treeView.undo_possible() else False)
        self.ACTredo.setEnabled(True if self.treeView.redo_possible() else False)
        self.ACTaddParent.setEnabled(True if self.treeView.hasFocus() else False)
        self.ACTnewPos.setEnabled(True if len(self.treeView.selectedIndexes()) > 0 else False)
        self.ACTremovePos.setEnabled(True if len(self.treeView.selectedIndexes()) > 0 else False)

    @pyqtSlot()               # caller : self.treeView.customContextMenuRequested
    def createContextMenue(self, point):   # called with (table/tree)view.customContextMenuRequested
        """
        This function is a customContextMenue of the presentation Area, it will be called with a right-click on the
        presentationArea.
        :param point: Qpoint, where the action was triggered.
        :return: brings up a context-menue which is almost the same, than in toolbar and menuebar.
        """
        #correct offset
        #point.setX(point.x() +10)   # -links +rechts
        point.setY(point.y() +20)   # -oben +unten

        # with a new Verion of PyQt od Qt4 this is necessary now. Otherwise no Icons will be displayed in context-menue
        self.ACTaddParent.setIconVisibleInMenu(True)
        self.ACTnewPos.setIconVisibleInMenu(True)
        self.ACTremovePos.setIconVisibleInMenu(True)
        self.ACTexpandAll.setIconVisibleInMenu(True)
        self.ACTcollapseAll.setIconVisibleInMenu(True)
        self.ACTundo.setIconVisibleInMenu(True)
        self.ACTredo.setIconVisibleInMenu(True)

        # create new QMenu
        self.owncontextMenue = QMenu()
        self.owncontextMenue.addAction(self.ACTaddParent)
        self.owncontextMenue.addAction(self.ACTnewPos)
        self.owncontextMenue.addAction(self.ACTremovePos)
        self.owncontextMenue.addAction(self.ACTexpandAll)
        self.owncontextMenue.addAction(self.ACTcollapseAll)
        self.owncontextMenue.addAction(self.ACTundo)
        self.owncontextMenue.addAction(self.ACTredo)

        # show new QMenu at the point where it was clicked.
        self.owncontextMenue.exec_(self.treeView.mapToGlobal(point))

    @pyqtSlot()
    def createContextMenueLogo(self, point):

        # correct offset
        #point.setX(point.x() + 10)     # -links +rechts
        #point.setY(point.y() + 10)    # -oben +unten

        self.picContext = QMenu()
        self.picContext.addAction(QAction(QIcon(":/reset.png"),
                                          u"Bild zurücksetzen", self, triggered=self.setPicture))  # call with "False"
        self.picContext.addAction(QAction(QIcon(":/fromFile.png"),
                                          u"Neu, aus Datei", self, triggered=self.setNewPictureFromFile))
        self.picContext.addAction(QAction(QIcon(":/fromScreen.png"),
                                          u"Neu, aus Screenshot", self, triggered=self.setNewPictureFromScreen))
        self.picContext.exec_(self.lbl_PreviewPic.mapToGlobal(point))

    @pyqtSlot()              # caller : self.model, SIGNAL("set_current_row(PyQt_PyObject)")
    def on_set_current_row(self, item):

        treeView = self.treeView
        treeView.setFocus(Qt.NoFocusReason)
        treeView.sortByColumn(0, 0)
        model = self.model
        index_parent_mappend, index_self_mapped = model.searchModel(item)
        treeView.expand(index_parent_mappend)
        treeView.selectionModel().select(treeView.model().index(index_self_mapped.row(), index_self_mapped.column(),index_parent_mappend),
                                         QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
        #return index of proxy
        return treeView.model().index(index_self_mapped.row(), index_self_mapped.column(),index_parent_mappend)

    @pyqtSlot()              # caller : self.model, SIGNAL("database_changed()")
    def on_database_changed(self):
        print("Database Changed")
        self.emit(SIGNAL("database_changed()"))

    @pyqtSlot()               # caller : self.model, SIGNAL("check_dirty()")
    def check_dirty(self):
        print("check Dirty")

    @pyqtSlot()               # caller : treeView.selectionModel().selectionChanged
    def on_selection_changed(self):
        '''
        Each time if the selection of my TreeView gets changed by the user or programmatically, the right area
        has to be updated (Line-Edits, Pictures aso.)
        '''
        selectedEngine, Category = self.treeView.getCurrentSelectedArticleAndItsParent()
        #print("Section Changed with:", selectedEngine, Category)

        if not selectedEngine and not Category:
            print("Nothing is selected.")
            self.lE_Anzeigename.setText("")
            self.lE_Anzeigename.setEnabled(False)
            self.lE_Link.setText("")
            self.lE_Link.setEnabled(False)
            self.update_Preview_Pixmap()
            self.lE_Link_is_dirty = False
            self.lE_Anzeigename_diry = False
            self.tB_Screenshot.setVisible(False)
            self.tB_Openpath.setVisible(False)
            return

        if selectedEngine == Category:
            print("U selected a category")
            self.lE_Anzeigename.setText(Category)
            self.lE_Anzeigename.setEnabled(True)
            self.lE_Link.setText("")
            self.lE_Link.setEnabled(False)
            self.update_Preview_Pixmap()
            self.lE_Link_is_dirty = False
            self.lE_Anzeigename_diry = False
            self.tB_Screenshot.setVisible(False)
            self.tB_Openpath.setVisible(False)

        if isinstance(selectedEngine, SearchEngine):
            print("Selected Engine:",selectedEngine.name)
            self.lE_Anzeigename.setText(selectedEngine.name)
            self.lE_Anzeigename.setEnabled(True)
            self.lE_Link.setText(selectedEngine.link)
            self.lE_Link.setEnabled(True)
            self.update_Preview_Pixmap(selectedEngine.imagepath)
            self.lE_Link_is_dirty = False
            self.lE_Anzeigename_diry = False
            self.tB_Screenshot.setVisible(True)
            self.tB_Openpath.setVisible(True)


        print("Selected Category:",Category)
        self.checkActions()

    @pyqtSlot()   # save changes in LineEdits is something was changed...
    def processChanges(self):
        #validate entrys in Line-Edits...
        print("ProcessChanges....", self.sender())
        needViewUpdate = False

        if self.lE_Anzeigename_diry:
            print("Anzeigename Changed")
            # Validation-Steps.
            if len(self.lE_Anzeigename.text()) < 3:
                self.treeView.setDisabled(True)
                if not self.dialogsActive:
                    self.dialogsActive = True
                    self.askQuestion("Name zu kurz","Der von Ihnen eingegeben Name ist zu kurz!", "Ok",
                             "Geben Sie einen Namen mit mindestens 3 Zeichen ein.")
                    self.dialogsActive = False
                    self.OkToContinue = False
                return
            else:
                self.treeView.setDisabled(False)
                new_name = unicode(self.lE_Anzeigename.text()).lstrip().rstrip()
                changedEngineData, category = self.treeView.getCurrentSelectedArticleAndItsParent()
                index = self.treeView.selectionModel().selectedIndexes()[0]
                if not isinstance(changedEngineData, SearchEngine):  # you edited a category
                    self.model.setData(index, QVariant(new_name))

                elif changedEngineData.name != new_name:        # you edited a searchengine
                    changedEngineData.name = new_name
                    needViewUpdate = True
                self.lE_Anzeigename_diry = False
                self.OkToContinue = True

        if self.lE_Link_is_dirty:
            print("Link Changed")
            changedEngineData, category = self.treeView.getCurrentSelectedArticleAndItsParent()
            self.treeView.setDisabled(True)
            if not self.dialogsActive:
                resultLink = self.validate_Link()
                if resultLink != 2 and changedEngineData != category:
                    self.lE_Link.setFocus()
                    self.OkToContinue = False
                    return
                else:
                    new_link = unicode(self.lE_Link.text()).lstrip().rstrip()
                    self.treeView.setDisabled(False)
                    if changedEngineData.link != new_link:
                        changedEngineData.link = new_link
                        needViewUpdate = True
                    self.lE_Link_is_dirty = False
                    self.OkToContinue = True

        if needViewUpdate:
            self.model.reset()

            self.treeView.expandCategory(category)
            if changedEngineData != category:
                self.treeView.selectArticle(category, changedEngineData.name)
            self.OkToContinue = True

    def addPosition(self):
        print("Add Positon")
        View = self.treeView
        model = self.model

        # get current Articel Obj. and its parent as a string
        current_article, parentCategory = View.getCurrentSelectedArticleAndItsParent()
        if parentCategory == False:
            return False # nothing was selected ... this is important for databaseedit
        newArticle = model.insertNewArticle(parentCategory)       # insert a new Article on self.articles of model
        pseudoItem =TreeItem(newArticle, newArticle.category, None) # create a pseudo Item for searching
        index = self.on_set_current_row(pseudoItem)          # search and select the new item which was created
        View.edit(index.sibling(index.row(),1), QAbstractItemView.DoubleClicked, QEvent(QEvent.MouseButtonDblClick))
        # set the selected row in edit mode (use the column 1 (description)
        return True

    def removePosition(self, indexes_list_int=None):

        if True:
            # None / Article   unicode(str)
            current_article, parentCategory = self.treeView.getCurrentSelectedArticleAndItsParent()

            if isinstance(current_article, SearchEngine): #no complete category was chosen to be removed, only a single article
                myMessageBox = QMessageBox()
                myMessageBox.setWindowTitle("Engine entfernen ?")
                myMessageBox.setIcon(QMessageBox.Question)
                myMessageBox.setText(QString("Engine: <b>%1</b> aus der Datenbank entfernen ?").arg(current_article.name.encode("utf-8").decode("utf-8")))
                myMessageBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                myMessageBox.setDefaultButton(QMessageBox.Yes)

                if myMessageBox.exec_() == QMessageBox.No:
                    return
                                          #removeArticles(self, article, category=None, removeCompleteCategory=False)
                self.model.removeArticle(current_article, parentCategory, False)

            else:   # if current_article was None (a complete Category was chosen to be deleted)
                articlesToBeDeleted = self.model.getAllArticlesFromCategory(parentCategory)

                descriptions= ""
                for article in articlesToBeDeleted:
                    desc = article.name.encode("utf-8").decode("utf-8")
                    descriptions += " {0},".format(desc.encode("utf-8"))
                myMessageBox = QMessageBox()
                myMessageBox.setWindowTitle("Gesamte Kategorie entfernen ?")
                myMessageBox.setIcon(QMessageBox.Question)
                myMessageBox.setText(QString("Kategorie: Die gesammte Kategorie <b>%1</b> (Engine <b>%2</b>) "
                                             "aus der Datenbank entfernen ?").arg(parentCategory.encode("utf-8").decode("utf-8"),
                                                                                  descriptions.decode("utf-8")))
                myMessageBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                myMessageBox.setDefaultButton(QMessageBox.Yes)

                if myMessageBox.exec_() == QMessageBox.No:
                    return
                                                     # None      u"Kategoriename" , True = remove all articles inside
                self.model.removeArticle(current_article, parentCategory, True)

    def on_undo(self):
        print("Undo")
        self.treeView.undo()

    def on_redo(self):
        print("Redo")
        self.treeView.redo()

    @pyqtSlot()
    def on_expandall(self, state):

        if state:
            self.treeView.expandAll()
        else:
            self.treeView.collapseAll()

    @pyqtSlot()
    def on_newParentInDatebase(self):
        self.model.insertNewCategory()

    @pyqtSlot()                        #caller:     self.model, SIGNAL("askQuestion(QString, QString, QString)")
    def askQuestion(self, TITLE, TEXT1, BTN1, TEXT2=None, BTN2=None):
        '''
        Bring up a modal QMessageBox

        :param TITLE: Windwtitle
        :param TEXT1: First Textline
        :param BTN1:  First Buttontext
        :param TEXT2: Second Textline
        :param BTN2:  Second Buttontext
        :return: 0 if the dialog button1 was clicked, 1 of button2 was clicked
        '''

        title = str(unicode(TITLE).encode("utf-8")) if isinstance(TITLE, QString) else str(TITLE)
        text1 = str(unicode(TEXT1).encode("utf-8")) if isinstance(TEXT1, QString) else str(TEXT1)
        btn1 = str(unicode(BTN1).encode("utf-8")) if isinstance(BTN1, QString) else str(BTN1)

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle(title.decode("utf-8"))
        msgBox.setText("%s" % text1.decode("utf-8"))
        if TEXT2 is not None: msgBox.setInformativeText("%s" % str(unicode(TEXT2).encode("utf-8")) if isinstance(TEXT2,
                                                                              QString) else str(TEXT2).decode("utf-8"))
        msgBox.addButton("%s" % btn1.decode("utf-8"), QMessageBox.ActionRole)                             # ret = 0
        if BTN2 is not None: msgBox.addButton("%s" % str(unicode(BTN2).encode("utf-8")) if isinstance(BTN2,
                                    QString) else str(BTN2).decode("utf-8"), QMessageBox.RejectRole)        # ret = 2
        ret = msgBox.exec_()
        ret = int(ret)

        if ret == 0:
            return 0       # Result Button 1 (OK)
        else:
            return 1       # Result Button 2 (Cancel)

    def eventFilter(self, source, event):
        if source == self:
            if (event.type() == QEvent.DragEnter):
                #print("DragEnter! Main")
                if event.mimeData().hasUrls():
                    event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
                    #print "accept"


        if source == self.lbl_PreviewPic:          # if the lbl_PreviewPic Label
            if event.type() == QEvent.Resize:      # was resized
                pixmap = self.lbl_PreviewPic.pixmap() # check if currently is a pixmap shown
                if pixmap is not None:
                    self.update_Preview_Pixmap()   # is yes, call update_Preview (which recalculates and resizes pixm.)
                    # do not consume the event by returning True

            if (event.type() == QEvent.MouseButtonDblClick):
                if self.lE_Link.isEnabled():
                    self.setPicture()
                    event.accept()

            if (event.type() == QEvent.DragEnter):
                #print("DragEnter!")
                if self.lE_Link.isEnabled():
                    if event.mimeData().hasUrls():
                        event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
                        #print "accept"
                else:
                    event.ignore()
                    #print "ignore"
            if (event.type() == QEvent.Drop):

                if event.mimeData().hasUrls():   # if file or link is dropped
                    fileToImport=""

                    if event.mimeData().hasHtml():
                        print("it is a Online-Picture, lets download it...")
                        #TODO: if the Link does not end with any file-exsion, this will fail....
                        # need to search for extention and cut the rest away
                        for url in event.mimeData().urls():
                            url = QUrl.toString(url)
                            #print(url)
                            if url.toLower().endsWith(".jpg"):
                                extention = "jpg"
                            elif url.toLower().endsWith(".jpeg"):
                                extention = "jpeg"
                            elif url.toLower().endsWith(".png"):
                                extention = "png"
                            else:
                                #lets try it with an Jpeg
                                print("Can not identify file-Extension !")
                                return True

                            tempdir = tempfile.gettempdir()
                            filename = random.randint(1, 1000)

                            fileToImport = "%s/%s.%s" % (tempdir, filename, extention)

                            url = str(url)
                            #get around of some bot-prevention
                            req = urllib2.Request(url,
                               headers={'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; de-DE; rv:1.9.0.1) \
                                                                    Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'})
                            img = urllib2.urlopen(req)
                            with open(fileToImport, 'w') as f:
                                f.write(img.read())

                    else:
                        for url in event.mimeData().urls():
                            print(url)
                            fileToImport = str(url.toLocalFile())
                            print(fileToImport)

                    if os.path.isfile(fileToImport):
                        print("Open file for detailchooser:", fileToImport)
                        self.mydialog = detailChooser(fileToImport)
                        decission = self.mydialog.exec_()

                        if decission is 1:
                            fileToImport = str(self.mydialog.onFertig())
                        else:
                            #print("Es wurde ABBRECHEN geklickt")
                            return True
                        self.setPicture(fileToImport)

        return super(settings_dlg, self).eventFilter(source, event)

    def update_Preview_Pixmap(self, path=None):
        '''
        This is a helper-function which sets and resizes the Pixmap in my lbl_PreviewPic.
        If a path is provided, this function will set the given path as picture, if nothing was provided,
        it will only update the picture (reloading and resizing from the original stored image-file stored on disk
        :param path: filepath to existing file
        :return:
        '''
        if path is not None:
            if os.path.isfile(path):
                pixmap = QPixmap(path)
            else:
                pixmap = QPixmap(":/fromFile.png")
        else:  # if path is none
            selectedEngine, Category = self.treeView.getCurrentSelectedArticleAndItsParent()
            if selectedEngine == Category:
                pixmap = self.categoryImage_per_category_name(Category, self.lbl_PreviewPic.width(),
                                                              self.lbl_PreviewPic.height())
            else:
                if selectedEngine.imagepath is not None:
                    if os.path.isfile(os.path.join(cwd,selectedEngine.imagepath)):
                        pixmap = QPixmap(os.path.join(cwd,selectedEngine.imagepath))
                    elif os.path.isfile(selectedEngine.imagepath):
                        pixmap =QPixmap(selectedEngine.imagepath)
                    else:
                        pixmap = QPixmap(":/fromFile.png")
                else:
                    pixmap = QPixmap(":/fromFile.png")

        self.lbl_PreviewPic.setPixmap(pixmap.scaled(self.lbl_PreviewPic.size(), Qt.KeepAspectRatio,
                                                                Qt.SmoothTransformation))

    def categoryImage_per_category_name(self, categoryname, width, height):
        '''
        Take a categoryname and create a image-collection of all sub-engines fitting to width and height, keeping
        aspect ratio.
        :param categoryname: str("Kategoriename")
        :param width: int(<width in pixel>)
        :param height: int(<height in pixel>)
        :return: QPixmap()
        '''
        engines = self.model.getAllArticlesFromCategory(categoryname) # get list on relevant engines.
        if len(engines) > 1:                           # if there are more than 1 engine located in the given category
            # Calculate needed columns and rows
            row=0
            column=0
            maxcolumn=0
            engines_with_logo=[]
            for engine in engines:                     # for each engine in engines (all engines in one category)
                if os.path.isfile(engine.imagepath):   # check if the stored imagepath is existing
                    engines_with_logo.append(engine)   # if yes, store it to another interim list.
                    column +=1
                    if column > 2:                     # if column-count grow higher than 2 ? starting form 0
                        row += 1                       # a new row is needed
                        column = 0                     # column count starts at 0 again
                        maxcolumn = 2                  # remember what maximum columncount was
            if column < maxcolumn:                     # if columncount is lower than maxcolumn
                column = maxcolumn                     # update columcount to maxcolumn (if a new row was created)

            # Populate a interim Label with sublabels with pixmaps on it
            layout = QGridLayout()                     # create interim Layout
            parentlabel = QLabel()                     # create interim QLabel as parent
            parentlabel.setLayout(layout)              # set the interim Layout to the interim Label
            parentlabel.setAttribute(Qt.WA_TranslucentBackground)
            new_row=0
            new_column=0
            for engine in engines_with_logo:           # for each engine with a real existing logo
                sublabel = QLabel()                    # create sublabels
                sublabel.setAttribute(Qt.WA_TranslucentBackground)
                pixmap = QPixmap(engine.imagepath)
                # resize logos to fit into given width and height keeping aspect-ratios of logos
                sublabel.setPixmap(pixmap.scaled(width / (column+1),
                                                      height / (row+1),
                                                      Qt.KeepAspectRatio,
                                                      Qt.SmoothTransformation))
                layout.addWidget(sublabel,new_row, new_column)  # add the interim sublabel to the layout of parentlabel
                new_column +=1
                if new_column > 2:
                    new_row += 1
                    new_column = 0
            if len(engines_with_logo) > 0:
                return QPixmap().grabWidget(parentlabel) # return a "screenshot" of the parentlabel
            else:
                return QPixmap()

        elif len(engines) == 1:
            if engines[0].imagepath == None:
                return QPixmap()
            elif os.path.exists(engines[0].imagepath):
                return QPixmap(engines[0].imagepath)
            else:
                return QPixmap()
        else: # len is 0
            return QPixmap()

    @pyqtSlot()
    def validate_Link(self):
        """
        is triggered by "textChanged" Signal of the LineEdit for the Link
        """

        engine, category = self.treeView.getCurrentSelectedArticleAndItsParent()
        if engine == category:
            print("Ignore Validation on category")
            return

        if isinstance(engine, SearchEngine):
            if str(engine.link).startswith("-"):
                return 2

        resultLink = self.validation_Link.validate(self.lE_Link.text(), 0)
        #print("Validate Link is called...", self.dialogWASActive)
        if resultLink[0] != 2:
            palette = QPalette()
            palette.setColor(self.lE_Link.foregroundRole(), QColor('red'))
            self.lE_Link.setPalette(palette)
            if not self.dialogWASActive:
                self.dialogsActive = True
                self.askQuestion("Fehler","Der verwendete Link, muss wie folgt aufgebaut sein \n"
                                 "'http(s)://(www.)eineSuchmaschine.com/' \n"
                                 "im darauffolgenden Ausdruck, ersetzen Sie die Stelle, an der das Suchwort steht, mit '%s' \n"
                                 "es darf nur einmal (!) ein '%s' vorkommen \n\n"
                                 "Beispiel: 'https://www.google.de/#q=%s&safe=off'",
                                 "Ok")

                self.dialogsActive = False
                self.dialogWASActive = True
            return 1
        else:
            self.dialogWASActive = False
            palette = QPalette()
            palette.setColor(self.lE_Link.foregroundRole(), QColor('black'))
            self.lE_Link.setPalette(palette)

            return 2

    def dirty_lE_Link(self, status):
        self.lE_Link_is_dirty = status

    def dirty_lE_Anzeigename(self, status):
        print("dirty Anzeigename...")
        self.lE_Anzeigename_diry = status

    def onFinish(self, status):
        if status:
            if self.OkToContinue:
                self.model.saveDatabase()
                self.close()
        else:
            self.close()


if __name__ == "__main__":
    main(sys.argv)
