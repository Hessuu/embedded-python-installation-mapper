echo "Syncing files to Ultrazed EG..."
sshpass -p 'root' scp -o StrictHostKeyChecking=no ./*.py root@192.168.1.135:
