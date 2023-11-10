# -----------------------------------------
#                 NOTES 
# -----------------------------------------
"""
Dieter Steinhauser
10/2023
I2C Device, Register, and field objects for driver implementation

"""
# -----------------------------------------
#               IMPORTS
# -----------------------------------------


# -----------------------------------------
#               CLASS
# -----------------------------------------

_RW_TYPE = ['R', 'W', 'R/W']
_READ = ['R', 'R/W']
_WRITE = ['W', 'R/W']


# TODO: add support for endian swapping throughout the device
# TODO: add support for 16 bit registers

class Device:

    def __init__(self, name:str, address:int, i2c_bus, description:str = None, endian='big', *args, **kwargs) -> None: 
        """
        Device Creation.

        :param name: Device name.
        :type name: str
        :param address: device i2c address
        :type address: int
        """

        # Check inputs for errors
        if not isinstance(name, str):
            raise ValueError(f" Incorrect type for name: {name}. Input should be a string")
        
        if not isinstance(address, int):
            raise ValueError(f" Incorrect type for address: {address}. Input should be a Int")

        self.name = name
        self.addr = address
        self.description = description
        self.registers= {}
        self.endian = endian

        if i2c_bus is not None:
            self.i2c_bus = i2c_bus
 
    def read(self):
        """
        Read data from the device. 
        
        Primarily used when the I2C device does not employ a memory system or a register set.

        :param register: Register object to read from.
        :type register: Register
        :return: Data read from the register.
        """
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")
        
        read_data = self.i2c_bus.readfrom(self.addr, 1)
        return int.from_bytes(read_data, "big")
            

    def write(self, data):
        """
        Write data to the device.

        Primarily used when the I2C device does not employ a memory system or a register set.

        :param data: Data to write to the device.
        :type data: int
        """
        
        # Write the data to the bus
        self.i2c_bus.writeto(self.addr, bytes([data]))
        
        # Confirm the write by reading and comparing the data
        read_data = self.read()
        if read_data != data:
            raise ValueError(f"Write confirmation failed.\nRead Data: {read_data} \nWritten Data: {data}")


    def add_register(self, name:str, address:int, *args, **kwargs) -> None: # TODO: Add register width
        """
        Register addition to the device.

        :param name: Name of the Register
        :type name: str
        :param address: Address of the Register.
        :type address: int
        :param width: width, should be some power of 2, defaults to 8
        :type width: int, optional
        """

        register = Register(self, name, address, *args, **kwargs)
        self.registers[name] = register
        setattr(self, name, register)

    def reg_read(self, register): # TODO: Add register width and Endian
        """
        Read data from a specific register in the device's memory.

        :param register: Register object to read from.
        :type register: Register
        :return: Data read from the register.
        """
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")
        
        read_data = self.i2c_bus.readfrom_mem(self.addr, register.addr, 1)
        return int.from_bytes(read_data, "big")
            

    def reg_write(self, register, data): # TODO: Add register width and maybe endian?
        """
        Write data to a specific register in the device's memory.

        :param register: Register object to write to.
        :type register: Register
        :param data: Data to write to the register.
        :type data: int
        """
        
        # Write the data to the bus
        self.i2c_bus.writeto_mem(self.addr, register.addr, bytes([data]))
        
        # If possible, confirm that we correctly edited the field.
        if self.register.r_w in _READ:

            # Confirm the write by reading and comparing the data
            read_data = self.reg_read(register)
            if read_data != data:
                raise ValueError(f"Write confirmation failed.\nRead Data: {read_data} \nWritten Data: {data}")





class Register:

    def __init__(self, device, name : str, address : int, width : int = 8, r_w:str = "R/W", description : str = None, *args, **kwargs) -> None:
        """
        Register creation

        :param name: Name of the Register
        :type name: str
        :param address: Address of the Register.
        :type address: int
        :param width: width, should be some power of 2, defaults to 8
        :type width: int, optional
        """
        # Check inputs for errors
        if not isinstance(name, str):
            raise ValueError(f" Incorrect type for name: {name}. Input should be a string")
        
        if not isinstance(address, int):
            raise ValueError(f" Incorrect type for address: {address}. Input should be a Int")

        if not isinstance(width, int):
            raise ValueError(f" Incorrect type for width: {width}. Input should be a Int")

        # check the width of a register is a power of 2
        if width == 0 or width & (width-1) != 0:
            raise ValueError(f" Incorrect value for address: {address}. Input should be a power of 2")

        self.name = name
        self.addr = address
        self.width = width
        self.r_w = r_w
        self.description = description
        self.device = device
        self.fields= {}
        self.i2c_bus = device.i2c_bus

    def add_field(self, name:str, bit_offset:int, *args, **kwargs):
        """
        Field addition to the register.

        :param name: Name of field.
        :type name: str
        :param bit_offset: offset of the bits
        :type bit_offset: int
        :param size: size of the fields bits, defaults to 1
        :type size: _type_, optional
        :param r_w: Read/Write permissions for the field, can be 'R', 'W', 'R/W', defaults to "R/W"
        :type r_w: str, optional
        :param description: description of the field and how it operates, defaults to None
        :type description: str, optional
        """
        field = Field(self, name, bit_offset, *args, **kwargs)
        self.fields[name] = field
        setattr(self, name, field)

    def read(self):
        """
        Read from the register.

        :return: Returns the value of the read register.
        :rtype: int
        """
        # Throw an error if the I2C bus object does not exist.
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")
        
        # Throw an error if not readable.
        if self.r_w not in _READ:
            raise ValueError(f"Error writing to register, Permission is {self.r_w} 'Write Only'.")

        read_byte = self.i2c_bus.readfrom_mem(self.device.addr, self.addr, 1) # TODO: add support for endian swapping and for 16 bit registers
        return int.from_bytes(read_byte, "big")
    
         
    def write(self, value):
        """
        Write data to a register.

        :param value: integer value for the data to be written.
        :type value: int
        """

        # Throw an error if the I2C bus object does not exist.
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")

        # Throw an error if the field cannot be written.
        if self.r_w not in _WRITE:
            raise ValueError(f"Error writing to register, Permission is {self.r_w} 'Read Only'.")

        # Throw an error if the value is larger than the field width
        if value > (2**self.width - 1):
            raise ValueError(f"Error writing to register, Value {value} is too large for register size {self.width}")
        
        # TODO: add support for endian swapping and for 16 bit registers
        # Write the data to the bus
        self.i2c_bus.writeto_mem(self.device.addr, self.addr, bytes([value]))
        
        # If possible, confirm that we correctly edited the field.
        if self.r_w in _READ:

            # Confirm the write by reading and comparing the data
            read_data = self.read()
            if read_data != value:
                raise ValueError(f"Write confirmation failed.\nRead Data: {read_data} \nWritten Data: {value}")



class Field:

    def __init__(self, register, name:str, bit_offset:int, width:int = 1, r_w:str = "R/W", description : str = None, *args, **kwargs) -> None:
        """
        Field creation.

        :param name: Name of field.
        :type name: str
        :param name: Name of field.
        :type name: str
        :param bit_offset: offset of the bits
        :type bit_offset: int
        :param width: Width of the fields bits, defaults to 1
        :type width: _type_, optional
        :param r_w: Read/Write permissions for the field, can be 'R', 'W', 'R/W', defaults to "R/W"
        :type r_w: str, optional
        :param description: description of the field and how it operates, defaults to None
        :type description: str, optional
        """

        # Check inputs for errors
        if not isinstance(name, str):
            raise ValueError(f" Incorrect type for name: {name}. Input should be a string")
        
        if not isinstance(bit_offset, int):
            raise ValueError(f" Incorrect type for bit offset: {bit_offset}. Input should be a Int")
        
        if not isinstance(width, int):
            raise ValueError(f" Incorrect type for size: {width}. Input should be a Int")
        
        if not isinstance(r_w, str) or r_w not in _RW_TYPE:
            raise ValueError(f" Incorrect value for r_w: {r_w}. Input should be in {_RW_TYPE}")
        
        self.name = name
        self.bit_offset = bit_offset
        self.width = width
        self.r_w = r_w
        self.description = description
        self.register = register
        self.device = register.device
        self.i2c_bus = register.i2c_bus
        
    def read(self):
        """
        Read from the field.

        :return: Returns the value of the read field.
        :rtype: int
        """
        # Throw an error if the I2C bus object does not exist.
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")
        
        # Throw an error if not readable.
        if self.r_w not in _READ:
            raise ValueError(f"Error writing to field, Permission is {self.r_w} 'Write Only'.")

        read_byte = self.i2c_bus.readfrom_mem(self.device.addr, self.register.addr, 1) # TODO: add support for endian swapping and for 16 bit registers
        read_data = int.from_bytes(read_byte, "big")
        field =  (read_data >> self.bit_offset) & ((2**self.width) - 1)
        return field
            
    def write(self, value):
        """
        Write data to a field.

        :param value: integer value for the data to be written.
        :type value: int
        """

        # Throw an error if the I2C bus object does not exist.
        if not self.i2c_bus:
            raise ValueError("I2C bus not initialized.")

        # Throw an error if the field cannot be written.
        if self.r_w not in _WRITE:
            raise ValueError(f"Error writing to field, Permission is {self.r_w} 'Read Only'.")

        # Throw an error if the value is larger than the field width
        if value > (2**self.width - 1):
            raise ValueError(f"Error writing to field, Value {value} is too large for field size {self.size}")
        
        # Read the existing register data
        register_data = self.register.read()

        # AND field bits with zero and don't care bits with one to clear field bits
        register_data &= ~(((2**self.width)-1) << self.bit_offset)

        # offset the value desired for the field and OR it with the existing register
        register_data |= (value << self.bit_offset)
        
        # TODO: add support for endian swapping and for 16 bit registers
        # Write the data to the bus
        self.i2c_bus.writeto_mem(self.device.addr, self.register.addr, bytes([int(register_data)]))
        
        
        # Confirm the write by reading and comparing the data
        read_data = self.read()
        if read_data != value:
            raise ValueError(f"Write confirmation failed.\nRead Data: {read_data} \nWritten Data: {value}")
        

# -----------------------------------------
#               END OF FILE
# -----------------------------------------
   
