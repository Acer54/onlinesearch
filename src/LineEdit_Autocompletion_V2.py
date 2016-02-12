#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This is a custom LineEdit-Class which makes it possible to get "Google-Suggestions" in different
auto-completion methodes.
Additionally, custom completions can be set.
Also an additional button can be set. The LineEdit appears like the searchfield at google.com

How to setup the lineEdit:

 = LineEdit_Autocomplete(w)                        #this is how to implement its LineEdit. Parent = w
.setCompletions(LIST_DATA)                         #Set a List with Strings for custom completion ["string", ..]
.setKeyWordForCompletion(".*@.+", " @")            #default is "whitespace" as trigger for suffix completion
.setGOOGLESEARCH(True)                             #activating Google-Suggest (default is "False")
.setLanguageForGOOGLESEARCH("de")                  #with German language (default is english)
.setCompletionDialogFoam(QCompleter.UnfilteredPopupCompletion) #Possible Options:    QCompleter.UnfilteredPopupCompletion
                                                                                     QCompleter.PopupCompletion
                                                                                     QCompleter.InlineCompletion
.setSpecialToolButton(iconpath, alignment, tooltip)    #display an integrated button in LineEdit
.setSpecialToolButton_newIcon(Iconpath)                #define a new icon for the toolButton
'''

import json
import urllib2
from PyQt4.QtCore import QEvent, Qt, QRegExp, pyqtSignal, pyqtSlot, QString, QTimer
from PyQt4.QtGui import QLineEdit, QCompleter, QStringListModel, QToolButton, QHBoxLayout, QIcon, QListView


 
class LineEdit_Autocomplete(QLineEdit):

    AutoComplete = pyqtSignal(QString)

    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
       
        self.completions = []                   # All available completions
        self.googlesuggestions = []             # This will be filled automatically if GOOGLESEARCH is True
        self.partials = []                      # Parsed completions according to partially typed word
        self.staticsuggestions = []             # Static suggestions list
       
        self.cursorpos = 0
        self.wordstart = -1                     # Start of word where cursor positioned
        self.wordend = -1                       # End of word where cursor is positioned
        self.lastindex = -1                     # Last used completion of available completions

        ######################## Completer for first part (without trigger)

        self.completer = QCompleter()
        self.completer.setParent(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.popup().setMinimumHeight(40)           # Keep a minumum heigt if the completer is shown
        self.setCompleter(self.completer)
        self.model = QStringListModel()
        self.model.setParent(self.completer)
        self.completer.setModel(self.model)
        self.completer.setMaxVisibleItems(6)
        self.__set_data(self.model)


        self.setCompletionDialogFoam()            # Set to standard (PopupCompletion)
        self.setKeyWordForCompletion()            # default keyword = "whitespace" - " "

        self.Timer = QTimer()                     # Setup singleshot Timer for GoogleSuggestions
        self.Timer.setSingleShot(True)

        self.setGOOGLESEARCH_attr = False         # initial Settings
        self.languageForGOOGLESEARCH = "en"


        self.textEdited.connect(self.onTextEdit)  # define connections
        self.Timer.timeout.connect(self.googlesearch)

        self.toolButton = None

    def set_data(self):
        """
        :Triggers the internal __set_data Methode
        """
        self.__set_data(self.model)

    def __set_data(self, model):
        """
        :param model: QStringlistmodel which is used
        :Is adding all suggestions which are available at the time of call to the model which manage the input
        for the used completer (Popup, Inline or Unfiltered Popup Completion
        """
        #print("Setup Completer with available completions")
        stringlist = []

        for item in self.staticsuggestions:
            stringlist.append(item)

        for item in self.googlesuggestions:
            stringlist.append(item)

        model.setStringList(stringlist)



    def setCompletionDialogFoam(self, QCompleter_Mode=QCompleter.PopupCompletion):
        '''
        Possible Options:    QCompleter.UnfilteredPopupCompletion
                             QCompleter.PopupCompletion
                             QCompleter.InlineCompletion
        '''
        self.completer.setCompletionMode(QCompleter_Mode)


    def setGOOGLESEARCH(self, bool):
        '''
        With this attribute the "google-suggest" function can be activated, and deactivated....
        '''
        self.setGOOGLESEARCH_attr = bool

    def setLanguageForGOOGLESEARCH(self, language="en"):
        self.languageForGOOGLESEARCH = language


    @pyqtSlot(QString)
    def onTextEdit(self, Text=None):
        '''
        If Googelsearch is set to "True" this will trigger the suggestions after 500ms, when the user do not enter
        anything.
        '''
        if self.setGOOGLESEARCH_attr:
            self.Timer.start(500)
            # Timer is connected to "googlesearch"

    @pyqtSlot()
    def googlesearch(self):
        '''
        Is collecting the current text entered and is requesting a suggestion-list
        This list is replacing the current self.googlesuggest
        '''
        #print("Googlesearch")
        query = self.text()
        text = unicode(query)              #convert QString to str.
        text = text.encode('utf-8')

        if text.find(self.keyWord) != -1:
            self.googlesuggestions = []
            self.__set_data(self.model)
            return

        result = self.get_querySuggestionList(text, self.languageForGOOGLESEARCH)

        self.googlesuggestions = []

        for suggestion in result:
            self.googlesuggestions.append(unicode(suggestion))

        #print(self.googlesuggestions)
        self.__set_data(self.model)

    def addCompletion(self, word):
        '''
        Adds a Word to the custom completions-list
        '''
        if not word in self.completions:
            self.completions.append(word)
           
    def delCompletion(self, word):
        '''
        Removes a Word from the custom completions-list
        '''
        if word in self.completions:
            self.completions.remove(word)
           
    def setCompletions(self, items=[]):
        '''
        items is a List of Strings
        '''
        self.completions = items

    def setKeyWordForCompletion(self, Regex_String=".*", Wordseparator=" "):
        '''
        Regex_String is something like this: ".*@.+"
        Per default, the Completion-List will be applied for evey Word entered
        '''
        self.keyWordREGEX = Regex_String     #".*@.+"
        self.keyWord = Wordseparator         # " @"     ... is watching for a "@" with a whitespace in front of it
       
    def getWords(self):
        #print('Func "getWords"')
        text = unicode(self.text())#.encode('utf-8')
        #print(text)
        if self.lastindex == -1:
            self.cursorpos = self.cursorPosition()
            self.wordstart = text.rfind(self.keyWord, 0, self.cursorpos) + 1  # all, which is in front of " @" is ONE word. and is ignored.
            #print(self.wordstart)
            #print(self.cursorpos)

        pattern = text[self.wordstart:self.cursorpos]

        #xyz = text.split(" ")
        #pattern = xyz[len(xyz) -1]
        #pattern = "".join(pattern)

        #print(pattern)

        self.partials = [item for item in self.completions if item.lower().startswith(pattern.lower())]
        #print(self.partials)
        return self.partials
       
    def applyCompletion(self, text):
        #oldlen = len(str(self.text()))
        #print('Laenge ohne Umwandlung "old":',oldlen)
        old = unicode(self.text())#.encode('utf-8')
        #print('Laenge nach Umwandlung "%s" ist %d Zeichen lang:' %(old, len(old)))

        self.wordend = old.find(" ", self.cursorpos)
       
        if self.wordend == -1:
            self.wordend = len(old)

        new = unicode(old[:self.wordstart]) + text + unicode(old[self.wordend:]) #beide decodieren ?

        self.setText(new)
        self.setSelection(len(unicode(old)), len(new))   #decode ?

    def get_querySuggestionList(self, query, language='de'):
        '''
        Takes a "query" and a "language"-definition (de = deutsch, en = englisch) and returns a list with search-suggestions
        by Google.com

        Example:
        myreturn = get_querySuggestionList("die", "de")
        print(myreturn)
        [u'die bahn', u'die zeit', u'die welt', u'die bestimmunng]

        please note, that the result is in unicode !
        '''
        querynew = query.replace(" ", "%20")     # replacing all whitespaces wit "%20"
        if query == "":
            #print("EMPTY")
            return []
        link = ('http://suggestqueries.google.com/complete/search?hl=%s&client=chrome&q=%s&hjson=t&cp3' %(language, querynew))
        #print("Asking Google for suggestions...")
        try:
            j = json.loads(unicode(urllib2.urlopen(link, timeout=400).read(), "ISO-8859-1"))
            if len(j) > 0:
                results = j[1]         # result for query "die" = [u'die bahn', u'die zeit', u'die welt', u'die bestimmun...]
            else:
                results = []
            #for suggestion in results:
                #print(suggestion.encode('utf-8'))     # for german umlauts
            #print("Suggestions received")
        except:
            #print("There was a Problem during response ... received an empty list :-(")
            results = []

        return results          # result for query "die" = [u'die bahn', u'die zeit', u'die welt', u'die bestimmun...]
       
    def event(self, event):
        if event.type() == QEvent.KeyPress:

            if event.key() in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_AltGr, Qt.Key_Alt):
                return True

            regex = QRegExp(self.keyWordREGEX, Qt.CaseInsensitive, QRegExp.RegExp)
            if regex.exactMatch(self.text()) and not (event.key() == Qt.Key_Backspace): # 16777219 is the backspace
            #if event.key() != Qt.Key_Backspace and event.key() != Qt.Key_Space:
                QLineEdit.event(self, event)
                self.getWords()
                if not len(self.completions):
                    return True
                if self.text() == "":
                    return True

                if len(self.partials) >= 1:
                    autocomplete = self.partials[0]
                    self.applyCompletion(autocomplete)
                    signalAttach = QString(autocomplete)
                    self.AutoComplete.emit(signalAttach)    #if autocomplete got a "@" in it, only the part, starting with "@..." will be sent
                    return True
                else:
                    signalAttach = QString('NONE')
                    self.AutoComplete.emit(signalAttach)
                    return True


            else:
                return QLineEdit.event(self, event)

        else:
            return QLineEdit.event(self, event)

    ####################### New in V2 ############### Add a clickable Butten into the LineEdit....

    def setSpecialToolButton(self, iconpath=None, Alignment=Qt.AlignRight, tooltip=None):

        self.toolButton = QToolButton(self)
        self.toolButton.setCursor(Qt.PointingHandCursor)
        self.toolButton.setFocusPolicy(Qt.NoFocus)
        if iconpath is not None:
            self.toolButton.setIcon(QIcon(iconpath))
            self.toolButton.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.addWidget(self.toolButton,0,Alignment)

        layout.setSpacing(0)
        layout.setMargin(5)
        # ToolTip
        if tooltip is not None:
            self.toolButton.setToolTip(tooltip)
    
    def setSpecialToolButton_newIcon(self, iconpath):
        
        if self.toolButton is not None:
            self.toolButton.setIcon(QIcon(iconpath))
        




def main():
    import sys
    from PyQt4.QtGui import QLabel, QVBoxLayout, QApplication, QWidget
   
    LIST_DATA = ['@gougl',
                 '@google',
                 '@goooogle',
                 '@gouggl',
                 '@whatelse']
             
    app = QApplication(sys.argv)
   
    # objects
    w = QWidget()
    label = QLabel(w)
    text = "Possible suffix: \n" + \
        "%s\n"
    label.setText(text % ", ".join(LIST_DATA))

    #setup lineEdit
    lineedit = LineEdit_Autocomplete(w)                        #this is how to implement its LineEdit. Parent = w
    lineedit.setCompletions(LIST_DATA)                         #Set a List with Strings for custom completion
    lineedit.setKeyWordForCompletion(".*@.+", " @")            #preset is "whitespace" as trigger for suffix completion
    lineedit.setGOOGLESEARCH(True)                             #activating Google-Suggest (default is "False")
    lineedit.setLanguageForGOOGLESEARCH("de")                  #with German language (default is english)
    lineedit.setCompletionDialogFoam(QCompleter_Mode=QCompleter.UnfilteredPopupCompletion)

    # layout
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(lineedit)
    w.setLayout(layout)

    w.show()
    sys.exit(app.exec_())
   
if __name__ == "__main__":
    main()











