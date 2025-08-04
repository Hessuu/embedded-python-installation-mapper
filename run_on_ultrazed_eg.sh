#!/bin/sh

./sync_to_ultrazed_eg.sh

echo "Running on Ultrazed EG..."
sshpass -p 'root' ssh -o StrictHostKeyChecking=no root@192.168.1.135 python3 -P python-ast-module-finder.py

