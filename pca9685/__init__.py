# coding=utf-8

# Python Standard Library Imports
import time
import math

# External Imports
pass

# Custom Imports
from pycomms import PyComms

# ============================================================================
# Adafruit PCA9685 16-Channel PWM Servo Driver (slightly modified)
# ============================================================================


class PCA9685():
    i2c = None

    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40):
        self.i2c = PyComms(address)
        self.address = address
        self.i2c.write8(self.__MODE1, 0x00)

    def setPWMFreq(self, freq):
        # Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.i2c.readU8(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.i2c.write8(self.__MODE1, newmode)        # go to sleep
        self.i2c.write8(self.__PRESCALE, int(math.floor(prescale)))
        self.i2c.write8(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.write8(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        # Sets a single PWM channel
        self.i2c.write8(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.i2c.write8(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.i2c.write8(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.i2c.write8(self.__LED0_OFF_H + 4 * channel, off >> 8)