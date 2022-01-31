import sys
import random
import requests

from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog

from io import BytesIO

from geocoder import *

SCREEN_SIZE = [600, 450]
lat, lon = "37.619727", "55.750536"


class MapWidget(QtWidgets.QWidget):
    def __init__(self, parent, lat, lon):
        super().__init__(parent)
        self.params = {"l": "map"}
        self.map = self.get_image(lat, lon, self.params)
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.map)
        self.label = QtWidgets.QLabel(self)
        self.label.resize(*SCREEN_SIZE)
        self.set_image(self.pixmap)

    def get_image(self, lat, lon, params):
        image = get_static_map(lat, lon, **params)
        return image

    def set_image(self, image):
        self.label.setPixmap(self.pixmap)

    def updateimage(self):
        self.map = self.get_image(lat, lon, self.params)
        self.set_image()

    def setl(self, l):
        self.params["l"] = l


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 650)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = MapWidget(self.centralwidget, lat, lon)
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 400, *SCREEN_SIZE)
        self.setWindowTitle('Карта')

    def load_image(self, image):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.widget.params["l"] == "map":
                self.widget.setl("sat")
            else:
                self.widget.setl("map")
            self.widget.updateimage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())