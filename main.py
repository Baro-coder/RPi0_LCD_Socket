#!/usr/bin/python
# -- LCD_Socket: main.py --

import sys
import configparser as cfgp

from tcp_server import TCP_Server
from lcd_display import LCD_Display

APP_DIR = '/home/pi/.Private/RPi0_LCD_Socket'
CONFIG_FILE = f'{APP_DIR}/config.ini'


def config_init():
    try:
        config = cfgp.ConfigParser()

        config.read(CONFIG_FILE)

        # TCP Server
        global HOST, PORT, BUFFER_SIZE, FORMAT
        
        HOST = config['TCP Server']['host']
        PORT = int(config['TCP Server']['port'])
        BUFFER_SIZE = int(config['TCP Server']['buffer_size'])
        FORMAT = config['TCP Server']['format']
        
        # RPi LCD
        global LCD_PIN_E, LCD_PIN_RS, LCD_PINS_DATA, LCD_SIZE
        
        cols = int(config['RPi LCD']['columns'])
        rows = int(config['RPi LCD']['rows'])
        LCD_SIZE = {'cols' : cols, 'rows' : rows}
        
        LCD_PIN_E = int(config['RPi LCD']['pin_e'])
        LCD_PIN_RS = int(config['RPi LCD']['pin_rs'])
        LCD_PINS_DATA = config['RPi LCD']['pins_data'].split(', ')
        
        for i in range(len(LCD_PINS_DATA)):
            LCD_PINS_DATA[i] = int(LCD_PINS_DATA[i])
    
    
    except KeyError as e:
        sys.stderr.write('-- Config Key Error --')
        sys.stderr.write(str(e))
        sys.exit(1)
    
    except Exception as e:
        sys.stderr.write('-- Unexpected Error Config --')
        sys.stderr.write(str(type(e)))
        sys.stderr.write(str(e))
        sys.exit(1)


def main():
    # -- Config
    print('Reading config... ', end='')
    config_init()
    print('Done.')
    
    # -- LCD Display
    print('Setting up the LCD display... ', end='')
    lcd = LCD_Display(size=LCD_SIZE, pin_e=LCD_PIN_E, pin_rs=LCD_PIN_RS, pins_data=LCD_PINS_DATA)
    print('Done.')
    
    # -- TCP Server
    print('Setting up the server... ', end='')
    server = TCP_Server((HOST, PORT), BUFFER_SIZE, lcd, FORMAT)
    print('Done.\n')
    
    try:
        server.run()
        
    except KeyboardInterrupt:
        lcd.write(0, '-- Manually Interrupt --'.center(24))
        lcd.write(1, '')
        print('-- Manually Interrupt --')
    
    except Exception as e:
        lcd.write(0, '-- Error Server --')
        lcd.write(1, '')
        
        sys.stderr.write('-- Unexpected Error Server --')
        sys.stderr.write(str(type(e)))
        sys.stderr.write(str(e))
        sys.exit(1)
        

if __name__ == '__main__':
    main()
    sys.exit(0)
