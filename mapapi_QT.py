import sys

import PyQt5
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from geocoder import *

SCREEN_SIZE = [639, 539]
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
        elif key == 1040:
            self.clear_points()
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
        self.params['pt'] = pointer

    def clear_points(self):
        self.params["pt"] = ""

    def change_mode(self):
        self.l_pos = (self.l_pos + 1) % len(self.l_types)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_menu.ui', self)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.initUI()
        self.button.clicked.connect(self.search)
        self.check_box.stateChanged.connect(self.show_postal_code)

    def initUI(self):
        self.setGeometry(400, 400, *SCREEN_SIZE)
        self.setWindowTitle('Карта')

        self.widget = MapWidget(self.widget, LAT, LON)
        self.widget.setGeometry(10, 10, 650, 450)
        self.pushButton.clicked.connect(self.search)
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(580, 30, 31, 21)
        self.pushButton_3.setText("map")
        self.pushButton_3.clicked.connect(self.change_mode)
        self.pushButton_2.clicked.connect(self.clear_points)

    def keyPressEvent(self, event):
        self.widget.move_map(event.key())
        self.widget.scale_map(event.key())
        if event.key() == 1040:
            self.lineEdit.setText("Введите поисковый запрос")
        elif event.key() == 1050:
            self.pushButton_3.setText(self.widget.params["l"])

    def change_mode(self):
        self.widget.move_map(1050)
        self.pushButton_3.setText(self.widget.params["l"])

    def clear_points(self):
        self.widget.move_map(1040)
        self.lineEdit.setText("Введите поисковый запрос")

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

    def show_postal_code(self):
        if self.check_box.isChecked():
            request = geocode(self.lineEdit.text())
            postal_code = get_postal_code(request)
            if postal_code:
                self.lineEdit.setText(self.lineEdit.text() + f' Почтовый индекс: {postal_code}')
                self.len_postal_code = len(f' Почтовый индекс: {postal_code}')
            else:
                self.len_postal_code = 0
        elif not self.check_box.isChecked():
            self.lineEdit.setText(self.lineEdit.text()[:len(self.lineEdit.text()) - self.len_postal_code])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
