import sys
import os
import configparser as cfgp

from tcp_server import TCP_Server
from lcd_display import LCD_Display

CONFIG_FILE = './config.ini'
PID_FILE = '/var/lcd_socket.pid'


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
        print('-- Config Error --')
        print(e)
    
    except Exception as e:
        print('-- Unexpected Error Config --')
        print(type(e))
        print(e)
        sys.exit(1)


def store_pid():
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))


def main():
    # -- PID
    print('Storing the PID... ', end='')
    store_pid()
    print('Done.\n')
    
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
    print('Done.')
    
    try:
        server.run()
        
    except KeyboardInterrupt:
        print('-- Manually Interrupt --')
    
    except Exception as e:
        print('-- Unexpected Error Server --')
        print(type(e))
        print(e)
        sys.exit(1)
        

if __name__ == '__main__':
    main()
    sys.exit(0)