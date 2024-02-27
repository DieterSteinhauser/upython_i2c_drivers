# -----------------------------------------
#                 NOTES 
# -----------------------------------------
"""
Trevor Free and Yiwei Bian
2/2024
BQ25756 I2C Main Script

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

i2c_bus =  I2C(1, sda=Pin(26), scl=Pin(25), freq=100_000)

if __name__ == '__main__':
     bq =  BQ25756(name="BQ_Board", address=0x6B, i2c_bus=i2c_bus)
     #devices = bq.i2c_bus.scan()
     #hex_addr = [hex(x) for x in devices]
     #print(f"Seen device addresses: {hex_addr}")

     programming = True
     if programming:

          #Charging Voltage Setting
          print("")  
          print("Reading and Writing the Charging Voltage")
          print("----------------------------------")

          print("")
          print((bq.voltage_limit()))
          time.sleep(0.1)
            
          print("")
          bq.voltage_limit(1504)
          print('setting reference voltage')
          time.sleep(0.1)
            
          print("")
          print((bq.voltage_limit()))
          time.sleep(0.1)
        
          #Charge Current Setting
          print("")  
          print("Reading and Writing the Charging Current")
          print("----------------------------------")

          print("")
          print((bq.current_limit()))
          time.sleep(0.1)
            
          print("")
          bq.current_limit(2000)
          print('setting reference current')
          time.sleep(0.1)
        
          print("")
          print((bq.current_limit()))
          time.sleep(0.1)
        
          #Input Voltage Setting
          print("")  
          print("Reading and Writing the Input Voltage Limit")
          print("----------------------------------")

          print("")
          print((bq.input_voltage_limit()))
          time.sleep(0.1)
            
          print("")
          bq.input_voltage_limit(20000)
          print('setting input voltage')
          time.sleep(0.1)
        
          print("")
          print((bq.input_voltage_limit()))
          time.sleep(0.1)

          #Input Current Setting
          print("")  
          print("Reading and Writing the Input Current Limit")
          print("----------------------------------")

          print("")
          print((bq.input_current_limit()))
          time.sleep(0.1)
            
          print("")
          bq.input_current_limit(2500)
          print('setting input current')
          time.sleep(0.1)
        
          print("")
          print((bq.input_current_limit()))
          time.sleep(0.1)

          #Precharge Current Setting
          print("")  
          print("Reading and Writing the Precharge Current Limit")
          print("----------------------------------")

          print("")
          print((bq.precharge_current_limit()))
          time.sleep(0.1)
            
          print("")
          bq.precharge_current_limit(500)
          print('setting precharge current')
          time.sleep(0.1)
        
          print("")
          print((bq.precharge_current_limit()))
          time.sleep(0.1)

          #Termination Current Setting
          print("")  
          print("Reading and Writing the Termination Current Limit")
          print("----------------------------------")

          print("")
          print((bq.termination_current_limit()))
          time.sleep(0.1)
            
          print("")
          bq.termination_current_limit(500)
          print('setting termination current')
          time.sleep(0.1)
        
          print("")
          print((bq.termination_current_limit()))
          time.sleep(0.1)

          print("")
          print((bq.status()))
          time.sleep(0.1)

     

# -----------------------------------------
#              END OF FILE
# -----------------------------------------