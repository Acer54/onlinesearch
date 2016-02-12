#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from settings_v3 import settings_dlg
from src.FadingPicturesLabel import FadingStackedPictureWidget
from src.LineEdit_Autocompletion_V2 import LineEdit_Autocomplete
import res.resources

cwd = os.path.dirname(os.path.realpath(__file__))      # gives the path, where the script is located
#cwd = os.getcwd()                                     # gives only the path from where the script is executed ....

__version__ = "0.1.0"


def main(argv):
    app = QApplication(argv)
    qt_translator = QTranslator()
    qt_translator.load("qt_" + QLocale.system().name(),
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    mainwindow = SearchPromt(argv)
    mainwindow.show()
    sys.exit(app.exec_())


class SearchPromt(QWidget):

    def __init__(self, search="", *args):
        QWidget.__init__(self, *args)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # if no custom file is found, the default searchengines were loaded
        self.searchquerys = []
        self.language = "en"
        self.history = []
        self.SEARCHENGINES = {}
        self.__constructITEMS()
        self.__constructMENU()
        self.__constructLAYOUT()
        self.__setConnections()

        self.loadEngines()

        self.loadHistorySearches()
        self.setGoogleSuggest()
        self.setFixedSize(300, 280)

        self.__moveCenter()               # places the window in the middle of the screen

        #Setup Variables
        self.query = None
        self.readSettings()               # read settings for language and Google-suggest setting

        self.__checkForArguments(search)

    def __checkForArguments(self, arg):
        """
        :param arg: a list with arguments ["onlinesearch.py","this","is","a","test"]
        :return: addes the query after the programms-name into the LineEdit at Startup.

        If the statement is not true. nothing will be done here.
        """

        if len(arg) > 1:
            query = ' '.join(arg[1:])
            self.searchquery.setText(query)

    def __moveCenter(self):
        """
        Placing the windows in the middle of the screen
        """

        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def __constructITEMS(self):
        """
        Setup all necessary Items
        """

        #LineEdit:
        self.searchquery = LineEdit_Autocomplete()                       # Eigene Klasse mit Autocomplete funktion

        #Label for showing pictures
        self.labelIcon = FadingStackedPictureWidget()                    # Eigenge Klasse namens "fading stacked Pictures"
        self.labelIcon.setFocusPolicy(Qt.NoFocus)
        self.labelIcon.setFixedSize(280, 200)

        #self.labelIcon.showPicture(0)                                    # Anzeige des Index 0 Bildes
        self.labelIcon.addPicture(':/kombo-search-icon.png', 280, 200) # index 0

        #Buttons
        self.btnOK = QPushButton("Suchen...")
        self.btnOK.setFocusPolicy(Qt.TabFocus)
        self.btnOK.setAutoDefault(True)

        self.btnNOK = QPushButton("Abbrechen")
        self.btnNOK.setFocusPolicy(Qt.TabFocus)
        self.btnNOK.setAutoDefault(False)

        self.settingsPromt = settings_dlg(os.path.join(cwd,"engines.csv"), self)

    def __constructMENU(self):
        """
        Setup the menue
        """
        #Settingsmenu
        self.btnCONF = QToolButton()
        self.icon_Conf = QIcon(":/settings.png")
        self.btnCONF.setIcon(self.icon_Conf)
        self.btnCONF.setFocusPolicy(Qt.NoFocus)
        menu = QMenu()
        self.TriggerGoogleSuggestACT = QAction(u"Google-Vorschläge verwenden", self, triggered=self.setGoogleSuggest)
        self.TriggerGoogleSuggestACT.setCheckable(True)

        self.SettingsACT = QAction(u"Suchmaschinen verwalten", self, triggered=self.on_Settings)
        menu.addAction(self.TriggerGoogleSuggestACT)
        menu.addSeparator()
        actionGroupLanguage = QActionGroup(self)
        actionGroupLanguage.setExclusive(True)
        self.TriggerGoogleSuggestLanguageACT_DE = QAction(u"Deutsch", actionGroupLanguage,
                                                          triggered=lambda : self.setLanguageForGoogleSuggest("de"))
        self.TriggerGoogleSuggestLanguageACT_DE.setCheckable(True)

        self.TriggerGoogleSuggestLanguageACT_EN = QAction(u"Englisch", actionGroupLanguage,
                                                          triggered=lambda : self.setLanguageForGoogleSuggest("en"))
        self.TriggerGoogleSuggestLanguageACT_EN.setCheckable(True)
        menu.addAction(self.TriggerGoogleSuggestLanguageACT_DE)
        menu.addAction(self.TriggerGoogleSuggestLanguageACT_EN)
        self.deleteHistoryACT = QAction(u"gespeicherte Suchworte löschen", self, triggered=self.deleteHistory)
        menu.addAction(self.deleteHistoryACT)
        self.deleteHistoryACT.setEnabled(False)
        menu.addSeparator()
        menu.addAction(self.SettingsACT)

        self.btnCONF.setMenu(menu)
        self.btnCONF.setPopupMode(QToolButton.InstantPopup)

    def __constructLAYOUT(self):
        """
        Setup Layout
        """
        layoutZentral = QVBoxLayout()                         # Zentrales Layout erstellen und
        layoutZentral.addWidget(self.labelIcon)             # Bestandteile zuordnen (reihenfolge ist hier entscheidend)
        horizontalCombi = QHBoxLayout()
        horizontalCombi.addWidget(self.searchquery)
        horizontalCombi.addWidget(self.btnCONF)
        layoutZentral.addLayout(horizontalCombi)

        #layoutZentral.addWidget(self.searchquery)                      # ....
        horizontalBTN = QHBoxLayout()

        horizontalBTN.addWidget(self.btnOK)          # ....was "unter" oder "über" einem Widget steht
        horizontalBTN.addWidget(self.btnNOK)          # ....was "unter" oder "über" einem Widget steht
        layoutZentral.addLayout(horizontalBTN)

        self.setLayout(layoutZentral)                      # dem zentralen Widget ein Layout zuordnen

    def __setConnections(self):
        """
        Setup Signal - Slot connections
        """
        self.connect(self.searchquery, SIGNAL("AutoComplete(QString)"), self.on_AutoComplete)
        self.searchquery.editingFinished.connect(self.on_editingFinished)
        self.searchquery.textChanged.connect(self.on_textChanged)
        self.btnOK.clicked.connect(self.on_OK)
        self.btnNOK.clicked.connect(self.close)

    def __fillLabel(self):
        """
        construct QLabels(including pictures) in the stacked widget (FadingPicturesLabel)
        """
        # i = 0 is recerved for the "fallback-picture" which is shown, when no Searchengine is entered

        #self.labelIcon.removeWidget()
        if self.labelIcon.count() > 1:
            for i in range((self.labelIcon.count()-1), 0, -1):
                #print("removing Index:", i)
                widget = self.labelIcon.widget(i)
                self.labelIcon.removeWidget(widget)
            #print("After removing i have", self.labelIcon.count(), "stored widgets...")

        for key in self.SEARCHENGINES:
            path = self.SEARCHENGINES[key]["PIC"]

            if os.path.isfile(path) or path.startswith(":"):
                i = self.labelIcon.addPicture(path, 280, 200)
                #self.labelIcon.addPicture(path, 640, 480)
                self.SEARCHENGINES[key].update({"INDEX": i})
                #print("Fill Label with: ",key ,self.SEARCHENGINES[key]["INDEX"])
            elif len(self.SEARCHENGINES[key]["LINK"]) > 1:
                print("populating Label with CategoryImage", key[1:])
                pixmap = self.settingsPromt.categoryImage_per_category_name(key[1:],280,200)
                if not pixmap.isNull():
                    i = self.labelIcon.addPicture(pixmap, 280, 200,True)
                    self.SEARCHENGINES[key].update({"INDEX": i})
            else:
                continue

    def __startBrowser(self):
        # extract Searchengine and searchquery....

        text = unicode(self.searchquery.text())
        textsegments = text.split(" ")

        i = 0
        for segment in textsegments:
            if segment.startswith("@"):
                print("found engine starting with ",segment)
                break
            i += 1

        #Engine = textsegments[len(textsegments) -1]
        Enginesegments = textsegments[i:]
        lenEngine = len(Enginesegments)
        Engine = ' '.join(Enginesegments)


        print("then Engine is:", Engine)

        if Engine.startswith("@") and Engine in self.SEARCHENGINES.keys():
            searchstring = "%20".join(textsegments[:-lenEngine])
        else:
            searchstring = "%20".join(textsegments)

        searchstring = searchstring.lower()
        #searchstring = searchstring.replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace("ß", "ss")

        #print('Engine:', Engine)
        #print('Search for:', searchstring)

        # generate Link and open with prefered browser
        if Engine in self.SEARCHENGINES.keys():
            link_uncomplete_list = self.SEARCHENGINES[Engine]["LINK"]
            for link in link_uncomplete_list:
                if link.startswith("www."):
                    link = "http://"+link
                link_comlete = link.replace("%s", searchstring)
                QDesktopServices.openUrl(QUrl(link_comlete))
            return True

        else:
            #if requested engine is not defined in Searchengines dict
            #print('Searchengine not known, or not defined')
            link_uncomplete = "https://www.google.de/#safe=off&q=%s"
            link_comlete = link_uncomplete.replace("%s", searchstring)
            if QDesktopServices.openUrl(QUrl(link_comlete)):
                return True
            else:
                return False

    def setGoogleSuggest(self, active=True):
        self.searchquery.setGOOGLESEARCH(active)                           # Enables or disables Google-Suggest
        if active:
            self.TriggerGoogleSuggestLanguageACT_DE.setVisible(True)
            self.TriggerGoogleSuggestLanguageACT_EN.setVisible(True)
        else:
            self.TriggerGoogleSuggestLanguageACT_DE.setVisible(False)
            self.TriggerGoogleSuggestLanguageACT_EN.setVisible(False)

    @pyqtSlot()   # Auto-change Focus to "OK" Button, after Autocompletion is accepted (Enter is pressed)
    def on_editingFinished(self):
        self.btnOK.setFocus()

    @pyqtSlot(QString)   # is checking the content of LineEdit on every single keypress
    def on_textChanged(self, text):
        """
        resets the Logo which is shown if the "@..." is deleted or the completet LineEdit is empty (deleted by user)
        """

        if text.isEmpty() or not "@" in text:
            self.on_AutoComplete()

    def setLanguageForGoogleSuggest(self, language="de"):
        self.searchquery.setLanguageForGOOGLESEARCH(language)
        self.language = language
        if language == "de":
            self.TriggerGoogleSuggestLanguageACT_DE.setChecked(True)
        else:
            self.TriggerGoogleSuggestLanguageACT_EN.setChecked(True)

    @pyqtSlot()                                # Process request for online search
    def on_OK(self):
        """
        If the "Suchen" Button is pressed, the currend searchstring will be saved (including @.....)
        After this the browser is started.
        If this function returns true. The onlinesearch-app will be closed. (see closeEvent)
        :return:
        """
        self.savehistory()
        if self.__startBrowser():
            self.close()

    @pyqtSlot()
    def on_Settings(self):
        """
        Will be called, if the QAction "self.SettingsACT" which is part of the menue
        :return: Will open Settings-Dialog
        If the "OK" Button of Settings-Dialog is pressed, the new searchengines(dict) will be transfered in a new
        searchquerys-list, and a corresponding self.SEARCHENGINES(dict) where all links are stored.
        """
        print("SettingsDLG will be created")
        self.settingsPromt.show()
        self.connect(self.settingsPromt, SIGNAL("database_changed()"), self.on_Settings_accepted)
        self.settingsPromt.show()
        #print("SettingsDLG was left.")

    def on_Settings_accepted(self):
        print("Settings was accepted")
        self.loadEngines()
        self.__fillLabel()

    def keyPressEvent(self, QKeyEvent):
        """
        :param QKeyEvent: QKeyEvent
        :return: Close Application if <ESC> is pressed
        """
        if QKeyEvent.key() == Qt.Key_Escape:
            self.close()

    @pyqtSlot()                                # process close Event and post-actions
    def closeEvent(self, QCloseEvent):
        """
        Do post Action befor closing (save Settings if necessary)
        Also the closeEvent can be triggered by pressing <ESC> Key
        """

        #print("Post-Actions")
        self.writeSettings()
        #self.saveEngines()                   # "save Engines" is done by the Settings-dlg only
        QCloseEvent.accept()

    @pyqtSlot(QString)                         # process autocompletes (@goole, @youtube, @wikipedia aso.)
    def on_AutoComplete(self,Completion=None):
        """
        :param Completion: QString(u"@google") including the completion which was applyed
        :return: No return
        :function: Is checking, if the applyed Auto-Completion is on of the keys of SEARCHENGINES. If yes, the stored
        index of the coresponding QLabel(including chosen picture) will be called (shown). If there is no such key,
        it will set the "default" Picture.
        If the Completion is "None". it will set the default picture if the it is not set already...
        """
        #print("Habe folgende Completion erhalten:", Completion)
        if Completion is None:
            if self.labelIcon.currentIndex() is not 0:
                self.labelIcon.showPicture(0)
                self.query = None
            return
        try:
            query = unicode(Completion)

            if self.query != query:
                self.query = query
            else:
                return

        except:
            self.query = None

        #print('Schleife:', self.query)

        if self.query in self.SEARCHENGINES.keys():
            #print('Searchengine exists...')
            if self.SEARCHENGINES[self.query]["INDEX"] != "":
                self.labelIcon.showPicture(self.SEARCHENGINES[self.query]["INDEX"])
            else:
                self.labelIcon.showPicture(0)
                pass

        else:
            if self.labelIcon.currentIndex() is not 0:
                self.labelIcon.showPicture(0)    # will be used, for querys which are not defined yet

    def readSettings(self):

        settings = QSettings("Laumer", "Onlinesearch")
        checkGoogle = settings.value("checkGoogle", True)
        checkGoogle = checkGoogle.toBool()
        self.TriggerGoogleSuggestACT.setChecked(True if checkGoogle else False)

        language = settings.value("language", "en")
        language = language.toString()
        self.language = language
        self.setLanguageForGoogleSuggest(self.language)

    def writeSettings(self):

        settings = QSettings("Laumer", "Onlinesearch")
        settings.setValue("checkGoogle", self.TriggerGoogleSuggestACT.isChecked())
        settings.setValue("language", self.language)

    def loadEngines(self):

        self.SEARCHENGINES = {}
        self.searchquerys = []

        for engine in self.settingsPromt.model.engines:
            self.SEARCHENGINES.update({"@"+engine.name : {"LINK": [engine.link],
                                                          "PIC" : engine.imagepath,
                                                          "INDEX" : ""}})
        for category in self.settingsPromt.model.categories:
            for engine in self.settingsPromt.model.getAllArticlesFromCategory(category):
                if ("@"+category) not in self.SEARCHENGINES.keys():
                    print("Add Category", category)
                    self.SEARCHENGINES.update({"@"+category : {"LINK": [engine.link],
                                                          "PIC" : "",
                                                          "INDEX" : ""}})
                else:
                    print("Add a link to category", category, engine.name)
                    self.SEARCHENGINES["@"+category]["LINK"].append(engine.link)

        for key in self.SEARCHENGINES.iterkeys():
            self.searchquerys.append(key)

        print("SEARCHENGINES:", self.SEARCHENGINES)
        print("Searchquerys:", self.searchquerys)
        self.searchquery.setCompletions(self.searchquerys) # die Liste mit den vordefinierten Such-Ergänzungen wird übergeben
        self.searchquery.setKeyWordForCompletion(".*@.+", " @")

        #self.searchquery.setCompletionDialogFoam(QCompleter.UnfilteredPopupCompletion)
        self.searchquery.setCompletionDialogFoam(QCompleter.PopupCompletion)
        #self.searchquery.setCompletionDialogFoam(QCompleter.InlineCompletion)
        self.__fillLabel()

        return True

    def loadHistorySearches(self):

        basename = "history"
        #cwd = os.getcwd()
        fileName = '%s/%s.onlinesearch' % (cwd, basename)
        try:

            self.history = pickle.load(open(fileName, "rb" ) )
            #print("loaded %d searchquerys from history-file" % len(self.history))
            self.searchquery.staticsuggestions = self.history
            self.searchquery.set_data()
            self.deleteHistoryACT.setEnabled(True)                # if a file was found and loaded, provide ACT

            return True
        except:
            self.deleteHistoryACT.setEnabled(False)
            return False

    def savehistory(self):
        """
        Will be done everytime when "OK" is klicked and the browser is opened
        Is saving the last 10 entered searchstring.
        :return: True or False
        """
        try:
            if self.searchquery.text().isEmpty():                   # Do not write "" to history...
                return False
            elif unicode(self.searchquery.text()) in self.history:  # do not write history if query is already included
                return False

            if len(self.history) > 10:
                self.history.pop(10)

            self.history.append(unicode(self.searchquery.text()))
            basename = "history"
            fileName = '%s/%s.onlinesearch' % (cwd, basename)
            pickle.dump(self.history, open(fileName, "wb"))
            return True
        except:
            return False

    def deleteHistory(self):
        basename = "history"
        fileName = '%s/%s.onlinesearch' % (cwd, basename)
        os.remove(fileName)
        self.loadHistorySearches()

    def askQuestion(self, text1, btn1, text2=None, btn2=None):
        text1 = str(text1)
        btn1 = str(btn1)
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("%s" % text1.decode("utf-8"))
        if text2 is not None: msgBox.setInformativeText("%s" % text2.decode("utf-8"))
        msgBox.addButton("%s" % btn1.decode("utf-8"), QMessageBox.ActionRole)                             # ret = 0
        if btn2 is not None: msgBox.addButton("%s" % btn2.decode("utf-8"), QMessageBox.RejectRole)        # ret = 2
        ret = msgBox.exec_()
        ret = int(ret)

        if ret == 0:
            return 0       # Result Button 1 (OK)
        else:
            return 1       # Result Button 2 (Cancel)

class WorkerThread(QThread):


    def __init__(self, parent, function, *args, **kwargs):
        QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

    #def __del__(self):
    #    self.wait()

    def run(self):
        result = self.function(*self.args,**self.kwargs)
        #print("Result in Worker:", result)
        self.parent.emit(SIGNAL("searchquery(QString)"), QString(result))
        return


if __name__ == "__main__":
    main(sys.argv)


'''
Versionhistory:
0.0.1               Initial Version
0.0.2               After Adding a Searchengine, including a picture, pictures were loaded again
0.0.3               Some Bugs
0.0.4               Some Bugs
0.0.5               Evaluation Arguments given, now you can drag and drop a query from any other programm to this...
0.0.6               Now, Logos can be choosen by a screenshot.
0.0.7               use newest Version of detail-chooser (can move croping Area ...aso)
0.0.8               updated the usage of different Mouse-Cursors in Detail-Chooser...
0.1.0               Excluded speech-recognizer ...
'''



