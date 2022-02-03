import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from geocoder import *

SCREEN_SIZE = [600, 450]
LAT, LON = "37.620447", "55.751034"
MAX_SCALE, MIN_SCALE = 19, 1


class MapWidget(QtWidgets.QWidget):
    pointer_style = 'pm2' + 'org' + 'l'
    l_types = ["map", "sat", "skl"]

    def __init__(self, parent, lat, lon):
        super().__init__(parent)
        self.l_pos = 0
        self.params = {'lat': lat, 'lon': lon, 'z': 18, 'pt': '', "l": self.l_types[self.l_pos]}
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
        delta = 298.033 * math.e ** (-0.678 * self.params['z'])
        if key == 16777236:
            self.params['lat'] = str(float(self.params['lat']) + delta)
        elif key == 16777234:
            self.params['lat'] = str(float(self.params['lat']) - delta)
        elif key == 16777235:
            self.params['lon'] = str(float(self.params['lon']) + delta)
        elif key == 16777237:
            self.params['lon'] = str(float(self.params['lon']) - delta)
        elif key == 1050:
            self.l_pos = (self.l_pos + 1) % len(self.l_types)
        self.params["l"] = self.l_types[self.l_pos]
        self.params['lat'] = str(max(min(float(self.params['lat']), 180), -180))
        self.params['lon'] = str(max(min(float(self.params['lon']), 90), -90))
        self.update_image(**self.params)

    def scale_map(self, key):
        if key == QtCore.Qt.Key.Key_PageUp:
            self.params['z'] = self.params['z'] + 1
        elif key == QtCore.Qt.Key.Key_PageDown:
            self.params['z'] = self.params['z'] - 1
        self.params['z'] = max(min(self.params['z'], MAX_SCALE), MIN_SCALE)
        self.update_image(**self.params)

    def add_pointer(self, lat, lon):
        pointer = f'{lat},{lon},{self.pointer_style}'
        self.params['pt'] += pointer


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
        self.lineEdit = QtWidgets.QLineEdit(MainWindow)
        self.lineEdit.setText('Россия, Москва, Большой Кремлёвский сквер')
        self.lineEdit.setGeometry(10, 420, 480, 25)
        self.button = QtWidgets.QPushButton(MainWindow)
        self.button.setGeometry(490, 420, 100, 25)
        self.button.setText('Искать')
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setupUi(self)
        self.initUI()
        self.button.clicked.connect(self.search)

    def initUI(self):
        self.setGeometry(400, 400, *SCREEN_SIZE)
        self.setWindowTitle('Карта')

    def load_image(self, image):
        pass

    def keyPressEvent(self, event):
        self.widget.move_map(event.key())
        self.widget.scale_map(event.key())

    def search(self):
        try:
            address = self.lineEdit.text()
            toponym = get_toponym(geocode(address))
            cords = [str(i) for i in get_coordinates(toponym)]
            self.widget.params['lat'] = cords[0]
            self.widget.params['lon'] = cords[1]
            self.widget.add_pointer(*cords)
            self.widget.update_image(**self.widget.params)
        except Exception as e:
            print('Неверный запрос')
        self.widget.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
