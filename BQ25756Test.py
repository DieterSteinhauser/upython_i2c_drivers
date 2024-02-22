# -----------------------------------------
#                 NOTES 
# -----------------------------------------
"""
Trevor Free
2/2024
BQ25756 I2C Test Script

"""

# -----------------------------------------
#               IMPORTS
# -----------------------------------------

from machine import Pin, I2C
import time
from i2c_device import Device
from helpers import *
from BQ25756 import BQ25756

# -----------------------------------------
#               MAIN
# -----------------------------------------

i2c_bus =  I2C(1, sda=Pin(36), scl=Pin(39), freq=1_000_000)

