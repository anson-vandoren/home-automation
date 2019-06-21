from machine import Pin

_DIR_CW = const(0x10)
_DIR_CCW = const(0x20)

_R_START = const(0x0)
_R_CW_1 = const(0x1)
_R_CW_2 = const(0x2)
_R_CW_3 = const(0x3)
_R_CCW_1 = const(0x4)
_R_CCW_2 = const(0x5)
_R_CCW_3 = const(0x6)

_t_table = [
    [_R_START, _R_CCW_1, _R_CW_1, _R_START],
    [_R_START, _R_START, _R_CW_1, _R_CW_2],
    [_R_START, _R_CW_3, _R_CW_1, _R_CW_2],
    [_DIR_CW, _R_CW_3, _R_START, _R_CW_2],
    [_R_START, _R_CCW_1, _R_START, _R_CCW_2],
    [_R_START, _R_CCW_1, _R_CCW_3, _R_CCW_2],
    [_DIR_CCW, _R_START, _R_CCW_3, _R_CCW_2],
]

_STATE_MASK = const(0x7)
_DIR_MASK = const(0x30)


class Rotary(object):
    def __init__(self, pin_clk, pin_dt, min_val, max_val):
        self._min_val = min_val
        self._max_val = max_val
        # set up pins
        self._pin_clk = Pin(pin_clk, Pin.IN)
        self._pin_dt = Pin(pin_dt, Pin.IN)

        # enable IRQs
        self._pin_clk.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_trigger
        )
        self._pin_dt.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_trigger
        )

        # set initial state
        self._state = _R_START
        self._value = min_val

    def value(self):
        return self._value

    def _process_trigger(self, pin):
        # get the updated pin values
        next_pins = (self._pin_clk.value() << 1) | self._pin_dt.value()
        # if last state was a directional turn, reset, otherwise leave unchanged
        self._state &= _STATE_MASK
        # get next state from the transition table
        self._state = _t_table[self._state][next_pins]
        # check if a full 'click' is achieved
        direction = self._state & _DIR_MASK
        # convert direction bits to +/- 1
        incr = -2 * ((0x1) & ((direction >> 4) ^ (0x3))) + 1
        # update value if a full click
        self._value += incr if direction else 0
        # bound value at max and min
        self._value = min(self._max_val, max(self._min_val, self._value))

