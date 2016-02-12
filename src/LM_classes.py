#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'matthias'

import csv
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import copy

CATEGORY, DESCRIPTION = range(2)

class SearchEngine(object):

    def __init__(self, name, link, imagepath, category=None):
        self.name = name
        self.link = link
        self.imagepath = imagepath
        self.category = category
        self.index = None

    def pixmap(self):
        if os.path.isfile(self.imagepath):
            return QPixmap(self.imagepath)
        else:
            return None

    def get_atName(self):
        return "@" + self.name

    def setIndex(self, Index):
        self.index = Index

    def __str__(self):
        return self.category

    def get_dict(self):
        """
        fieldnames = ["category","name","link","imagepath"]
        """
        article_dict = {}
        article_dict.update({"category": self.category.encode("utf-8")})
        article_dict.update({"name": self.name.encode("utf-8")})
        article_dict.update({"link": self.link.encode("utf-8")})
        article_dict.update({"imagepath": self.imagepath.encode("utf-8")})

        return article_dict

################################################################# define model and delegate for database - editor TREE:

class LM_EDITORModel_Tree(QAbstractItemModel):
    '''
    a model to display a few names, ordered by sex
    '''
    def __init__(self, parent=None):
        super(LM_EDITORModel_Tree, self).__init__(parent)
        self.database = {}  #{u'@google': <src.LM_classes.SearchEngine object at 0x7fdc32a92710>}
        self.engines = []
        self.categories = []
        self.descriptions = {}
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        #self.setupModelData()
        self.filename = ""
        self.dirty = False

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return 2

    def flags(self, index):
        #print("Flag:", index)
        if not index.isValid():
            return Qt.ItemIsEnabled

        #if index.column() == CATEGORY_editor:                                     # Unit and Price is not Editable !
        if isinstance(index.internalPointer().engine, SearchEngine):              # an singel article is only dragable
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                                Qt.ItemIsEditable|Qt.ItemIsDragEnabled)
        else:                                                                 # a category-node does accept drops
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                                Qt.ItemIsEditable|Qt.ItemIsDropEnabled)

        #return Qt.ItemFlags(QAbstractItemModel.flags(self, index)|
        #                   Qt.ItemIsEditable|Qt.ItemIsDragEnabled)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            #print("data: return Empty")
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        if role == Qt.UserRole:
            if item:
                if item.engine == None:
                    return item.category
                return item.engine
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        print("Set Data ", index.row(), index.column(), value)
        self.emit(SIGNAL("addToUndoStack(QString)"), u"Neuer Artikel")
        self.emit(SIGNAL("save_expansion()"))
        #print("indexValid:",index.isValid())
        #print("0 <= index.row():",0 <= index.row())
        #print("index.row() < len(self.engines)",index.row() < len(self.engines))
        if index.isValid() and 0 <= index.row():

            item = index.internalPointer()
            engine = item.engine
            column = index.column()

            if column == CATEGORY:
                if not isinstance(engine, SearchEngine):
                    print("you want to change a parent-category which will affect all childs ...")
                    old_text = item.category
                    new_text = str(unicode(value.toString()).encode("utf-8")).decode("utf-8")
                    child_count = item.childCount()
                    print("Childcount =", child_count)
                    for x in range(child_count):
                        child_item = item.child(x)
                        print("Update Child", child_item.engine.category)
                        child_item.engine.category = new_text
                        print("Update Child to", child_item.engine.category)
                        child_item.category = new_text
                    item.category = new_text
                    self.categories.append(new_text)
                    x = 0
                    for entry in self.categories:
                        if entry == old_text:
                            self.categories.pop(x)
                        x += 1
                else:
                    engine.category = str(unicode(value.toString()).encode("utf-8")).decode("utf-8")
                    print(engine.category)
                    if engine.category not in self.categories:
                        print("Add new Cat:", engine.category)
                        self.categories.append(engine.category)
                    #self.emit(SIGNAL("sort_request(PyQt_PyObject)"), index)
                    self.sort(0, 0)
                    count = 0
                    for engine_existing in self.engines:
                        if engine.category == engine_existing.category:
                            if engine_existing.name.startswith(engine.name):
                                count += 1
                    if count > 1:
                        engine.name = engine.name + "_{0}".format(count)

            elif column == DESCRIPTION:
                engine.name = str(unicode(value.toString()).encode("utf-8")).decode("utf-8")
                category = str(unicode(self.data(index.sibling(index.row(), CATEGORY)).toString()).encode("utf-8")).decode("utf-8")
                newArticle = None
                for articles in self.engines:
                    if articles.category == category:
                        if articles.name == engine.name:
                            newArticle = articles
                            break

                if category not in self.descriptions.keys():
                    self.descriptions.update({category : [engine.name]})
                else:
                    nestedList = self.descriptions.get(category)
                    nestedList.append(engine.name)
                    self.descriptions.update({category: nestedList})

            self.dirty = True
            self.setupModelData()

            if not isinstance(engine, SearchEngine):
                #print("Expand category", article, item.category)
                self.emit(SIGNAL("expand(QString)"), item.category)
            else:
                #print("emit setCurrent_row", article)
                self.emit(SIGNAL("set_current_row(PyQt_PyObject)"), item)

            self.emit(SIGNAL("restore_expansion()"))
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            self.emit(SIGNAL("check_dirty()"))
            return True
        return False

    def headerData(self, section, orientation, role):

        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == CATEGORY:
                return QVariant("Kategorie")
            elif section == DESCRIPTION:
                return QVariant("Bezeichnung")
        return QVariant(int(section + 1))

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QModelIndex()

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ['text/xml']

    def mimeData(self, indexes):

        articleObject = indexes[0].internalPointer().engine
        if articleObject is not None:
            mimedata = QMimeData()
            mimedata.setData('text/xml', "{0}|{1}".format(unicode(articleObject.category).encode("utf-8"),
                                                          unicode(articleObject.name).encode("utf-8")))
            return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        #print 'dropMimeData %s %s %s %s' % (data.data('text/xml'), action, row, parent)
        #print 'drop %s to category %s' % (str(unicode(data.data('text/xml')).encode("utf-8")).decode("utf-8"),
        #                                  unicode(parent.internalPointer().category).encode("utf-8"))
        self.emit(SIGNAL("addToUndoStack(QString)"), u"Neuer Artikel")
        target_category = parent.internalPointer().category
        data_extract = str(unicode(QString.fromUtf8(data.data('text/xml'))).encode("utf-8")).decode("utf-8")
        start_category = data_extract.split("|")[0]
        start_description = data_extract.split("|")[1]

        if target_category == start_category:
            return True

        article_to_move = None
        for article in self.engines:
            if article.category == start_category:
                if article.name == start_description:
                    print("found!")
                    article_to_move = article
                    break

        if article_to_move is not None:
            article_to_move.category = target_category

        self.dirty = True
        self.emit(SIGNAL("save_expansion()"))
        self.setupModelData()
        self.emit(SIGNAL("restore_expansion()"))
        self.emit(SIGNAL("expand(QString)"), target_category)
        self.emit(SIGNAL("select(QString, QString)"), target_category, start_description)
        self.emit(SIGNAL("check_dirty()"))

        return True

    def setupModelData(self):
        #print("Setup Model Data:")

        self.parents =None
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.categories.sort()
        for category in self.categories:
            if not self.parents.has_key(category):
                #print("Update Category with", category)
                newparent = TreeItem(None, category, self.rootItem)
                self.rootItem.appendChild(newparent)
                self.parents[category] = newparent

        for engine in self.engines:
            #print("check", engine)
            if isinstance(engine, SearchEngine):
                if not self.parents.has_key(engine.category):
                    #print("Add additional Category during population", engine.category)
                    newparent = TreeItem(None, engine.category, self.rootItem)
                    self.rootItem.appendChild(newparent)
                    self.parents[engine.category] = newparent
                parentItem = self.parents[engine.category]
                newItem = TreeItem(engine, engine.category, parentItem)
                parentItem.appendChild(newItem)

        self.reset()

    def searchModel(self, item):
        '''
        get the modelIndex for a given appointment
        '''
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''

            for child in node.childItems:

                if child.engine is not None and \
                                item.engine.category == child.engine.category and \
                                item.engine.name == child.engine.name:
                    #return QModelindex of parent
                    #print("found!", child.article.category, child.article.description, child.article.price)
                    index_parent = self.createIndex(child.parent().row(), 0, child.parent())
                    index_child = self.createIndex(child.row(), 0, child)
                    print(index_child.row(), index_parent.row())

                    return index_parent, index_child

                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result

        retarg = searchNode(self.parents[0])

        return retarg

    def insertNewArticle(self, category):
        print("Insert row in Model")
        self.emit(SIGNAL("addToUndoStack(QString)"), u"Neuer Artikel")
        newArticle = SearchEngine("Neu*","-","",category)
        self.engines.append(newArticle)
        self.engines.sort()
        #check if there is already a New, Empty Article in category, if yes, add _1 to it.
        count = 0
        for article_existing in self.engines:
            if newArticle.category == article_existing.category:
                if article_existing.name.startswith(newArticle.name):
                    count += 1
        if count > 1:
            newArticle.name = newArticle.name + "_{0}".format(count)
        self.emit(SIGNAL("save_expansion()"))
        self.setupModelData()
        self.emit(SIGNAL("restore_expansion()"))
        self.emit(SIGNAL("expand(QString)"), category)
        self.dirty = True
        return newArticle

    def insertNewCategory(self):
        print("Insert new Category")
        self.emit(SIGNAL("addToUndoStack(QString)"), u"Neuer Artikel")
        negativelist = []
        for categorie in self.categories:
            if categorie.startswith(u"_*_NEU"):
                negativelist.append(int(categorie.split("_*_NEU")[1]))

        negativelist.sort(reverse=True)
        if len(negativelist) > 0:
            freshIndex = negativelist[0] + 1
        else:
            freshIndex = 0
        categoriename = u"_*_NEU{0}".format(freshIndex)
        self.categories.append(categoriename)
        self.emit(SIGNAL("save_expansion()"))
        self.setupModelData()
        self.emit(SIGNAL("restore_expansion()"))
        self.emit(SIGNAL("expand(QString)"), categoriename)

    def removeArticle(self, article, category=None, removeCompleteCategory=False):
        print("remove Articles", article)
        self.emit(SIGNAL("addToUndoStack(QString)"), u"Neuer Artikel")
        if not removeCompleteCategory:   # remove a single article
            index = 0
            for existing_article in self.engines:
                if article == existing_article:
                    self.engines.pop(index)
                    break
                index += 1
        else:                            # remove a complete category (all its articles)
            # remove all articles which have category-name as category
            articles_in_category = self.getAllArticlesFromCategory(category)
            for current_article in articles_in_category:
                index = 0
                for existing_article in self.engines:
                    if current_article == existing_article:
                        self.engines.pop(index)
                        break
                    index += 1
            # remove "empty" category-name
            if category in self.categories:
                index = 0
                for existingCat in self.categories:
                    if category == existingCat:
                        self.categories.pop(index)
                        break
                    index += 1
        # reload Tree but save expansions
        self.dirty = True
        self.emit(SIGNAL("save_expansion()"))
        self.setupModelData()
        self.emit(SIGNAL("restore_expansion()"))
        self.emit(SIGNAL("check_dirty()"))

    def loadDatabase(self, filepath):
        """
        self.engines.append( Article(category, unit, price, description) ) >> List of class Article
        self.categories.add("Name of Category")                             >> List of available categories
        self.descriptions.update({category: nestedList})                    >> Dict, with nested lists (cat : descr.)

        :return: True or False
        """
        self.database = {} # clean database

        if not isinstance(filepath, str): # if filepath is not a string:
            try:
                filepath = str(unicode(filepath).encode("utf-8")).decode("utf-8")   # try to convert
            except:
                raise TypeError, "filename must be specified as a string str() not {0}".format(type(filepath))

        if  filepath == "":
            raise IOError, "no filename specified for loading"

        try:
            cwd = os.path.dirname(os.path.realpath(__file__))
            reader = csv.DictReader(open(filepath, "rb"), delimiter=",")
            for item in reader:
                # category,name,link,imagepath
                category = item.get("category").decode("utf-8")
                name = item.get("name").decode("utf-8")
                link = item.get("link").decode("utf-8")
                imagepath = item.get("imagepath").decode("utf-8")
                if imagepath.startswith("Logos"):
                    imagepath = os.path.join(cwd.split("/src")[0],imagepath)

                searchengine_new = SearchEngine(name, link, imagepath, category)
                atName = searchengine_new.get_atName()
                self.database.update()

                if atName not in self.database.keys():
                    self.database.update({atName : searchengine_new})
                else:
                    print("{0} befindet sich doppelt in der Datenbank und wurde ignoriert".format(atName))
                    pass # ignore doubles

        except:
            print(u'Datei "%s" nicht gefunden oder konnte nicht geöffnet werden, '
                  u'überprüfen Sie die Schreibweise' % filepath).encode("utf-8")
            return False
        finally:
            self.filename = filepath

        if len(self.database) == 0:
            return True

        for name, obj in self.database.iteritems():

            if obj.category not in self.categories:
                self.categories.append(obj.category)
                if obj.category not in self.descriptions.keys():
                    self.descriptions.update({obj.category : [name]})
                else:
                    nestedList = self.descriptions.get(obj.category)
                    nestedList.append(name)
                    self.descriptions.update({obj.category: nestedList})
            self.engines.append(obj)

        self.engines.sort()
        self.setupModelData()

        return True

    @pyqtSlot()   # this is called if the detail-edit dialog was dirty and something in my articles was changed.
    def on_reread_articles(self):
        print("rereading articles...")

        self.categories = []
        self.unit = []
        for article in self.engines:
            if article.category not in self.categories: self.categories.append(article.category)
            self.units.append(article.unit)
            if article.category not in self.descriptions.keys():
                self.descriptions.update({article.category : [article.name]})
            else:
                nestedList = self.descriptions.get(article.category)
                nestedList.append(article.name)
                self.descriptions.update({article.category: nestedList})

        self.dirty = True
        self.emit(SIGNAL("save_expansion()"))
        self.engines.sort()
        self.setupModelData()
        self.emit(SIGNAL("restore_expansion()"))
        self.emit(SIGNAL("check_dirty()"))

    def saveDatabase(self):
        print("Save that shit")
        articles_new = []

        for item in self.engines:
            dictpro = item.get_dict()
            articles_new.append(dictpro)

        with open(self.filename, 'w') as new_file:
            fieldnames = ["category","name","link","imagepath"]

            csvwriter = csv.DictWriter(new_file, delimiter=',', fieldnames=fieldnames)
            csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
            for row in articles_new:
                csvwriter.writerow(row)
        self.dirty = False
        self.emit(SIGNAL("check_dirty()"))
        self.emit(SIGNAL("database_changed()"))
        return True, None
        #except:
        #    return False, None

    def getAllArticlesFromCategory(self, category):
        matchlist = []
        for article in self.engines:
            if article.category == category:
                matchlist.append(article)

        return matchlist

    def undo_redo_setCurrentState(self, new_state=[]):
        #0    List with Article Objects
        #1    List with categories
        #2    nested list with descriptions
        #3    position of vertical scrollbar                       --- will be done in TreeView
        #4    int list, which parent-nodes are expanded            --- will be done in TreeView
        #5    a text-description which can be displayed as tooltip --- will be shown in mainwindow
        self.engines = new_state[0]
        self.categories = new_state[1]
        self.descriptions = new_state[2]
        self.dirty = True
        self.emit(SIGNAL("check_dirty()"))

class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, engine, category, parentItem):
        self.engine = engine
        self.parentItem = parentItem
        self.category = category
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 2

    def data(self, column):
        if self.engine == None:  #if the treeItem is a parent Node
            if column == CATEGORY:
                return QVariant(self.category)
            else:
                return QVariant("")
        else:
            if column == CATEGORY:
                return QVariant(self.engine.category)
            elif column == DESCRIPTION:
                return QVariant(self.engine.name)
        return QVariant()

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

class LM_EDITORDelegate_Tree(QItemDelegate):

    def __init__(self, parent=None):
        super(LM_EDITORDelegate_Tree, self).__init__(parent)
        self.installEventFilter(self)

    def paint(self, painter, option, index):
        QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        fm = option.fontMetrics

        if index.column() == DESCRIPTION:
            text = index.model().data(index).toString()
            document = QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            return QSize(document.idealWidth() + 5, (fm.height() * 2))
        return QItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        #print("Create Editor")
        self.currentIndex = index
        if index.column() == CATEGORY:
            #if item, where editor should be created is a category-parent
            if not isinstance((index.model().data(index, Qt.UserRole)), SearchEngine):
                self.negativeList = []
                model = index.model()
                #current = index   # find out current selected index
                #current_mapped = index.model().mapToSource(current)       # map the current (proxy) image to the model-index
                positiveCategory = model.data(index, Qt.UserRole) # get the article from the current selection

                self.negativeList = copy.deepcopy(index.model().categories) # all existing categories are NEGATIVE

                if self.negativeList is not None:
                    x = 0
                    for word in self.negativeList:
                        if word == positiveCategory:
                            self.negativeList.pop(x)
                            break
                        x += 1

                editor = QLineEdit(parent)
                #self.connect(editor, SIGNAL("returnPressed()"),
                #             self.commitAndCloseEditor)
                editor.textChanged.connect(self.checkDescEdit)

                return editor
            else:
                combobox = QComboBox(parent)
                #combobox.addItems(sorted(index.model().sourceModel().categories))
                for item in sorted(index.model().categories):
                    combobox.addItem(item)
                combobox.addItem("")
                combobox.setEditable(True)
                return combobox

        elif index.column() == DESCRIPTION:
            self.negativeList = []
            model = index.model()
            #current = index   # find out current selected index
            #current_mapped = index.model().mapToSource(current)       # map the current (proxy) image to the model-index
            positivePosition = model.data(index, Qt.UserRole) # get the article from the current selection

            self.negativeList_Article = index.model().getAllArticlesFromCategory(positivePosition.category)
            for entry in self.negativeList_Article:
                self.negativeList.append(entry.name)

            if self.negativeList is not None:
                x = 0
                for word in self.negativeList:
                    if word == positivePosition.name:
                        self.negativeList.pop(x)
                        break
                    x += 1

            editor = QLineEdit(parent)
            #self.connect(editor, SIGNAL("returnPressed()"),
            #             self.commitAndCloseEditor)
            editor.textChanged.connect(self.checkDescEdit)

            return editor
        else:
            return QItemDelegate.createEditor(self, parent, option,
                                              index)

    def commitAndCloseEditor(self):
        print("commit and CloseEditor")
        editor = self.sender()
        if isinstance(editor, (QTextEdit, QLineEdit)):
            self.emit(SIGNAL("commitData(QWidget*)"), editor)
            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)

    def checkDescEdit(self):
        #print("check Edit")
        editor = self.sender()
        if isinstance(editor, QLineEdit) and self.negativeList is not None:
            if editor.text() == "":
                editor.setStyleSheet("color: black")
                return
            else:
                for word in self.negativeList:
                    #if word.encode("utf-8").startswith(unicode(editor.text())):
                    if unicode(editor.text()) == word:
                        #print("Das hatten wir schon mal.")
                        editor.setStyleSheet("color: red")
                        break
                else:
                    #print("ok")
                    editor.setStyleSheet("color: black")

    def setEditorData(self, editor, index):
        #print("Set Editor Data")
        text = index.model().data(index, Qt.DisplayRole).toString()

        if index.column() == CATEGORY:
            #if item, where editor should be created is a category-parent
            if not isinstance((index.model().data(index, Qt.UserRole)), SearchEngine):
                print("pass")
                editor.setText(text)
                pass
            else:
                print("setText")
                i = editor.findText(text)
                if i == -1:
                    i = 0
                editor.setCurrentIndex(i)

        elif index.column() == DESCRIPTION:
            #print("Set Editor Data: Unit", text)
            editor.setText(text)
        else:
            print("Nothing ?")
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        #print("setModelData")
        if index.column() == CATEGORY:
            #if item, where editor should be created is a category-parent
            if not isinstance((index.model().data(index, Qt.UserRole)), SearchEngine):
                if editor.styleSheet() == "color: red":
                    model.emit(SIGNAL("askQuestion(QString, QString, QString)"),
                               "Doppelte Kategorie!".decode("utf-8"),
                               ("Der Kategorie <b>'{0}'</b> existiert bereits in Ihrer Datenbank, "
                               "es ist nicht erlaubt die selbe Kategorie mehrmals in der "
                                "Datenbank zu führen".format(unicode(editor.text()).encode("utf-8"))).decode("utf-8"),
                               "Ok")
                elif editor.text() == "":  # not red but empty
                    pass #abort here
                else:  # not red and not empty
                    text = editor.text()
                    if text.length() >= 3:
                        model.setData(index, QVariant(text))
                    else:
                        model.emit(SIGNAL("askQuestion(QString, QString, QString)"),
                           "Bezeichnung zu kurz".decode("utf-8"),
                           ("Die Kategorie <b>'{0}'</b> kann nicht angelegt werden, "
                           "da er weniger als 3 Zeichen enthällt. Bitte verwenden Sie eine längere "
                            "Bezeichnung".format(unicode(editor.text()).encode("utf-8"))).decode("utf-8"),
                           "Ok")
            else:
                text = editor.currentText()
                if text.length() >= 3:
                    model.setData(index, QVariant(text))
                else:
                    model.emit(SIGNAL("askQuestion(QString, QString, QString)"),
                           "Bezeichnung zu kurz".decode("utf-8"),
                           ("Die Kategorie <b>'{0}'</b> kann nicht angelegt werden, "
                           "da er weniger als 3 Zeichen enthällt. Bitte verwenden Sie eine längere "
                            "Bezeichnung".format(unicode(editor.currentText()).encode("utf-8"))).decode("utf-8"),
                           "Ok")

        elif index.column() == DESCRIPTION:
            if editor.styleSheet() == "color: red":
                model.emit(SIGNAL("askQuestion(QString, QString, QString)"),
                           "Doppelter Artikel!".decode("utf-8"),
                           ("Der Artikel <b>'{0}'</b> existiert bereits in Ihrer Datenbank, "
                           "es ist nicht erlaubt den selben Artikel mehrmals in der Datenbank zu "
                            "führen".format(unicode(editor.text()).encode("utf-8"))).decode("utf-8"),
                           "Ok")
            elif editor.text() == "":
                pass

            else:
                text = editor.text()
                if text.length() >= 3:
                    model.setData(index, QVariant(text))
                else:
                    model.emit(SIGNAL("askQuestion(QString, QString, QString)"),
                           "Bezeichnung zu kurz".decode("utf-8"),
                           ("Der Artikel <b>'{0}'</b> kann nicht angelegt werden, "
                           "da er weniger als 3 Zeichen enthällt. Bitte verwenden Sie eine längere "
                            "Bezeichnung".format(unicode(editor.text()).encode("utf-8"))).decode("utf-8"),
                           "Ok")
        else:
            QItemDelegate.setModelData(self, editor, model, index)

    def eventFilter(self, receiver, event):
        '''
        This eventFilter prevents the user for wrong and invalid inputs into the Spinbox (during enter of a formula)
        remember to install the eventfilter during init (self.installEventFilter(self)
        :param receiver:
        :param event:
        :return:
        '''
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                pass
        elif event.type() == QEvent.FocusOut:
            pass
        #Call Base Class Method to Continue Normal Event Processing
        return QItemDelegate.eventFilter(self, receiver, event)

class LM_TreeView(QTreeView):

    def __init__(self, parent=None):
        super(LM_TreeView, self).__init__(parent)
        self.undoStack = []
        self.undoStack_previousIndex = -1  # 0 is invalid for "undo"
        self.undoStack_current_saved = False
        self.currentExpansion = []
        self.currentSrollbarPosition = self.verticalScrollBar().value()

    def edit(self, index, trigger, event):
        # open Edit only, if anything was doubleclicked
        if trigger == QAbstractItemView.DoubleClicked:
            return QTreeView.edit(self, index, trigger, event)
        return False

    def save_expansion(self):
        """
        is called BEFORE setDate in my model --> Restored will be afterwards with restore_expansion
        """
        #print("Save Expansion")
        self.currentExpansion = []

        for index in range(self.model().rowCount()):
            #proxy_index = self.model().index(index,0)
            #mapped_index = self.model().mapToSource(proxy_index)
            mapped_index = self.model().index(index, 0, QModelIndex())
            text = unicode(self.model().data(mapped_index, Qt.DisplayRole).toString())

            expanded = self.isExpanded(mapped_index)
            if expanded:
                self.currentExpansion.append([expanded, text])
        #print("Save Scrollbarposition")
        self.currentSrollbarPosition = self.verticalScrollBar().value()
        print(self.currentSrollbarPosition)

    def restore_expansion(self):
        """
        is called AFTER setDate in my model (due to this, model is also resetted)
        :return:
        """
        #print("Restore Expansion")

        for index in range(self.model().rowCount()):
            #proxy_index = self.model().index(index,0)
            #mapped_index = self.model().mapToSource(proxy_index)
            mapped_index = self.model().index(index, 0, QModelIndex())
            text = unicode(self.model().data(mapped_index, Qt.DisplayRole).toString())

            for expansion in self.currentExpansion:
                if expansion[1] == text:
                    self.setExpanded(mapped_index, True)

        #self.scrollContentsBy(0, self.currentSrollbarPosition)
        self.verticalScrollBar().setSliderPosition(self.currentSrollbarPosition)

    def expandCategory(self, category):
        print("Expand Cat:", unicode(category))
        for index in range(self.model().rowCount()):
            #proxy_index = self.model().index(index,0)
            #mapped_index = self.model().mapToSource(proxy_index)
            mapped_index = self.model().index(index, 0, QModelIndex())
            text = unicode(self.model().data(mapped_index, Qt.DisplayRole).toString())

            if unicode(category) == text:
                self.setExpanded(mapped_index, True)
                self.selectionModel().select(mapped_index, QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)

    def selectArticle(self, category, articlename):
        print("Select Article", category, articlename)
        for index in range(self.model().rowCount()):
            #proxy_index = self.model().index(index,0)
            mapped_index = self.model().index(index, 0, QModelIndex())

            text = unicode(self.model().data(mapped_index, Qt.DisplayRole).toString())

            if unicode(category) == text:
                print("found category")
                for i in range(mapped_index.internalPointer().childCount()):
                    if mapped_index.internalPointer().child(i).engine.name == unicode(articlename):
                        print("found article")
                        item = mapped_index.internalPointer().child(i)
                        scrap , item_index = self.model().searchModel(item)
                        self.selectionModel().select(item_index,
                                                     QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)

    def getCurrentSelectedArticleAndItsParent(self):

        model = self.model()
        current_mapped = self.selectionModel().selectedIndexes()
        if len(current_mapped) > 0:
            current_mapped = self.selectionModel().selectedIndexes()[0]     # find out current selected index
        else:
            return False, False
        #current_mapped = self.model().mapToSource(current)       # map the current (proxy) image to the model-index
        selected_article = model.data(current_mapped, Qt.UserRole) # get the article from the current selection

        if isinstance(selected_article, SearchEngine):                         # if node is a parentnode, article is NONE
            if isinstance(selected_article, SearchEngine):   # check if it is a instance of articles.Articles
                parentCategory = selected_article.category
            else:
                print("FEHLER, Debug")                           # this happens if an empty QVariant was returned
                return                                           # abort here
        else:
            # if the selected article was only a parent node, get the "displayRole" which is the category in text
            parentCategory = unicode(model.data(current_mapped, Qt.DisplayRole).toString())

        return selected_article, parentCategory

    def cellButtonClicked(self, articleObject):
        if isinstance(articleObject, SearchEngine):
            self.selectArticle(articleObject.category, articleObject.name)
            self.model().categories
            self.emit(SIGNAL("view_details(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"),articleObject,
                                                            self.model().categories,
                                                            self.model().descriptions)

    def addToUndoStack(self, description_of_change=""):
        print("Create new UndoStack", description_of_change)

        if (len(self.undoStack) -1) > self.undoStack_previousIndex:
            print("something changed after undo-action...")
            self.undoStack = self.undoStack[:(self.undoStack_previousIndex-1)]
            print("new len is ", len(self.undoStack))
            self.undoStack_current_saved = False

        if len(self.undoStack) > 9:
            print("Stack is full (10), remove the oldest...")
            self.undoStack.pop(0)  # remove oldest undo-stack-list if undoStack is 10

        self.save_expansion()
        #collect data:
        articles_backup = copy.deepcopy(self.model().engines)
        categories_backup = copy.deepcopy(self.model().categories)
        descriptions_backup = copy.deepcopy(self.model().descriptions)
        position_of_scrollbar = copy.deepcopy(self.currentSrollbarPosition)
        current_expansions = copy.deepcopy(self.currentExpansion)
        selected_article, parentCategory = self.getCurrentSelectedArticleAndItsParent()
        selected_article = copy.deepcopy(selected_article)
        parentCategory = copy.deepcopy(parentCategory)
        description_text = description_of_change

        self.undoStack.append([articles_backup,      #0    List with Article Objects
                               categories_backup,    #1    List with categories
                               descriptions_backup,  #2    nested list with descriptions
                               position_of_scrollbar,#3    position of vertical scrollbar
                               current_expansions,   #4    int list, which parent-nodes are expanded
                               [selected_article, parentCategory], #5    current selected item (name of parent and article)
                               description_text])    #6    a text-description which can be displayed as tooltip
        self.undoStack_previousIndex = len(self.undoStack) -1
        self.emit(SIGNAL("checkActions()"))
        print("previousIndex in UndoStack is", self.undoStack_previousIndex)

    def undo(self):
        if len(self.undoStack) == 0:
            print("Return False, no items in undoStack")
            return False
        if self.undoStack_previousIndex == -1:
            print("no more undos possible")
            return False
        print("undo return to index", self.undoStack_previousIndex)
        if not self.undoStack_current_saved:
            print("current-Version is not saved... save it")
            self.addToUndoStack()  #save state BEFOR undo >> undoStack_previousIndex is +1 than
            self.undoStack_previousIndex = self.undoStack_previousIndex -1
            print("load index", self.undoStack_previousIndex)
            new_state = self.undoStack[self.undoStack_previousIndex]
            self.undoStack_current_saved = True
        else:
            new_state = self.undoStack[self.undoStack_previousIndex]
        self.model().undo_redo_setCurrentState(new_state)
        self.model().setupModelData()

        self.currentSrollbarPosition = new_state[3]
        self.currentExpansion = new_state[4]
        descr = new_state[5][0]
        if not descr:
            descr = ""
        elif isinstance(descr, unicode):
            descr = new_state[5][0]
        else:
            descr = new_state[5][0].name
        self.selectArticle(new_state[5][1], descr)
        self.restore_expansion()

        self.undoStack_previousIndex -= 1

        self.emit(SIGNAL("checkActions()"))
        print("undo done, new index is", self.undoStack_previousIndex, len(self.undoStack)-1)

    def redo(self):
        if self.undoStack_previousIndex >= (len(self.undoStack)-2):
            print("No redo is possible,",len(self.undoStack)-2, self.undoStack_previousIndex)
            return False
        print("redo with index", self.undoStack_previousIndex +2, len(self.undoStack))
        new_state = self.undoStack[self.undoStack_previousIndex +2]
        #new_state = self.undoStack[self.undoStack_previousIndex +1]


        self.model().undo_redo_setCurrentState(new_state)
        self.model().setupModelData()

        self.currentSrollbarPosition = new_state[3]
        self.currentExpansion = new_state[4]
        descr = new_state[5][0]
        if not descr:
            descr = ""
        elif isinstance(descr, unicode):
            descr = new_state[5][0]
        else:
            descr = new_state[5][0].name
        self.selectArticle(new_state[5][1], descr)
        self.restore_expansion()

        self.undoStack_previousIndex += 1
        self.emit(SIGNAL("checkActions()"))
        print("redo done, new index is", self.undoStack_previousIndex)

    def undo_possible(self):
        if len(self.undoStack) == 0:
            return False
        if self.undoStack_previousIndex == -1:
            return False
        else:
            return True

    def redo_possible(self):
        if len(self.undoStack) <= 1:
            return False
        if self.undoStack_previousIndex >= (len(self.undoStack)-2):
            return False
        else:
            return True

