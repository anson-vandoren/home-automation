import utime
import ssd1306
import machine
from rotary import Rotary
from config import *

import roboto16 as small_font
import roboto48 as large_font
import writer


_WIDTH = 128
_HEIGHT = 64
_MENU_WIDTH = 32

# set up rotary encoder
r_temp = Rotary(
    pin_clk=PIN_CLK,
    pin_dt=PIN_DT,
    min_val=50,
    max_val=90,
    range_mode=Rotary.RANGE_BOUNDED,
    enabled=False,
)

# initialize display
i2c = machine.I2C(scl=machine.Pin(DISPLAY_SCL), sda=machine.Pin(DISPLAY_SDA))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
# set display to partial brightness
display.contrast(80)

small_font_writer = writer.Writer(display, small_font)
large_font_writer = writer.Writer(display, large_font)

lastval = r_temp.value()

do_set = False

last_click_millis = utime.ticks_ms()

current_temp = 83
setpoint_temp = 75
is_upstairs = True


def rotary_switch(pin):
    global last_click_millis, do_set, setpoint_temp, is_upstairs
    # debounce switch click
    if utime.ticks_diff(utime.ticks_ms(), last_click_millis) > 200:
        do_set = not do_set
        last_click_millis = utime.ticks_ms()

        if do_set:
            # TODO: update setpoint temp from web somewhere
            r_temp.enable()
            r_temp.value(setpoint_temp)
            # draw setpoint temp
            write_temp(r_temp.value())
            # draw box around temperature
            draw_control_box(color=1)
        else:
            is_upstairs = not is_upstairs
            # remove box around temperature
            draw_control_box(color=0)
            # disable rotary encoder
            setpoint_temp = r_temp.value()
            r_temp.disable()
            # TODO: write new setpoint to server
            # TODO: poll actual temperature
            # draw actual temperature
            write_temp(current_temp)
            write_menu()

        display.show()


# set up rotary encoder switch
r_sw = machine.Pin(PIN_ROT_SW, machine.Pin.IN)
r_sw.irq(trigger=machine.Pin.IRQ_RISING, handler=rotary_switch)


def write_temp(val):

    temp_str = str(val) + "°"
    temp_str_len = large_font_writer.stringlen(temp_str)

    temp_str_left = _MENU_WIDTH + (_WIDTH - temp_str_len - _MENU_WIDTH) // 2
    # the degree character renders too wide in chosen font. remove some rpad
    temp_str_left += 4

    large_font_writer.set_textpos(temp_str_left, 8)
    large_font_writer.printstring(temp_str)


def draw_control_box(color=1):
    display.rect(_MENU_WIDTH, 0, (128 - _MENU_WIDTH), 64, color)


def clear_control_area():
    display.fill_rect(_MENU_WIDTH, 0, (128 - _MENU_WIDTH), 64, 0)


def write_menu():
    display.fill_rect(0, 0, _MENU_WIDTH, 64, 0)

    # set menu
    labels = ["SET", str(setpoint_temp) + "F", "HUM", "45%"]
    for i, menu_label in enumerate(labels):
        str_len = small_font_writer.stringlen(menu_label)
        str_left = 1 + (_MENU_WIDTH - str_len) // 2
        small_font_writer.set_textpos(str_left, i * 16)
        small_font_writer.printstring(menu_label)


write_menu()
write_temp(current_temp)
display.show()

while True:
    if r_temp.is_enabled:
        val = r_temp.value()
        if val != lastval:
            lastval = val

            write_temp(val)
            draw_control_box(color=1)
            display.show()
    else:
        # TODO: poll current temperature periodically
        pass

    utime.sleep_ms(50)
