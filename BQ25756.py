# -----------------------------------------
#                 NOTES 
# -----------------------------------------
"""
Dieter Steinhauser
11/2023
BQ25756 I2C Driver

"""

# -----------------------------------------
#               IMPORTS
# -----------------------------------------

"""
The BQ25756 is a wide input voltage, switchedmode buck-boost Li-Ion, Li-polymer, or LiFePO4
battery charge controller with bidirectional power flow
support. The device offers high-efficiency battery
charging over a wide voltage range with accurate
charge current and charge voltage regulation,
in addition to automatic charge preconditioning,
termination, and charge status indication


The device uses I2C compatible interface for flexible charging parameter programming and instantaneous device
status reporting. I2C is a bi-directional 2-wire serial interface. Only two open-drain bus lines are required: a
serial data line (SDA), and a serial clock line (SCL). Devices can be considered as controllers or targets when
performing data transfers. A controller is a device which initiates a data transfer on the bus and generates the
clock signals to permit that transfer. At that time, any device addressed is considered a target.
The device operates as a target device with address 0x6B, receiving control inputs from the controller device like
a micro-controller or digital signal processor through the registers defined in the Register Map. Registers read 

outside those defined in the map, return 0xFF. The I2C interface supports standard mode (up to 100 kbits/s), fast
mode (up to 400 kbits/s), and fast mode plus (up to 1 Mbit/s). When the bus is free, both lines are HIGH. The
SDA and SCL pins are open drain and must be connected to the positive supply voltage via a current source or
pull-up resistor

"""

from machine import Pin, I2C
from time import sleep
from i2c_device import Device
from helpers import *
# -----------------------------------------
#                Class:
# -----------------------------------------

class BQ25756(Device):

    I2C_MIN_FREQ = 100_000
    I2C_MAX_FREQ = 1_000_000
    DEFAULT_ADDR = 0x6B

    def __init__(self, name:str, address:int, i2c_bus, description:str = None, *args, **kwargs) -> None:
        """Object initialization for BQ25756. Follow device initialization and adds register information to object"""
        super().__init__(name, address, i2c_bus, description, *args, **kwargs)

        # Add device registers
        self.add_register("CHARGE_VOLT_LIMIT", 0x0, r_w = "R/W", description='Charge Voltage limit register.')
        self.add_register("CHARGE_CURR_LIMIT", 0x0, r_w = "R/W", description='Charge Current limit register.')

        # Add fields to each register
        self.CHARGE_VOLT_LIMIT.add_field(name='VFB_REG', bit_offset=0, width=5, r_w="R/W", description="FB Voltage Regulation Limit")
        self.CHARGE_VOLT_LIMIT.add_field(name='ICHG_REG', bit_offset=2, width=8, r_w="R/W", description="Fast Charge Current Regulation Limit")




    # Example changing the charge voltage limit. 
    def voltage_limit(self, voltage_mv= None):
        """
        Command or Query the charge voltage limit of the device. Voltage given in millivolts.

        if no value is given, return the current voltage limit from the device.

        :param voltage: Charge voltage limit in mV.
        :type voltage: int
        """

        if voltage_mv is None:
            
            # read from the device
            bit_value = self.CHARGE_VOLT_LIMIT.VFB_REG.read()

            # format for the user in a similar fashion to the input.
            voltage_mv = (bit_value * 2) + 1054

            return voltage_mv

        # Throw errors for incorrect values given
        check_type(voltage_mv, 'voltage_mv', (int))
        check_range(voltage_mv, 'voltage_mv', 1504, 1566)

        # remove 1.504V offset and 2mV step to produce bit value.
        bit_value = int((voltage_mv - 1504) / 2)

        # Write to the register
        self.CHARGE_VOLT_LIMIT.VFB_REG.write(bit_value)



if __name__ == '__main__':

    i2c_bus =  I2C(0, sda=Pin(12), scl=Pin(13), freq=100_000)

    bq =  BQ25756(name="BQ25756", address=0x6B, i2c_bus=i2c_bus)
    devices = bq.i2c_bus.scan()
    hex_addr = [hex(x) for x in devices]
    print(f"Seen device addresses: {hex_addr}")


    # bq.VOLT_LIMIT.VFB_REG.write()

# -----------------------------------------
#              END OF FILE
# -----------------------------------------