import time
from rotary import Rotary

PIN_CLK = 14  # D5
PIN_DT = 13  # D7

r = Rotary(pin_clk=PIN_CLK, pin_dt=PIN_DT, min_val=50, max_val=90)

lastval = r.value()
while True:
    val = r.value()

    if lastval != val:
        lastval = val

        print("result =", val)

    time.sleep_ms(50)
