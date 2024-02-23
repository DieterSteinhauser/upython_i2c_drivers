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

if __name__ == '__main__':
     bq =  BQ25756(name="BQ_Board", address=0x6B, i2c_bus=i2c_bus)
     devices = bq.i2c_bus.scan()
     hex_addr = [hex(x) for x in devices]
     print(f"Seen device addresses: {hex_addr}")

     test_reading = True
     if test_reading:
          print("Testing reading of each register")
          print("----------------------------------")

          print(bin(bq.CHARGE_VOLT_LIMIT.read()))
          print(bin(bq.CHARGE_CURR_LIMIT.read()))
          print(bin(bq.INPUT_CURR_LIMIT.read()))
          print(bin(bq.INPUT_VOLT_LIMIT.read()))
          print(bin(bq.PRECHG_CURR_LIMIT.read()))
          print(bin(bq.TERM_CURR_LIMIT.read()))
          print("")

          print("Testing the reading of each field")
          print("----------------------------------")

          print(bin(bq.CHARGE_VOLT_LIMIT.VFB_REG.read()))
          print("")
          print(bin(bq.CHARGE_CURR_LIMIT.ICHG_REG.read()))
          print("")
          print(bin(bq.INPUT_CURR_LIMIT.IAC_DPM.read()))
          print("")
          print(bin(bq.INPUT_VOLT_LIMIT.VAC_DPM.read()))
          print("")
          print(bin(bq.PRECHG_CURR_LIMIT.PRECHG_REG.read()))
          print("")
          print(bin(bq.TERM_CURR_LIMIT.ITERM_REG.read()))
          print("")
          print(bin(bq.STATUS.read()))

          print("")  
          print("Reading and Writing the Reference Voltage")
          print("----------------------------------")

          print("")
          print((bq.voltage_limit()))
          time.sleep(0.1)
            
          print("")
          bq.voltage_limit(1510)
          print('setting reference voltage')
          time.sleep(0.1)
        
            
          print("")
          print((bq.voltage_limit()))
          time.sleep(0.1)
        
          bq.voltage_limit(1550)
          time.sleep(0.1)
        
          print("")
          print((bq.voltage_limit()))
          time.sleep(0.1)
        
          print("")
          print((bq.status()))
          time.sleep(0.1)

     # test_output = True
     # if test_output:
        
     #      # 5V input
     #      bq.input_voltage_limit(5000)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)
        
     #      print("")
     #      print((bq.input_voltage_limit()))
     #      time.sleep(0.1)
        

     #    #   print("")  
     #    #   print("Enabling the Output")
     #    #   bq.output_enable(value=1)
     #    #   print(bq.output_enable())
          
        
     #      # 20V output
     #      bq.input_voltage_limit(20000)
     #      time.sleep(0.1)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)
        
     #      # 19V output
     #      bq.input_voltage_limit(19000)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)
        
     #      # 11.9V output
     #      bq.input_voltage_limit(11900)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)
        
     #      # 9V output
     #      bq.input_voltage_limit(9000)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)

     #      # 5V output
     #      bq.input_voltage_limit(5000)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)

     #      # 33V output
     #      bq.input_voltage_limit(33000)
     #      print((bq.input_voltage_limit()))
     #      time.sleep(1)
        
        #   time.sleep(5)
        #   bq.output_enable(value=0)
        #   print(bq.output_enable())

# -----------------------------------------
#              END OF FILE
# -----------------------------------------