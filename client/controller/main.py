import utime
import ssd1306
import machine
from rotary import Rotary
from config import *

import roboto16 as small_font
import roboto48 as large_font
import writer


_WIDTH = 128

# set up rotary encoder
r_temp = Rotary(
    pin_clk=PIN_CLK,
    pin_dt=PIN_DT,
    min_val=50,
    max_val=90,
    range_mode=Rotary.RANGE_BOUNDED,
    enabled=False,
)
r_menu = Rotary(
    pin_clk=PIN_CLK,
    pin_dt=PIN_DT,
    min_val=0,
    max_val=3,
    range_mode=Rotary.RANGE_WRAP,
    enabled=True,
)


i2c = machine.I2C(scl=machine.Pin(DISPLAY_SCL), sda=machine.Pin(DISPLAY_SDA))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
# set display to partial brightness
disp_contrast = 100
display.contrast(disp_contrast)

small_font_writer = writer.Writer(display, small_font)
large_font_writer = writer.Writer(display, large_font)

lastval = r_temp.value()

is_menu = True
curr_sel = 1
r_menu.value(curr_sel)


_SEL_MENU = 0
_SEL_SET = 1
_MENU_WIDTH = 32

last_sw_click_millis = utime.ticks_ms()


def rotary_switch(pin):
    global is_menu, last_sw_click_millis
    # debounce switch click
    if utime.ticks_diff(utime.ticks_ms(), last_sw_click_millis) > 100:
        is_menu = not is_menu
        last_sw_click_millis = utime.ticks_ms()
        if r_temp.is_enabled:
            # switch to menu
            r_temp.disable()
            r_menu.enable()

            clear_control_area()
            draw_menu_box(color=1)

            display.show()
        else:
            # switch to control
            r_menu.disable()
            r_temp.enable()

            draw_menu_box(color=0)
            write_temp(r_temp.value())
            draw_control_box(color=1)

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


def draw_menu_box(color=1):
    top = curr_sel * 16
    bottom = top + 15

    display.hline(0, top, _MENU_WIDTH, color)
    display.hline(0, bottom, _MENU_WIDTH, color)
    display.vline(0, top, 16, color)
    display.vline(_MENU_WIDTH, top, 16, color)


def draw_control_box(color=1):
    display.rect(_MENU_WIDTH, 0, (128 - _MENU_WIDTH), 64, color)


def clear_control_area():
    display.fill_rect(_MENU_WIDTH, 0, (128 - _MENU_WIDTH), 64, 0)


def write_menu():
    print("writing menu text")
    display.fill_rect(0, 0, _MENU_WIDTH, 64, 0)

    # set menu
    labels = ["SET", "75F", "HUM", "45%"]
    for i, menu_label in enumerate(labels):
        str_len = small_font_writer.stringlen(menu_label)
        str_left = 1 + (_MENU_WIDTH - str_len) // 2
        small_font_writer.set_textpos(str_left, i * 16)
        small_font_writer.printstring(menu_label)

    # draw selected element
    draw_menu_box(color=1)


write_menu()
display.show()

while True:
    if r_temp.is_enabled:
        val = r_temp.value()
        if val != lastval:
            lastval = val
            print("updating control")

            write_temp(val)
            draw_control_box(color=1)
            display.show()

    elif r_menu.is_enabled:
        new_menu_val = r_menu.value()
        if curr_sel != new_menu_val:
            print("updating menu")
            # remove old selection box
            draw_menu_box(color=0)
            # update to new selection
            curr_sel = new_menu_val
            # draw new selection box
            draw_menu_box(color=1)
            # flip display buffer
            display.show()

    utime.sleep_ms(50)
