#!/usr/bin/python
# -- LCD_Socket: lcd_display.py --

import RPi.GPIO as GPIO
from RPLCD import CharLCD

from time import sleep


class LCD_Display:
    def __init__(self, size : dict, pin_e : int, pin_rs : int, pins_data : list) -> None:
        self.size = size
        self.pin_e = pin_e
        self.pin_rs = pin_rs
        self.pins_data = pins_data
        
        self.rows_text = []
        for i in range(self.size['rows']):
            self.rows_text.append('')
        
        self.__gpio_init()
        
        self.__display_init_show()
        
        self.display.clear()
        
        
    def __gpio_init(self):
        num_mode = GPIO.BCM
        
        GPIO.setwarnings(False)
        GPIO.setmode(num_mode)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        GPIO.setup(self.pin_e,  GPIO.OUT)

        for pin in self.pins_data:
            GPIO.setup(pin, GPIO.OUT)

        self.display = CharLCD(cols=self.size['cols'],
                      rows=self.size['rows'],
                      pin_rs=self.pin_rs,
                      pin_e=self.pin_e,
                      pins_data=self.pins_data,
                      numbering_mode=num_mode,
                      backlight_enabled=False)
        
        GPIO.setwarnings(True)
        
        
    def __display_init_show(self):
        self.display.clear()
        
        text = '-- LCD READY --'.center(self.size['cols'])
        
        self.write(row=0, text=text)
        
        sleep(3)
        
        
    def write(self, row : int, text : str):
        self.rows_text[row] = text
        
        self.display.clear()
        
        for i, row_text in enumerate(self.rows_text):
            self.display.cursor_pos = (i, 0)
            self.display.write_string(row_text)
