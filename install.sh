#!/bin/bash


FILE=/usr/local/bin/vmfinder
if [ -f "$FILE" ]; then
  sudo rm -rf $FILE
  sudo cp ./vmfinder.py /usr/local/bin/vmfinder
  sudo chmod +x /usr/local/bin/vmfinder
else
  sudo cp ./vmfinder.py /usr/local/bin/vmfinder
  sudo chmod +x /usr/local/bin/vmfinder
fi
