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

# _t_table = [
#     [_R_START, _R_CCW_1, _R_CW_1, _R_START],
#     [_R_START, _R_START, _R_CW_1, _R_CW_2],
#     [_R_START, _R_CW_3, _R_CW_1, _R_CW_2],
#     [_DIR_CW, _R_CW_3, _R_START, _R_CW_2],
#     [_R_START, _R_CCW_1, _R_START, _R_CCW_2],
#     [_R_START, _R_CCW_1, _R_CCW_3, _R_CCW_2],
#     [_DIR_CCW, _R_START, _R_CCW_3, _R_CCW_2],
# ]

_t_table = [
    [_R_START, _R_CCW_1, _R_CW_1, _R_START],
    [_R_CW_2, _R_START, _R_CW_1, _R_START],
    [_R_CW_2, _R_CW_3, _R_CW_1, _R_START],
    [_R_CW_2, _R_CW_3, _R_START, _DIR_CCW],
    [_R_CCW_2, _R_CCW_1, _R_START, _R_START],
    [_R_CCW_2, _R_CCW_1, _R_CCW_3, _R_START],
    [_R_CCW_2, _R_START, _R_CCW_3, _DIR_CW],
]

_STATE_MASK = const(0x7)
_DIR_MASK = const(0x30)


def _bound(value, incr, lower_bound, upper_bound):
    return min(upper_bound, max(lower_bound, value + incr))


def _wrap(value, incr, lower_bound, upper_bound):
    range = upper_bound - lower_bound + 1
    value = value + incr

    if value < lower_bound:
        value += range * ((lower_bound - value) // range + 1)

    return lower_bound + (value - lower_bound) % range


class Rotary(object):
    RANGE_BOUNDED = const(1)
    RANGE_WRAP = const(2)

    def __init__(self, pin_clk, pin_dt, min_val, max_val, range_mode, enabled):
        self._min_val = min_val
        self._max_val = max_val
        self._range_mode = range_mode
        # set up pins
        self._pin_clk = Pin(pin_clk, Pin.IN, Pin.PULL_UP)
        self._pin_dt = Pin(pin_dt, Pin.IN, Pin.PULL_UP)

        # set initial state
        self._state = _R_START
        self._value = min_val

        if enabled:
            self.enable()
        else:
            self.is_enabled = False

    def enable(self):
        # enable IRQs
        self._pin_clk.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_trigger
        )
        self._pin_dt.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_trigger
        )
        self.is_enabled = True

    def disable(self):
        self._pin_clk.irq(handler=None)
        self._pin_dt.irq(handler=None)
        self.is_enabled = False

    def value(self, new_val=None):
        if new_val is None:
            return self._value
        else:
            self._value = new_val

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
        incr = -2 * ((0x1) & ((direction >> 4) ^ (0x3))) + 1 if direction else 0

        if not incr:
            return

        # bound value at max and min
        if self._range_mode == self.RANGE_BOUNDED:
            self._value = _bound(self._value, incr, self._min_val, self._max_val)
        elif self._range_mode == self.RANGE_WRAP:
            self._value = _wrap(self._value, incr, self._min_val, self._max_val)
