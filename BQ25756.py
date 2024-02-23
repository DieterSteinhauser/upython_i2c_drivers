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

    def __init__(self, name:str, address:int, i2c_bus, description:str = 'None', width = 16, endian = 'little', *args, **kwargs) -> None:
        """Object initialization for BQ25756. Follow device initialization and adds register information to object"""
        super().__init__(name, address, i2c_bus, description, width, endian, *args, **kwargs)

        # Add device registers
        self.add_register("CHARGE_VOLT_LIMIT", 0x00, r_w = "R/W", description='Charge Voltage limit register.')
        self.add_register("CHARGE_CURR_LIMIT", 0x02, r_w = "R/W", description='Charge Current limit register.')
        self.add_register("INPUT_CURR_LIMIT", 0x06, r_w = "R/W", description='Input Current limit register.')
        self.add_register("INPUT_VOLT_LIMIT", 0x08, r_w = "R/W", description='Input Voltage limit register.')
        self.add_register("REV_MODE_IN_CURR", 0x0A, r_w = "R/W", description='Reverse Mode Input Current Limit register.')
        self.add_register("REV_MODE_IN_VOLT", 0x0C, r_w = "R/W", description='Reverse Mode Input Voltage Limit register.')
        self.add_register("PRECHG_CURR_LIMIT", 0x10, r_w = "R/W", description='Precharge Current limit register.')
        self.add_register("TERM_CURR_LIMIT", 0x12, r_w = "R/W", description='Termination Current limit register.')
        self.add_register("PRECHG_TERM_CTRL", 0x14, r_w = "R/W", description='Precharge and Termination Control register.')
        self.add_register("TIMER_CTRL", 0x15, r_w = "R/W", description='Timer Control register.')
        self.add_register("THREE_STAGE_CHARGE_CTRL", 0x16, r_w = "R/W", description='Three-Stage Charge Control register.')
        self.add_register("CHARGER_CTRL", 0x17, r_w = "R/W", description='Charger Control register.')
        self.add_register("PIN_CTRL", 0x18, r_w = "R/W", description='Pin Control register.')
        self.add_register("PWR_PATH_CTRL", 0x19, r_w = "R/W", description='Power Path and Reverse Mode Control register.')
        self.add_register("MPPT_CTRL", 0x1A, r_w = "R/W", description='MPPT Control register.')
        self.add_register("TS_CHARGE_THRESH_CTRL", 0x1B, r_w = "R/W", description='TS Charging Threshold Control register.')
        self.add_register("TS_CHARGE_REGION_CTRL", 0x1C, r_w = "R/W", description='TS Charging Region Behavior Control register.')
        self.add_register("TS_CHARGE_MODE_CTRL", 0x1D, r_w = "R/W", description='TS Charging Threshold Mode Control register.')
        self.add_register("REV_UNDERVOLTAGE_CTRL", 0x1E, r_w = "R/W", description='Reverse Undervoltage Control register.')
        self.add_register("VAC_MPP_DETECT", 0x1F, r_w = "R/W", description='VAC Max Power Point Detected register.')
        self.add_register("CHARGER_STATUS_1", 0x21, r_w = "R/W", description='Charger Status 1 register.')
        self.add_register("CHARGER_STATUS_2", 0x22, r_w = "R/W", description='Charger Status 2 register.')
        self.add_register("CHARGER_STATUS_3", 0x23, r_w = "R/W", description='Charger Status 3 register.')
        self.add_register("FAULT_STATUS", 0x24, r_w = "R/W", description='Fault Status register.')
        self.add_register("CHARGER_FLAG_1", 0x25, r_w = "R/W", description='Charger Flag 1 register.')
        self.add_register("CHARGER_FLAG_2", 0x26, r_w = "R/W", description='Charger Flag 2 register.')
        self.add_register("FAULT_FLAG", 0x27, r_w = "R/W", description='Fault Flag register.')
        self.add_register("CHARGER_MASK_1", 0x28, r_w = "R/W", description='Charger Mask 1 register.')
        self.add_register("CHARGER_MASK_2", 0x29, r_w = "R/W", description='Charger Mask 2 register.')
        self.add_register("FAULT_MASK", 0x2A, r_w = "R/W", description='Fault Mask register.')
        self.add_register("ADC_CTRL", 0x2B, r_w = "R/W", description='ADC Control register.')
        self.add_register("ADC_CHAN_CTRL", 0x2C, r_w = "R/W", description='ADC Channel Control register.')
        self.add_register("IAC_ADC", 0x2D, r_w = "R/W", description='IAC ADC register.')
        self.add_register("IBAT_ADC", 0x2F, r_w = "R/W", description='IBAT ADC register.')
        self.add_register("VAC_ADC", 0x31, r_w = "R/W", description='VAC ADC register.')
        self.add_register("VBAT_ADC", 0x32, r_w = "R/W", description='VBAT ADC register.')
        self.add_register("TS_ADC", 0x37, r_w = "R/W", description='TS ADC register.')
        self.add_register("VFB_ADC", 0x39, r_w = "R/W", description='VFB ADC register.')
        self.add_register("GD_STR_CTRL", 0x3B, r_w = "R/W", description='Gate Driver Strength Control register.')
        self.add_register("GD_DT_CTRL", 0x3C, r_w = "R/W", description='Gate Driver Dead Time Control register.')
        self.add_register("PART_INFO", 0x3D, r_w = "R/W", description='Part Information register.')
        self.add_register("REV_BAT_DISCH_CURR", 0x62, r_w = "R/W", description='Reverse Mode Battery Discharge Current register.')

        # Add fields to each register
        self.CHARGE_VOLT_LIMIT.add_field(name='VFB_REG', bit_offset=0, width=5, r_w="R/W", description="FB Voltage Regulation Limit")
        self.CHARGE_CURR_LIMIT.add_field(name='ICHG_REG', bit_offset=2, width=9, r_w="R/W", description="Fast Charge Current Regulation Limit")
        self.INPUT_CURR_LIMIT.add_field(name='IAC_DPM', bit_offset=2, width=9, r_w="R/W", description="FB Voltage Regulation Limit")
        self.INPUT_VOLT_LIMIT.add_field(name='VAC_DPM', bit_offset=2, width=12, r_w="R/W", description="FB Voltage Regulation Limit")
        self.PRECHG_CURR_LIMIT.add_field(name='PRECHG_REG', bit_offset=2, width=8, r_w="R/W", description="Precharge Current Regulation Limit")
        self.TERM_CURR_LIMIT.add_field(name='ITERM_REG', bit_offset=2, width=8, r_w="R/W", description="Termination Current Regulation Limit")


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


    def current_limit(self, current_mA= None):
        """
        Command or Query the charge current limit of the device. current given in milliamps.

        if no value is given, return the current limit from the device.

        :param voltage: Charge current limit in mA.
        :type voltage: int
        """

        if current_mA is None:
            
            # read from the device
            bit_value = self.CHARGE_CURR_LIMIT.ICHG_REG.read()

            # format for the user in a similar fashion to the input.
            current_mA = (bit_value * 50)

            return current_mA

        # Throw errors for incorrect values given
        check_type(current_mA, 'current_mA', (int))
        check_range(current_mA, 'current_mA', 400, 20000)

        # remove 50 mA step to produce bit value.
        bit_value = int(current_mA / 50)

        # Write to the register
        self.CHARGE_CURR_LIMIT.ICHG_REG.write(bit_value)


    def input_voltage_limit(self, in_voltage_mv= None):
        """
        Command or Query the input voltage limit of the device. Voltage given in millivolts.

        if no value is given, return the current input voltage limit from the device.

        :param voltage: Input voltage limit in mV.
        :type voltage: int
        """

        if in_voltage_mv is None:
            
            # read from the device
            bit_value = self.INPUT_VOLT_LIMIT.VAC_DPM.read()

            # format for the user in a similar fashion to the input.
            in_voltage_mv = (bit_value * 20)

            return in_voltage_mv

        # Throw errors for incorrect values given
        check_type(in_voltage_mv, 'in_voltage_mv', (int))
        check_range(in_voltage_mv, 'in_voltage_mv', 4200, 65000)

        # remove 20mV step to produce bit value.
        bit_value = int(in_voltage_mv / 20)

        # Write to the register
        self.INPUT_VOLT_LIMIT.VAC_DPM.write(bit_value)
    

    def input_current_limit(self, in_current_mA= None):
        """
        Command or Query the input current limit of the device. current given in milliamps.

        if no value is given, return the input current limit from the device.

        :param voltage: input current limit in mA.
        :type voltage: int
        """

        if in_current_mA is None:
            
            # read from the device
            bit_value = self.INPUT_CURR_LIMIT.IAC_DPM.read()

            # format for the user in a similar fashion to the input.
            in_current_mA = (bit_value * 50)

            return in_current_mA

        # Throw errors for incorrect values given
        check_type(in_current_mA, 'in_current_mA', (int))
        check_range(in_current_mA, 'in_current_mA', 400, 20000)

        # remove 50 mA step to produce bit value.
        bit_value = int(in_current_mA / 50)

        # Write to the register
        self.INPUT_CURR_LIMIT.IAC_DPM.write(bit_value)
    

    def precharge_current_limit(self, pre_current_mA= None):
        """
        Command or Query the precharge current limit of the device. current given in milliamps.

        if no value is given, return the precharge current limit from the device.

        :param voltage: precharge current limit in mA.
        :type voltage: int
        """

        if pre_current_mA is None:
            
            # read from the device
            bit_value = self.PRECHG_CURR_LIMIT.PRECHG_REG.read()

            # format for the user in a similar fashion to the input.
            pre_current_mA = (bit_value * 50)

            return pre_current_mA

        # Throw errors for incorrect values given
        check_type(pre_current_mA, 'pre_current_mA', (int))
        check_range(pre_current_mA, 'pre_current_mA', 250, 10000)

        # remove 50 mA step to produce bit value.
        bit_value = int(pre_current_mA / 50)

        # Write to the register
        self.PRECHG_CURR_LIMIT.PRECHG_REG.write(bit_value)
    

    def termination_current_limit(self, term_current_mA= None):
        """
        Command or Query the termination current limit of the device. current given in milliamps.

        if no value is given, return the termination current limit from the device.

        :param voltage: termination current limit in mA.
        :type voltage: int
        """

        if term_current_mA is None:
            
            # read from the device
            bit_value = self.TERM_CURR_LIMIT.ITERM_REG.read()

            # format for the user in a similar fashion to the input.
            term_current_mA = (bit_value * 50)

            return term_current_mA

        # Throw errors for incorrect values given
        check_type(term_current_mA, 'term_current_mA', (int))
        check_range(term_current_mA, 'term_current_mA', 250, 10000)

        # remove 50 mA step to produce bit value.
        bit_value = int(term_current_mA / 50)

        # Write to the register
        self.TERM_CURR_LIMIT.ITERM_REG.write(bit_value)


# if __name__ == '__main__':

#     i2c_bus =  I2C(0, sda=Pin(12), scl=Pin(13), freq=100_000)

#     bq =  BQ25756(name="BQ25756", address=0x6B, i2c_bus=i2c_bus)
#     devices = bq.i2c_bus.scan()
#     hex_addr = [hex(x) for x in devices]
#     print(f"Seen device addresses: {hex_addr}")


    # bq.VOLT_LIMIT.VFB_REG.write()

# -----------------------------------------
#              END OF FILE
# -----------------------------------------