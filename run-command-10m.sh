#!/bin/sh  

echo "starting alerts on a 10m loop"

while true  
do  
  python3 /app/main.py >> /proc/1/fd/1 
  sleep 600  
done
