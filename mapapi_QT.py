import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from geocoder import *
from main_menu_design import Ui_MainWindow

SCREEN_SIZE = [639, 539]
LAT, LON = "37.620447", "55.751034"
MAX_SCALE, MIN_SCALE = 19, 1


class MapWidget(QtWidgets.QLabel):
    pointer_style = 'pm2' + 'org' + 'l'
    l_types = ["map", "sat", "skl"]

    def __init__(self, parent, lat, lon):
        super().__init__(parent)
        self.l_pos = 0
        self.params = {'lat': lat, 'lon': lon, 'z': 1, 'pt': '', "l": self.l_types[self.l_pos]}
        self.map = None
        self.map_pixmap = QPixmap()
        self.update_image(**self.params)

    @staticmethod
    def get_image(lat, lon, **params):
        image = get_static_map(lat, lon, **params)
        return image

    def update_image(self, **params):
        self.map = self.get_image(**params)
        self.set_image(self.map)

    def set_image(self, image):
        self.map_pixmap.loadFromData(image)
        self.setPixmap(self.map_pixmap)

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


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.mapWidget = QtWidgets.QWidget()
        self.len_postal_code = 0
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.mapWidget = MapWidget(self, LAT, LON)
        self.gridLayoutControls.addWidget(self.mapWidget, 0, 0, 2, 2)
        self.mapWidget.lower()
        self.btnSearch.clicked.connect(self.search)
        self.btnMapStyle.setFixedSize(31, 21)
        self.btnMapStyle.setText("map")
        self.btnMapStyle.clicked.connect(self.change_mode)
        self.btnClear.clicked.connect(self.clear_points)
        self.checkBoxPostCode.setStyleSheet('QCheckBox::indicator {width:  25px;height: 25px;}')
        self.checkBoxPostCode.stateChanged.connect(self.show_postal_code)

    def keyPressEvent(self, event):
        self.mapWidget.move_map(event.key())
        self.mapWidget.scale_map(event.key())
        if event.key() == 1040:
            self.lineEditSearch.setText("Введите поисковый запрос")
        elif event.key() == 1050:
            self.btnMapStyle.setText(self.mapWidget.params["l"])

    def mousePressEvent(self, event):
        ll_x, ll_y = self.mapWidget.params['lat'], self.mapWidget.params['lon']
        x, y = get_cords_by_click(event.x() - 10, event.y() - 10, float(ll_x), float(ll_y), self.mapWidget.params['z'])
        #self.mapWidget.add_pointer(float(ll_x), float(ll_y))
        #self.mapWidget.update_image(**self.mapWidget.params)
        self.mapWidget.add_pointer(x, y)
        self.mapWidget.update_image(**self.mapWidget.params)

    def change_mode(self):
        self.mapWidget.move_map(1050)
        self.btnMapStyle.setText(self.mapWidget.params["l"])

    def clear_points(self):
        self.mapWidget.move_map(1040)
        self.lineEditSearch.clear()


    def search(self):
        try:
            address = self.lineEditSearch.text()
            toponym = get_toponym(geocode(address))
            cords = [str(i) for i in get_coordinates(toponym)]
            self.mapWidget.params['lat'] = cords[0]
            self.mapWidget.params['lon'] = cords[1]
            self.mapWidget.add_pointer(*cords)
            self.mapWidget.update_image(**self.mapWidget.params)
        except Exception:
            print('Неверный запрос')
        self.mapWidget.setFocus()

    def show_postal_code(self):
        if self.checkBoxPostCode.isChecked():
            request = geocode(self.lineEditSearch.text())
            postal_code = get_postal_code(request)
            if postal_code:
                self.lineEditSearch.setText(
                    self.lineEditSearch.text() + f' Почтовый индекс: {postal_code}')
                self.len_postal_code = len(f' Почтовый индекс: {postal_code}')
            else:
                self.len_postal_code = 0
        elif not self.checkBoxPostCode.isChecked():
            self.lineEditSearch.setText(
                self.lineEditSearch.text()[:len(self.lineEditSearch.text()) - self.len_postal_code])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
