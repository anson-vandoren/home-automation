PIN_CLK = 14  # D5
PIN_DT = 13  # D7
PIN_ROT_SW = 12  # D6

DISPLAY_SCL = 5  # D1
DISPLAY_SDA = 4  # D2

_WIDTH = const(128)
MENU_WIDTH = const(32)
CONTROL_WIDTH = const(_WIDTH - MENU_WIDTH)

WIFI_SSID = "yourWiFiSSID"
WIFI_PASSWORD = "yourWiFiPassword"

URL_GET_TEMP = "http://api.example.com/current_temp"
URL_GET_SETPOINT = "http://api.example.com/temp_setpoint"

TEMP_UNITS = "F"
