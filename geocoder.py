import math
import requests


def geocode(geocode_data, **params):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": geocode_data,
        "format": "json",
        **params
    }
    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass
    json_response = response.json()
    return json_response


def get_coordinates(toponym):
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = (float(i) for i in toponym_coodrinates.split(" "))
    return toponym_longitude, toponym_lattitude


def get_ll_span(toponym):
    envelope = toponym['boundedBy']['Envelope']
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(b) - float(t)) / 2.0
    return (dx, dy)


def get_postal_code(request):
    try:
        toponym = get_toponym(request)
        postal_code = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        return postal_code
    except Exception as e:
        return False


def get_toponym(geocode_result):
    # Получаем первый топоним из ответа геокодера.
    try:
        toponym = geocode_result["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
    except (KeyError, IndexError):
        raise ValueError
    return toponym


def get_nearest_object(organization_text, point):
    organizations = get_organizations_to_point(organization_text, ll=point)
    nearest_organization = organizations['features'][0]
    return nearest_organization


def get_organizations_to_point(search_data, **params):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "3933df6d-0803-4c0c-9e9a-5859245e51eb"

    search_params = {
        "apikey": api_key,
        "text": search_data,
        "lang": "ru_RU",
        "type": "biz",
        **params
    }

    response = requests.get(search_api_server, params=search_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()

    return json_response


def get_organization_coord(organization):
    point = organization['geometry']['coordinates']
    lat, lon = point
    return str(lat), str(lon)


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def get_static_map(lat=None, lon=None, **params):
    # Собираем параметры для запроса к StaticMapsAPI:
    map_type = params.get('l', 'map')
    map_params = {
        'l': map_type,
        **params,
    }
    if not (lat is None or lon is None):
        ll = ",".join([lat, lon])
        map_params['ll'] = ll
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    response.raise_for_status()
    return response.content


def get_snippet(toponym, organization):
    lat, lon = get_organization_coord(toponym)
    org_lat, org_lon = get_organization_coord(organization)
    distance = lonlat_distance(list(map(float, (lat, lon))), list(map(float, (org_lat, org_lon))))
    org_name = organization['properties']['CompanyMetaData']['name']
    org_address = organization['properties']['CompanyMetaData']['address']
    org_hours = organization['properties']['CompanyMetaData']['Hours']
    snippet = {
        'name': org_name,
        'address': org_address,
        'hours': org_hours,
        'distance': distance,
    }
    return snippet


def pprint_snippet(snippet):
    print('Название:', snippet['name'])
    print('Адрес:', snippet['address'])
    print('Время работы:', snippet['hours']['text'])
    print('Расстояние от организации до исходной точки:', snippet['distance'], 'м')


def get_cords_by_click(x, y, ll_x, ll_y, z):
    delta_x = 360 / 2 ** z * 2 * 1.17
    k = 0.7
    delta_y = 360 / 2 ** z * 2 * k ** 2
    lat = x / 600 * delta_x + ll_x - delta_x / 2
    lon = -y / 450 * delta_y + ll_y + delta_y / 2
    return lat, lon

