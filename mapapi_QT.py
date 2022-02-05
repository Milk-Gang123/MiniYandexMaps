import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from geocoder import *
from main_menu_design import Ui_MainWindow

LAT, LON = "37.620447", "55.751034"
MAX_SCALE, MIN_SCALE = 19, 1


class MapWidget(QtWidgets.QLabel):
    pointer_style = 'pm2' + 'org' + 'l'
    l_types = ["map", "sat", "sat,skl"]

    def __init__(self, parent, lat, lon):
        super().__init__(parent)
        self.l_pos = 0
        self.params = {'lat': lat, 'lon': lon, 'z': 18, 'pt': '', "l": self.l_types[self.l_pos]}
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
        elif key == 1050 or key == 82:
            self.l_pos = (self.l_pos + 1) % len(self.l_types)
        elif key == 1040 or key == 70:
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

    def from_pixel_to_coordinates(self, pixel_coord):
        # pixel_coord = self.mapFromParent(pixel_coord)
        # px, py = pixel_coord.x(), pixel_coord.y()
        # https://stackoverflow.com/a/2706847
        # pixel_coord = self.mapFromParent(pixel_coord)
        # pixel_globe_width = self.map_pixmap.size().width() * math.pow(2, self.params['z'])
        # pixel_globe_height = self.map_pixmap.size().height() * math.pow(2, self.params['z'])
        # x_pixels_to_degree_ratio = pixel_globe_width / 360
        # y_pixels_to_degree_ratio = pixel_globe_height / (2 * math.pi)
        # pixel_globe_center = pixel_globe_width / 2, pixel_globe_height / 2
        # pixel_glob_center_x, pixel_glob_center_y = pixel_globe_center
        # px, py = pixel_coord
        # longitude = (px - pixel_glob_center_x) / x_pixels_to_degree_ratio
        # latitude = (2 * math.atan(math.exp(py - pixel_glob_center_y))) / - y_pixels_to_degree_ratio
        # return latitude, longitude
        #
        # lat = (px / (self.map_pixmap.size().height() / 180) - 90) / -1
        # lng = py / (self.map_pixmap.size().width() / 360) - 180
        #
        # pixels_per_lon_degree = self.map_pixmap.width() / 360
        # pixels_per_lon_radian = self.map_pixmap.width() / (2 * math.pi)
        # tiles_no = 1 << self.params['z']
        # px /= tiles_no
        # py /= tiles_no
        # center_x, center_y = self.map_pixmap.width() / 2, self.map_pixmap.height() / 2
        # lng = (px - center_x) / pixels_per_lon_degree
        # lat_rad = (py - center_y) / -pixels_per_lon_radian
        # lat = math.degrees(2 * math.atan(math.exp(lat_rad)) - math.pi / 2)
        # lng = lng + float(self.params['lon'])
        # lat = lat + float(self.params['lat'])
        #
        # mapWidth = self.map_pixmap.width()
        # mapHeight = self.map_pixmap.height()
        # px /= 600 ** self.params['z']
        # py /= 450 ** self.params['z']
        # lng = ((360 * px) / mapWidth) - 180
        # lat = 90 * (-1 + (4 * math.atan(
        #     math.pow(math.e, (math.pi - (2 * math.pi * py) / mapHeight)))) / math.pi)
        # lng = lng + float(self.params['lon'])
        # lat = lat + float(self.params['lat'])
        #
        # lng = (px * 360) / (650 * math.pow(2, self.params['z'])) - 180
        # efactor = math.exp(0.5 - py / 450 / math.pow(2, self.params['z'])) * 4 * math.pi
        # lat = math.asin((efactor - 1) / (efactor + 1)) * 180 / math.pi
        # lng = lng + 180 + float(self.params['lon'])
        # lat = lat - 65.21843151737241 + float(self.params['lat'])
        return None, None


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
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
        self.btnClear.clicked.connect(self.clear_search_results)
        self.checkBoxPostCode.setStyleSheet('QCheckBox::indicator {width:  25px;height: 25px;}')
        self.checkBoxPostCode.stateChanged.connect(self.show_postal_code)

    def keyPressEvent(self, event):
        self.mapWidget.move_map(event.key())
        self.mapWidget.scale_map(event.key())
        if event.key() == 1040:
            self.lineEditSearch.clear()
        elif event.key() == 1050:
            self.btnMapStyle.setText(self.mapWidget.params["l"])

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.make_address_by_click(event)
        if event.button() == QtCore.Qt.RightButton:
            self.make_organization_by_click(event)

    def make_organization_by_click(self, event):
        if self.mapWidget.params['z'] < 14:
            return
        ll_x, ll_y = self.mapWidget.params['lat'], self.mapWidget.params['lon']
        x, y = get_cords_by_click(event.x() - 10, event.y() - 45, float(ll_x), float(ll_y),
                                  self.mapWidget.params['z'])
        toponym = get_toponym(geocode(f'{x},{y}', **self.mapWidget.params))
        address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        organizations = get_organizations_to_point(address, ll=f'{x},{y}')
        if not organizations['features']:
            return
        organization = organizations['features'][0]
        org_coord = organization['geometry']['coordinates']
        if lonlat_distance(org_coord, (x, y)) <= 50:
            self.clear_search_results()
            name = organization['properties']['name']
            address = organization['properties']['CompanyMetaData']['address']
            self.lineEditSearch.setText(name)
            self.labelFullAddress.setText(address)
            self.show_postal_code()

    def make_address_by_click(self, event):
        if self.mapWidget.params['z'] < 14:
            return
        self.clear_search_results()
        ll_x, ll_y = self.mapWidget.params['lat'], self.mapWidget.params['lon']
        x, y = get_cords_by_click(event.x() - 10, event.y() - 45, float(ll_x), float(ll_y),
                                  self.mapWidget.params['z'])
        self.mapWidget.add_pointer(x, y)
        self.mapWidget.update_image(**self.mapWidget.params)
        toponym = get_toponym(geocode(f'{x},{y}', **self.mapWidget.params))
        address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        self.lineEditSearch.setText(address)
        self.labelFullAddress.setText(address)
        self.show_postal_code()

    def change_mode(self):
        self.mapWidget.move_map(1050)
        self.btnMapStyle.setText(self.mapWidget.params["l"])

    def clear_search_results(self):
        self.mapWidget.move_map(1040)
        self.lineEditSearch.clear()
        self.labelFullAddress.clear()

    def search(self):
        try:
            address = self.lineEditSearch.text()
            toponym = get_toponym(geocode(address))
            cords = [str(i) for i in get_coordinates(toponym)]
            self.mapWidget.params['lat'] = cords[0]
            self.mapWidget.params['lon'] = cords[1]
            self.mapWidget.add_pointer(*cords)
            self.mapWidget.update_image(**self.mapWidget.params)
            full_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            self.labelFullAddress.setText(full_address)
        except Exception:
            self.statusBar.showMessage("Неверный запрос", 2 * 1000)
            self.statusBar.setStyleSheet("QStatusBar#statusBar {color: #f00;}")
        self.mapWidget.setFocus()
        self.show_postal_code()

    def show_postal_code(self):
        if self.checkBoxPostCode.isChecked():
            request = geocode(self.labelFullAddress.text())
            postal_code = get_postal_code(request)
            if postal_code and self.labelFullAddress.text() != "Полный адрес объекта":
                self.labelFullAddress.setText(f'{postal_code}, ' +
                                              self.labelFullAddress.text())
                self.len_postal_code = len(f'{postal_code}, ')
            else:
                self.len_postal_code = 0
        elif not self.checkBoxPostCode.isChecked() and self.len_postal_code:
            self.labelFullAddress.setText(
                self.labelFullAddress.text()[self.len_postal_code:])
            self.len_postal_code = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
