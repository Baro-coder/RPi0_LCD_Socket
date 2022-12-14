# RPi0_LCD_Socket

## Description

Python Raspberry Pi LCD Display project.

TCP Socket Server listening for specified data packets specifying
text to be displayed on LCD.

---

## Overview

Project is working as a Linux systemd service *lcd_socket.service*.
Service starts at runlevel 3 (multi-user mode) right after *network-online.target* and listening for data at specified port.

---

## Server

Server is listening at specified address (check *config.ini*) for following
datagrams:

## **Request**

**Body:**

``` text
ROW={LCD Display row}&TEXT={text to be displayed}
```

**Example:**

``` text
ROW=0&TEXT=Text displayed at row 0
```

Requests have to be encoded before being send with specified format (check *config.ini*).

After that request you should receive *RESPONSE_SEQ*.

Then you have to send request with *CLOSE_MSG*:

``` text
!SEQ
```

Then server should answer to client with one of the following responses:
*RESPONSE_SUCCESS*, *RESPONSE_FAILURE*.

## **Responses**

**RESPONSE_SEQ:**

``` text
SEQ-NEXT
```

This response is being send to handle connection and inform that server is 
waiting for the next data packets.

**RESPONSE_SUCCESS:**

``` text
REQ-0
```

This response is being send on the end of the connection and inform client
that the request was valid and was handled correctly.

**RESPONSE_FAILURE:**

``` text
REQ-1
```

This response is being send on the end of the connection and inform client
that the request was invalid.

---

### **Circuit plan**

Project is developed to work with the following circuit.

> ***TODO: Circuit plan image***

#### **Components**

- 1 x LCD Alphanumeric Display [2x24 signs]
- 1 x 10K Ohm resistor
- [Optional] 1 x Potentiometer

Potentiometer is optional component, which allow you to set LCD backlight brightness.

All the pins can be freely modified as you want. Pin numbers are specified in *config.ini*.

``` ini
# - LCD_Socket: config.ini

[TCP Server]
host = 0.0.0.0
port = 7666
buffer_size = 1024
format = utf-8

[RPi LCD]
columns = 24
rows = 2
pin_e = 23
pin_rs = 24
pins_data = 25, 8, 7, 1, 12, 16, 20, 21
```

Check out that TCP Server address is assign to **all net interfaces ('0.0.0.0')** at port **7666**.

---

### **Service**

To use project as a service you need main bash file. Remember to move the bash file outside of the project directory. In this case it is *lcd_socket.sh*.

Service at start firstly updates to latest GitHub repository version, then starting.

``` bash
#!/bin/bash

# - lcd_socket.sh

GITHUB_URL="https://github.com/Baro-coder/RPi0_LCD_Socket"

APP_DIR="/home/pi/.Private/RPi0_LCD_Socket"
MAIN_FILE="${APP_DIR}/main.py"

start(){
    if [[ -f $MAIN_FILE ]]; then
        echo "Starting the service..."
        sudo python $MAIN_FILE
        return 0
    else
        echo "$MAIN_FILE : The file does not exists!"
        return 1
    fi
}

update(){
    if [[ -d $APP_DIR ]]; then
            # App dir exists
            echo "Removing outdated source..."
            sudo rm -R ${APP_DIR}
    fi

    PARENT_DIR="${APP_DIR%/*}"

    cd $PARENT_DIR

    git clone $GITHUB_URL

    return $?
}



update

if [ $? -eq 0 ]; then
    start
    exit $?
else
    echo "Something went wrong during git cloning..."
    exit $?
fi
```

Next you need your *.service* file to copy to the */lib/systemd/system* directory.

``` service
[Unit]
Description=Raspberry Pi LCD Display TCP Socket Server
After=network-online.target
StartLimitIntervalSec=0

[Service]
ExecStart=/bin/bash /home/pi/.Private/lcd_socket.sh
WorkingDirectory=/home/pi/.Private
StandardOutput=append:/var/log/lcd_socket.log
StandardError=append:/var/log/lcd_socket.log
Restart=always
RestartSec=1
User=pi

[Install]
WantedBy=multi-user.target
```

**Example copy command:**

``` code
sudo cp /path/to/lcd_socket.service /lib/systemd/system/lcd_socket.service
```

Logs from service will be stored in default logfiles for systemd in */var/log/* and additionally in specified filepaths.

> StandardOutput=append:/var/log/lcd_socket.log
>  
> StandardError=append:/var/log/lcd_socket.log

After that service should be available by *systemd*, and if you want to run service after every boot, just enable it with *systemctl* like:

``` code
sudo systemctl enable lcd_socket.service
```

To start service type:

``` code
sudo systemctl start lcd_socket.service
```
