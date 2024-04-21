# -----------------------------------------
#                 NOTES
# -----------------------------------------
"""
Dieter Steinhauser
4/2024
I2C PCF8754 I/O Expander for HD44780 Dot Matrix LCD Driver
"""

# -----------------------------------------
#               IMPORTS
# -----------------------------------------

from upython_i2c_drivers.i2c_device import Device
from upython_i2c_drivers.helpers import *
import time
import gc
from machine import I2C, Pin

# -----------------------------------------
#            LCD Instantiation
# -----------------------------------------

# # Instantiate the I2C Bus
# i2c_bus =  I2C(1, sda=Pin(14), scl=Pin(15), freq=100_000)

# # Scan the I2C bus for Devices
# devices = i2c_bus.scan()
# hex_addr = [hex(x) for x in devices]
# print(f"Seen device addresses: {hex_addr}")

# lcd = Hd44780(name='2x16 LCD', address=0x27, i2c_bus=i2c_bus, rows=2, columns=16)

# lcd.clear()
# lcd.home()
# lcd.print('Hello World!\n')
# lcd.print('Dieter S.')

# -----------------------------------------
#                 LCD Class:
# -----------------------------------------

desc = 'The HD44780U is a dot-matrix liquid crystal display controller and driver. It is controlled using the PCF8574 8-bit I/O Expander for an I2C bus control.'

class Hd44780(Device):
    """Driver Class for HD44780 Dot Matrix LCD using PCF8574 IO Expander"""

    I2C_MIN_FREQ = 100_000
    I2C_MAX_FREQ = 400_000
    DEFAULT_ADDR = 0x27

    # PCF and LCD pinout
    #     7 | 7       DATA BUS
    #     6 | 6       DATA BUS
    #     5 | 5       DATA BUS
    #     4 | 4       DATA BUS
    #     3 | Backlight transistor (backlight active high)
    #     2 | EN      LCD Enable pin
    #     1 | R/W     Read/Write pin 
    #     0 | RS      Register Select
    
    # PCF8574 pin definitions
    _MASK_RS = 0x01      # P0
    _MASK_RW = 0x02      # P1
    _MASK_EN = 0x04      # P2
    _MASK_BL = 0x08      # P3
    _SHIFT_DATA = 4  # P4-P7

    _LCD_HOME = 0x02             # DB1: return to home position
    _LCD_CLR = 0x01              # DB0: clear display

    _LCD_ENTRY_MODE = 0x04       # DB2: set entry mode
    _LCD_ENTRY_INC = 0x02        # --DB1: increment
    _LCD_ENTRY_SHIFT = 0x01      # --DB0: shift

    _LCD_ON_CTRL = 0x08          # DB3: turn lcd/cursor on
    _LCD_ON_DISPLAY = 0x04       # --DB2: turn display on
    _LCD_ON_CURSOR = 0x02        # --DB1: turn cursor on
    _LCD_ON_BLINK = 0x01         # --DB0: blinking cursor

    _LCD_MOVE = 0x10             # DB4: move cursor/display
    _LCD_MOVE_DISP = 0x08        # --DB3: move display (0-> move cursor)
    _LCD_MOVE_RIGHT = 0x04       # --DB2: move right (0-> left)

    _LCD_FUNCTION = 0x20         # DB5: function set
    _LCD_FUNCTION_8BIT = 0x10    # --DB4: set 8BIT mode (0->4BIT mode)
    _LCD_FUNCTION_2LINES = 0x08  # --DB3: two lines (0->one line)
    _LCD_FUNCTION_10DOTS = 0x04  # --DB2: 5x10 font (0->5x7 font)
    _LCD_FUNCTION_RESET = 0x30   # See "Initializing by Instruction" section

    _LCD_CGRAM = 0x40            # DB6: set CG RAM address
    _LCD_DDRAM = 0x80            # DB7: set DD RAM address

    DEG_SYMBOL = chr(223) # Degree symbol for LCD

    def __init__(self, name:str, address:int, i2c_bus, rows:int=2, columns:int=16, description = None, *args, **kwargs) -> None:
        """Object initialization for HD44780 Dot Matrix LCD using PCF8574 IO Expander"""

        # Assign the description
        description = desc if desc is None else description

        # Call the I2C Device initializatiom
        super().__init__(name, address, i2c_bus, description, *args, **kwargs)

        # check for errors
        check_type(rows, 'rows', int)
        check_range(rows, 'rows', 1, 4)
        check_type(columns, 'columns', int)
        check_range(columns, 'columns', 8, 40)

        # assign variables
        self.rows = rows
        self.columns = columns
        self._x = 0
        self._y = 0
        self._backlight = 1

        # initialize the LCD directly
        self._lcd_init()
        self._write_cmd(self._LCD_FUNCTION | self._LCD_FUNCTION_2LINES if rows > 1 else self._LCD_FUNCTION)

        # pickup the trash
        gc.collect()

    # -----------------------------------------
    # Helper functions
    # -----------------------------------------

    _upper = lambda self, nibble: ((nibble >> self._SHIFT_DATA) & 0x0F) << self._SHIFT_DATA # helper function to format upper nibble
    _lower = lambda self, nibble: ((nibble) & 0x0F) << self._SHIFT_DATA                     # helper function to format lower nibble

    def _lcd_init(self):
        """Helper function for the initialization sequence of the LCD"""
        # initial wipe of PCF data bus and controls
        self.write(0)

        # Allow LCD time to powerup
        time.sleep_ms(20)   

        # Send reset 3 times over data bus while flashing the enable.
        self._strobe_data(self._upper(self._LCD_FUNCTION_RESET))
        time.sleep_ms(5) # Need to delay at least 4.1 msec
        self._strobe_data(self._upper(self._LCD_FUNCTION_RESET))
        self._strobe_data(self._upper(self._LCD_FUNCTION_RESET))

        # Put LCD into 4-bit 
        self._strobe_data(self._upper(self._LCD_FUNCTION))

        # startup sequence
        self.clear()
        self.home()
        self._write_cmd(self._LCD_ENTRY_MODE | self._LCD_ENTRY_INC)
        self.cursor_off()
        self.backlight(1)

    def _write_cmd(self, cmd):
        """
        Helper function to send values to the LCD command register

        :param data: full byte of data to be sent to the LCD
        :type data: int
        """
        self._strobe_data((self.backlight() << 3) | self._upper(cmd)) # type: ignore
        self._strobe_data((self.backlight() << 3) | self._lower(cmd)) # type: ignore

    def _write_data(self, data):
        """
        Helper function to send values to the LCD data register

        :param data: full byte of data to be sent to the LCD
        :type data: int
        """
        self._strobe_data(self._MASK_RS | (self.backlight() << 3) | self._upper(data)) # type: ignore
        self._strobe_data(self._MASK_RS | (self.backlight() << 3) | self._lower(data)) # type: ignore
    
    def _strobe_data(self, data):
        """
        Send Data via I2C to the LCD by flashing the enable pin.

        :param data: Data to be sent to the LCD
        :type data: int
        """
        # Set the enable high with the data
        self.write(data | self._MASK_EN, read_check=False)
        time.sleep_ms(1)

        # set the enable low with the data
        self.write(data, read_check=False)
        time.sleep_ms(1)
        gc.collect()

    def _fast_putch(self, char):
        """Write a character on to the LCD. No newline support"""

        # Write to the LCD and advance the column.
        self._write_data(ord(char))
        self._x += 1

        # if we have hit the end or the row, advance to the next row.
        if self._x >= self.columns:
            self._x = 0
            self._y += 1

        # if we have hit the end of our rows, reset to the beginning.
        self._y = 0 if self._y >= self.rows else self._y

    def _putch(self, char):
        """Write a character on to the LCD."""

        # Write to the LCD and advance the column.
        if char != '\n':
            self._write_data(ord(char))
            self._x += 1

        # if the character is a newline, advance to the next row.
        else:
            self._x = self.columns

        # if we have hit the end or the row, advance to the next row.
        if self._x >= self.columns:
            self._x = 0
            self._y += 1

        # if we have hit the end of our rows, reset to the beginning.
        if self._y >= self.rows:
            self._y = 0
        
        # provide movement to the LCD
        self.move_to(self._x, self._y)

    # -----------------------------------------
    # LCD Commands
    # -----------------------------------------

    def clear(self):
            """Clear the LCD Screen."""
            self._write_cmd(self._LCD_CLR)
            time.sleep_ms(5)

    # -----------------------------------------

    def home(self):
        """Return the Cursor to the starting position."""
        self._write_cmd(self._LCD_HOME)
        time.sleep_ms(5)
        self._x = 0
        self._y = 0

    # -----------------------------------------

    def print(self, string):
        """Write a string on to the LCD."""

        for element in string:
            self._putch(element)

    # -----------------------------------------

    def fast_print(self, string):
        """Write a string on to the LCD. Faster but lacks Newline support"""

        for element in string:
            self._fast_putch(element)
               
    # -----------------------------------------

    def cursor_on(self):
        """Turns on the cursor, Good for debugging."""
        self._write_cmd(self._LCD_ON_CTRL | self._LCD_ON_DISPLAY | self._LCD_ON_CURSOR)

    # -----------------------------------------

    def cursor_off(self):
        """Turns off the cursor."""
        self._write_cmd(self._LCD_ON_CTRL | self._LCD_ON_DISPLAY)

    # -----------------------------------------

    def blink_on(self):
        """Turns on the cursor, and makes it blink."""
        self._write_cmd(self._LCD_ON_CTRL | self._LCD_ON_DISPLAY | self._LCD_ON_CURSOR | self._LCD_ON_BLINK)

    # -----------------------------------------

    def blink_off(self):
        """Turns on the cursor, and makes it solid."""
        self.cursor_on()

    # -----------------------------------------

    def display_on(self):
        """Turns on (i.e. unblanks) the LCD."""
        self._write_cmd(self._LCD_ON_CTRL | self._LCD_ON_DISPLAY)

    # -----------------------------------------

    def display_off(self):
        """Turns off (i.e. blanks) the LCD."""
        self._write_cmd(self._LCD_ON_CTRL)

    # -----------------------------------------

    def backlight(self, status=None):
        """
        Command or query the status of the backlight on the device.

        :param status: Sets the status of the backlight with 0 off and 1 on. Defaults to None
        :type status: int, optional
        :return: if no status value is entered, returns the current state of the backlight.
        :rtype: int
        """

        # if nothing was passed in, read back the current backlight setting.
        if status is None:
            return self._backlight

        # check for errors
        check_type(status, 'status', int)
        check_range(status, 'status', 0, 1)

        # write to the device
        self._backlight = status
        self.write((status << 3), read_check=False)
        gc.collect()

    # ----------------------------------------- 

    def move_to(self, x, y):
        """Moves the cursor position to the indicated position. The cursor
        position is zero based (i.e. cursor_x == 0 indicates first column).
        """
        # save the movement to memory
        self._x = x
        self._y = y
        addr = x & 0x3F

        # Lines 1 & 3 add 0x40
        if y & 1:
            addr += 0x40    

        # Lines 2 & 3 add number of columns
        if y & 2:    
            addr += self.columns

        self._write_cmd(self._LCD_DDRAM | addr)

    # -----------------------------------------

    def custom_char(self, location, charmap):
        """Write a character to one of the 8 CGRAM locations, available
        as chr(0) through chr(7).
        """
        # indicate that we are writing to a CGRAM location
        self._write_cmd(self._LCD_CGRAM | ((location & 0x7) << 3))
        time.sleep_us(40)

        # Write the custom character map to the LCD
        for i in range(8):
            self._write_data(charmap[i])
            time.sleep_us(40)
        
        self.move_to(self._x, self._y)

    # -----------------------------------------

    def newline(self):
        """Move the cursor to the start of a new line."""

        # carriage return
        self._x = 0

        # line feed
        self._y += 1

        # if we have hit the end of our rows, reset to the beginning.
        if self._y >= self.rows:
            self._y = 0
        
        # provide movement to the LCD
        self.move_to(self._x, self._y)

    # -----------------------------------------

    def carriage_return(self):
        """Return the Cursor to the start of the existing line"""

        # carriage return
        self._x = 0

        # provide movement to the LCD
        self.move_to(self._x, self._y)

    # -----------------------------------------

    def line_feed(self):
        """Move the cursor down one row. Column remains the same."""

        # line feed
        self._y += 1

        # if we have hit the end of our rows, reset to the beginning.
        if self._y >= self.rows:
            self._y = 0
        
        # provide movement to the LCD
        self.move_to(self._x, self._y)


if __name__ == '__main__':
    
    # Instantiate the I2C Bus
    i2c_bus =  I2C(1, sda=Pin(14), scl=Pin(15), freq=100_000)

    # Scan the I2C bus for Devices
    devices = i2c_bus.scan()
    hex_addr = [hex(x) for x in devices]
    print(f"Seen device addresses: {hex_addr}")

    lcd = Hd44780(name='2x16 LCD', address=0x27, i2c_bus=i2c_bus, rows=2, columns=16)

    lcd.print('Hello World!\n')
    lcd.print('Dieter S.')


# -----------------------------------------
#              END OF FILE
# -----------------------------------------