# -----------------------------------------
#                 NOTES
# -----------------------------------------
"""
Dieter Steinhauser
4/2024
I2C HD44780 Dot Matrix LCD Driver
"""

# -----------------------------------------
#               IMPORTS
# -----------------------------------------

from machine import Pin
import utime
from i2c_device import Device, Register, Field
from helpers import *

# -----------------------------------------
#            LCD Instantiation
# -----------------------------------------

# add this code to the beginning of your main file to instantiate the LCD

# init I2C object using Class, at channel 0, data-GP00, clock-GP01, comm at 400kHz
# i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# return address of I2C at channel 0 (the i2c we just made)
# I2C_ADDR = i2c.scan()[0]

# init lcd object using I2cLcd library, protocol-i2c, at I2C addr returned above, 2X16 Char LCD
# lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)


# GPIO 
# lcd = LCD(enable_pin=0,           # Enable Pin, int
         # reg_select_pin=1,        # Register Select, int
         # data_pins=[2, 3, 4, 5]   # Data Pin numbers for the upper nibble. list[int]
         # )

# lcd.init()
# lcd.clear()
# lcd.cursor_on()
# lcd.blink()


# -----------------------------------------
#                 LCD Class:
# -----------------------------------------


class LCD:
    """The LCD class is meant to abstract the LCD driver further and streamline development."""


    def __init__(self, enable_pin: int, reg_select_pin: int, data_pins: list) -> None:
        """Object initialization"""

        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.reg_select_pin = Pin(reg_select_pin, Pin.OUT)
        self._data_pins = data_pins
        self.data_bus = []

        # Configure the pins of the device.
        self._configure()
        utime.sleep_ms(120)

    # -----------------------------------------

    def _configure(self):
        """Creates the data bus object from the pin list. """

        # Configure the pins of the device.
        for element in self._data_pins:
            self.data_bus.append(Pin(element, Pin.OUT))

    # -----------------------------------------

    def init(self):
        """Initializes the LCD for communication."""

        # clear values on data bus.
        for index in range(4):
            self.data_bus[index].value(0)
        utime.sleep_ms(50)

        # initialization sequence.
        self.data_bus[0].value(1)
        self.data_bus[1].value(1)
        self.strobe()
        utime.sleep_ms(10)

        self.strobe()
        utime.sleep_ms(10)

        self.strobe()
        utime.sleep_ms(10)

        self.data_bus[0].value(0)
        self.strobe()
        utime.sleep_ms(5)

        self.write(0x28, 0)
        utime.sleep_ms(1)

        self.write(0x08, 0)
        utime.sleep_ms(1)

        self.write(0x01, 0)
        utime.sleep_ms(10)

        self.write(0x06, 0)
        utime.sleep_ms(5)

        self.write(0x0C, 0)
        utime.sleep_ms(10)

    # -----------------------------------------

    def strobe(self):
        """Flashes the enable line and provides wait period."""

        self.enable_pin.value(1)
        utime.sleep_ms(1)

        self.enable_pin.value(0)
        utime.sleep_ms(1)

    # -----------------------------------------

    def write(self, command, mode):
        """Sends data to the LCD module. """

        # determine if writing a command or data
        data = command if mode == 0 else ord(command)

        # need upper nibble for first loop. lower nibble can use data directly.
        upper = data >> 4

        # write the upper nibble
        for index in range(4):
            bit = upper & 1
            self.data_bus[index].value(bit)
            upper = upper >> 1

        # strobe the LCD, sending the nibble
        self.reg_select_pin.value(mode)
        self.strobe()

        # write the lower nibble
        for index in range(4):
            bit = data & 1
            self.data_bus[index].value(bit)
            data = data >> 1

        # Strobe the LCD, sending the nibble
        self.reg_select_pin.value(mode)
        self.strobe()
        utime.sleep_ms(1)
        self.reg_select_pin.value(1)

    # -----------------------------------------

    def clear(self):
        """Clear the LCD Screen."""

        self.write(0x01, 0)
        utime.sleep_ms(5)

    # -----------------------------------------

    def home(self):
        """Return the Cursor to the starting position."""

        self.write(0x02, 0)
        utime.sleep_ms(5)

    # -----------------------------------------


    def blink(self):
        """Have the cursor start blinking."""

        self.write(0x0D, 0)
        utime.sleep_ms(1)

    # -----------------------------------------

    def cursor_on(self):
        """Have the cursor on, Good for debugging."""

        self.write(0x0E, 0)
        utime.sleep_ms(1)

    # -----------------------------------------

    def cursor_off(self):
        """Turn the cursor off."""

        self.write(0x0C, 0)
        utime.sleep_ms(1)

    # -----------------------------------------

    def print(self, string):
        """Write a string on to the LCD."""

        for element in string:
            self._putch(element)

    # -----------------------------------------

    def _putch(self, c):
        """Write a character on to the LCD."""
        self.write(c, 1)

    # -----------------------------------------

    def _puts(self, string):
        """Write a string on to the LCD."""

        for element in string:
            self._putch(element)


    # -----------------------------------------
    def go_to(self, column, row):


        if row == 0:
            address = 0

        if row == 1:
            address = 0x40

        if row == 2:
            address = 0x14

        if row == 3:
            address = 0x54

        address = address + column
        self.write(0x80 | address, 0)


# -----------------------------------------
#              END OF FILE
# -----------------------------------------

import utime
import gc
from machine import I2C

desc = ''

class pcf8574_lcd(Device):
    """PCF8574 IO Expander for HD44780 Dot Matrix LCD Driver Class"""

    
    I2C_MIN_FREQ = 100_000
    I2C_MAX_FREQ = 100_000
#   DEFAULT_ADDR = 0x74
#   ALT_ADDR = 0x75
    
    # PCF8574 pin definitions
    MASK_RS = 0x01       # P0
    MASK_RW = 0x02       # P1
    MASK_EN  = 0x04      # P2

    SHIFT_BACKLIGHT = 3  # P3
    SHIFT_DATA      = 4  # P4-P7

    LCD_CLR = 0x01              # DB0: clear display
    LCD_HOME = 0x02             # DB1: return to home position

    LCD_ENTRY_MODE = 0x04       # DB2: set entry mode
    LCD_ENTRY_INC = 0x02        # --DB1: increment
    LCD_ENTRY_SHIFT = 0x01      # --DB0: shift

    LCD_ON_CTRL = 0x08          # DB3: turn lcd/cursor on
    LCD_ON_DISPLAY = 0x04       # --DB2: turn display on
    LCD_ON_CURSOR = 0x02        # --DB1: turn cursor on
    LCD_ON_BLINK = 0x01         # --DB0: blinking cursor

    LCD_MOVE = 0x10             # DB4: move cursor/display
    LCD_MOVE_DISP = 0x08        # --DB3: move display (0-> move cursor)
    LCD_MOVE_RIGHT = 0x04       # --DB2: move right (0-> left)

    LCD_FUNCTION = 0x20         # DB5: function set
    LCD_FUNCTION_8BIT = 0x10    # --DB4: set 8BIT mode (0->4BIT mode)
    LCD_FUNCTION_2LINES = 0x08  # --DB3: two lines (0->one line)
    LCD_FUNCTION_10DOTS = 0x04  # --DB2: 5x10 font (0->5x7 font)
    LCD_FUNCTION_RESET = 0x30   # See "Initializing by Instruction" section

    LCD_CGRAM = 0x40            # DB6: set CG RAM address
    LCD_DDRAM = 0x80            # DB7: set DD RAM address

    LCD_RS_CMD = 0
    LCD_RS_DATA = 1

    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, name:str, address:int, i2c_bus, rows:int=2, columns:int=16, description = None, *args, **kwargs) -> None:
        """Object initialization for PCF8574 IO Expander for HD44780 Dot Matrix LCD Driver"""
        description = desc if desc is None else description
        super().__init__(name, address, i2c_bus, description, *args, **kwargs)

        self.write(0)
        utime.sleep_ms(20)   # Allow LCD time to powerup
        # Send reset 3 times
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        utime.sleep_ms(5)    # Need to delay at least 4.1 msec
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        # Put LCD into 4-bit mode
        self.hal_write_init_nibble(self.LCD_FUNCTION)

        # TODO Check the range of rows and columns
        self.rows = rows
        if self.rows > 4:
            self.rows = 4
        self.columns = columns
        if self.columns > 40:
            self.columns = 40
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True
        self.display_off()
        self.backlight_on()
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        self.hide_cursor()
        self.display_on()
        cmd = self.LCD_FUNCTION
        if rows > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        gc.collect()

    def hal_write_init_nibble(self, nibble):
        # Writes an initialization nibble to the LCD.
        # This particular function is only used during initialization.
        data = ((nibble >> 4) & 0x0f) << self.SHIFT_DATA
        self.strobe_data(data)
        gc.collect()

    def strobe_data(self, data):
        """
        Send Data via I2C to the LCD by flashing the enable pin.

        :param data: _description_
        :type data: _type_
        """
        # Set the enable high with the data
        self.write(data | self.ENABLE_MASK)
        utime.sleep_ms(1)

        # set the enable low with the data
        self.write(data)
        utime.sleep_ms(1)

        
    def backlight_on(self):
        # Allows the hal layer to turn the backlight on
        # TODO add read for backlight info
        self.backlight = True
        self.write(1 << self.SHIFT_BACKLIGHT)
        gc.collect()
        
    def backlight_off(self):
        #Allows the hal layer to turn the backlight off
        # TODO add read for backlight info
        self.backlight = False
        self.write(0)
        gc.collect()
        
    # TODO add read modify write to get backlight info
    def hal_write_command(self, cmd):
        # Write a command to the LCD. Data is latched on the falling edge of E.
        byte = ((self.backlight << self.SHIFT_BACKLIGHT) |
                (((cmd >> 4) & 0x0f) << SHIFT_DATA))
        
        self.strobe_data(byte)

        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                ((cmd & 0x0f) << SHIFT_DATA))
        
        self.strobe_data(byte)
        gc.collect()


    # TODO add read modify write to get backlight info
    def hal_write_data(self, data):
        # Write data to the LCD. Data is latched on the falling edge of E.
        byte = (self.MASK_RS |
                (self.backlight << self.SHIFT_BACKLIGHT) |
                (((data >> 4) & 0x0f) << self.SHIFT_DATA))
        self.strobe_data(byte)

        byte = (self.MASK_RS |
                (self.backlight << self.SHIFT_BACKLIGHT) |
                ((data & 0x0f) << self.SHIFT_DATA))      
        self.strobe_data(byte)

        gc.collect()

    def clear(self):
            """Clears the LCD display and moves the cursor to the top left
            corner.
            """
            self.hal_write_command(self.LCD_CLR)
            utime.sleep_ms(5) # The home and clear commands require a worst case delay of 4.1 msec
            self.hal_write_command(self.LCD_HOME)
            utime.sleep_ms(5) # The home and clear commands require a worst case delay of 4.1 msec
            self.cursor_x = 0
            self.cursor_y = 0

    def show_cursor(self):
        """Causes the cursor to be made visible."""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def hide_cursor(self):
        """Causes the cursor to be hidden."""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        """Turns on the cursor, and makes it blink."""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR | self.LCD_ON_BLINK)

    def blink_cursor_off(self):
        """Turns on the cursor, and makes it no blink (i.e. be solid)."""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def display_on(self):
        """Turns on (i.e. unblanks) the LCD."""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def display_off(self):
        """Turns off (i.e. blanks) the LCD."""
        self.hal_write_command(self.LCD_ON_CTRL)

    def move_to(self, x, y):
        """Moves the cursor position to the indicated position. The cursor
        position is zero based (i.e. cursor_x == 0 indicates first column).
        """
        self.x = x
        self.y = y
        addr = x & 0x3f
        if y & 1:
            addr += 0x40    # Lines 1 & 3 add 0x40
        if y & 2:    # Lines 2 & 3 add number of columns
            addr += self.columns
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putchar(self, char):
        """Writes the indicated character to the LCD at the current cursor
        position, and advances the cursor by one position.
        """
        if char == '\n':
            if self.implied_newline:
                # self.implied_newline means we advanced due to a wraparound,
                # so if we get a newline right after that we ignore it.
                self.implied_newline = False
            else:
                self.cursor_x = self.columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
        if self.cursor_x >= self.columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = (char != '\n')
        if self.cursor_y >= self.num_lines:
            self.cursor_y = 0
        self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        """Write the indicated string to the LCD at the current cursor
        position and advances the cursor position appropriately.
        """
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        """Write a character to one of the 8 CGRAM locations, available
        as chr(0) through chr(7).
        """
        location &= 0x7
        self.hal_write_command(self.LCD_CGRAM | (location << 3))
        self.hal_sleep_us(40)
        for i in range(8):
            self.hal_write_data(charmap[i])
            self.hal_sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    # This is a default implementation of hal_sleep_us which is suitable
    # for most micropython implementations. For platforms which don't
    # support `time.sleep_us()` they should provide their own implementation
    # of hal_sleep_us in their hal layer and it will be used instead.
    def hal_sleep_us(self, usecs):
        """Sleep for some time (given in microseconds)."""
        time.sleep_us(usecs)  # NOTE this is not part of Standard Python library, specific hal layers will need to override this

    