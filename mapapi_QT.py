import sys
import random
import requests

from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog

from io import BytesIO

from geocoder import *

SCREEN_SIZE = [600, 450]
LAT, LON = "37.619727", "55.750536"


class MapWidget(QtWidgets.QWidget):
    def __init__(self, parent, lat, lon):
        super().__init__(parent)
        self.params = {'lat': lat, 'lon': lon, 'z': 19}
        self.label = QtWidgets.QLabel(self)
        self.map = None
        self.pixmap = QPixmap()
        self.update_image(**self.params)

    def get_image(self, lat, lon, **params):
        image = get_static_map(lat, lon, **params)
        return image

    def update_image(self, **params):
        self.map = self.get_image(**params)
        self.set_image(self.map)

    def set_image(self, image):
        self.pixmap.loadFromData(image)
        self.label.setPixmap(self.pixmap)

    def move_map(self, key):
        if key == 16777236:
            self.params['lat'] = str(float(self.params['lat']) + 0.0001)
        elif key == 16777234:
            self.params['lat'] = str(float(self.params['lat']) - 0.0001)
        elif key == 16777235:
            self.params['lon'] = str(float(self.params['lon']) + 0.0001)
        elif key == 16777237:
            self.params['lon'] = str(float(self.params['lon']) - 0.0001)
        self.update_image(**self.params)






class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 650)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = MapWidget(self.centralwidget, LAT, LON)
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
        self.widget.move_map(event.key())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())