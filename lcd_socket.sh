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