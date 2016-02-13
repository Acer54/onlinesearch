#Online-Search, schnelle Onlinesuche
###Abhängigkeiten: python 2.7, PyQt4, Imagemagik, python-wand

![ScreenShot1](http://s8.postimg.org/v1557ijf9/screen1.png)

Dies ist ein kleines Programm, das eigentlich als "Rumprobierprojekt" geplant war um etwas mehr mit PyQt4 
zu machen, hat sich dann allerdings schnell zu einem vielgenutzten alltäglichen Helfer entwickelt.

Dieses Script öffnet ein kleines Fenster mit einem LineEdit, einem OK und Abbrechen Button in dem der User 
eine Such-Phrase eingeben kann wie:

"Etwas neues @amazon", was den Browser öffnet und auf die Seite "www.amazon.de/q=etwas%20neues" geht.

![ScreenShot2](http://s29.postimg.org/uh39504vb/screen2.png)

Das LineEdit indem der User seine Such-Phrase eingibt, hat "google-suggest" funktionalität und ein Gedächtnis
über vorherige Suchanfragen.

Es bietet ausserdem die Möglichkeit die Suchmaschinen nicht nur selbst hinzu zu fügen, Logos dafür zu vergeben und 
diese zu Kategorisieren, sondern auch, dass der user mittels "Kategorien" suchen kann.

![ScreenShot3](http://s30.postimg.org/fhwv5fj29/screen3.png)

Sucht der User z.B. nach "Etwas neues @shoppingseiten", öffnet sich ein Browser mit mehreren Tabs, die z.B.
amazon, ebay, billiger.de und und und durchsuchen.

Ausserdem habe ich das Script mittel "xbindkeys" auf einen Shortcut gelegt, was mir erlaubt dieses Fenster jederzeit
in kürzester Zeit zu öffnen und komplett ohne Maus zu bedienen.

### Getestet unter Ubuntu 14.04