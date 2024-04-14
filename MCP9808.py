# -----------------------------------------
#                 NOTES 
# -----------------------------------------
# 
# Dieter Steinhauser
# 10/2023
# MCP9808 I2C Driver


# -----------------------------------------
#               IMPORTS
# -----------------------------------------

desc = r"""none for the moment"""


from machine import Pin, I2C
from time import sleep
from upy_i2c_drivers.i2c_device import Device, Register, Field
from upy_i2c_drivers.helpers import *
# -----------------------------------------
#                Class:
# -----------------------------------------

class MCP9808(Device):

    I2C_MIN_FREQ = 100_000
    I2C_MAX_FREQ = 400_000
    DEFAULT_ADDR = 0x18
    # ALT_ADDR = [x for x in range (0x12, 0x18, 1)]

    CONFIG: Register
    UP_ALERT: Register
    LO_ALERT: Register
    CRIT_ALERT: Register
    TEMP: Register
    MFTR_ID: Register
    DEV_ID: Register
    RES: Register


    def __init__(self, name:str, address:int, i2c_bus, width=16, description = None, *args, **kwargs) -> None:
        """Object initialization for MCP9808. Follow device initialization and adds register information to object"""
        description = desc if desc is None else description
        super().__init__(name, address, i2c_bus, description, width, *args, **kwargs)

        # Add device registers
        self.add_register("CONFIG", 0x1, r_w = "R/W", description='Configure Device Settings')
        self.add_register("UP_ALERT", 0x2, r_w = "R/W", description=' Alert Temperature Upper Boundary Trip register')
        self.add_register("LO_ALERT", 0x3, r_w = "R/W", description=' Alert Temperature Lower Boundary Trip register')
        self.add_register("CRIT_ALERT", 0x4, r_w = "R/W", description=' Critical Temperature Trip register')
        self.add_register("TEMP", 0x5, r_w = "R/W", description='Temperature register')
        self.add_register("MFTR_ID", 0x6, r_w = "R/W", description='Mode Control')
        self.add_register("DEV_ID", 0x7, r_w = "R/W", description='Operating Status')
        self.add_register("RES", 0x8, r_w = "R/W", description='Operating Status')

        # Add fields to each register
        # self.VREF_LOW.add_field(name='REF_LSB', bit_offset=0, width=8, r_w="R/W", description="VREF Lower byte. 10 bits total.")

    def temperature_c(self):
        """
        Query Temperature data in degrees Celsius.

        :return: temp_celsius - Temperature in Celsius
        :rtype: int
        """

        # TCRIT, TUPPER, TLOWER, SIGN, DATA (11:0)
        # read the temperature register
        data = self.TEMP.read()

        # Evaluate if the temperature is negative.
        neg_sign = True if (data & 0x1000) == 0x1000 else False

        # Condition the temperature data.
        upper = (0x0F00 & data) >> 8
        lower = (0x00FF & data)
        temp = ((upper * 16) + (lower / 16))

        # return the positive or negative temperature.
        temp_celsius = temp if neg_sign == False else 256 - temp
        return temp_celsius

if __name__ == '__main__':
    i2c_bus =  I2C(1, sda=Pin(14), scl=Pin(15), freq=100_000)
    tsense =  MCP9808(name="temp Sensor", address=0x18, i2c_bus=i2c_bus)
    devices = tsense.i2c_bus.scan()
    hex_addr = [hex(x) for x in devices]
    print(f"Seen device addresses: {hex_addr}")

# -----------------------------------------
#              END OF FILE
# -----------------------------------------