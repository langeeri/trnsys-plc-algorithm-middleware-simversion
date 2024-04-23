
WEBSERVER_CONFIG = {
        "host": "127.0.0.1",
        "port": 5000,
    }


DIRECTORY_PATH_OTE = 'TestingSequenceOTE_all/'
DIRECTORY_PATH_METEO = 'TestingSequenceMeteo_all/'

FAVICON_SOURCE = 'static/favicon.ico'

ENDPOINT = "/v1/forecast"
LATITUDE = "50.088"
LONGITUDE = "14.420"
PARAMS = "hourly=temperature_2m,shortwave_radiation&timeformat=unixtime"

# OpenMeteo path
GET_METEO_PATH = f"{ENDPOINT}?latitude={LATITUDE}&longitude={LONGITUDE}&{PARAMS}"

# OTE path
GET_OTE_PATH = '/get_ote_data'