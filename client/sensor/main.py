import machine
import time
import dht
import config
import network
import urequests
import ssd1306
import sys
import time


def get_temperature_and_humidity():
    dht22 = dht.DHT22(machine.Pin(config.DHT_PIN))
    dht22.measure()

    return dht22.temperature(), dht22.humidity()


def deepsleep():
    print(
        "Going into deepsleep for {seconds} seconds...".format(
            seconds=config.LOG_INTERVAL
        )
    )
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, config.LOG_INTERVAL * 1000)
    machine.deepsleep()


def show_error():
    led = machine.Pin(config.LED_PIN, machine.Pin.OUT)
    for i in range(3):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
    led.on()


def connect_wifi():
    print("Deactivating access point")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

    print("Activating station interface")
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)

    else:
        print("Already connected...")
    print("Network config:", sta_if.ifconfig())


def upload_data(temperature, humidity):
    url = config.WEBHOOK_URL
    payload = {
        "sensor_name": config.SENSOR_NAME,
        "sensor_id": config.SENSOR_ID,
        "temperature": temperature,
        "humidity": humidity,
    }

    response = urequests.post(url, json=payload)
    if response.status_code < 400:
        print("Successful update")
        response.close()
    else:
        print("Failed update:", response.text)
        response.close()
        raise RuntimeError("Failed update")


def is_debug():
    debug = machine.Pin(config.DEBUG_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if debug.value() == 0:
        print("Debug mode detected.")
        return True
    return False


def display_temperature_and_humidity(temperature, humidity):
    i2c = machine.I2C(
        scl=machine.Pin(config.DISPLAY_SCL_PIN), sda=machine.Pin(config.DISPLAY_SDA_PIN)
    )
    if 60 not in i2c.scan():
        raise RuntimeError("Cannot find display.")

    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.fill(0)

    display.text("{:^16s}".format("Temperature:"), 0, 0)
    display.text("{:^16s}".format(str(temperature) + "C"), 0, 16)

    display.text("{:^16s}".format("Humidity:"), 0, 32)
    display.text("{:^16s}".format(str(humidity) + "%"), 0, 48)

    display.show()
    time.sleep(5)
    display.poweroff()


def run():
    try:
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print("woke from deep sleep")
        else:
            print("power on or hard reset")
        connect_wifi()
        temperature, humidity = get_temperature_and_humidity()
        if is_debug():
            display_temperature_and_humidity(temperature, humidity)
        upload_data(temperature, humidity)
    except Exception as exc:
        sys.print_exception(exc)
        show_error()

    if not is_debug():
        deepsleep()


run()

