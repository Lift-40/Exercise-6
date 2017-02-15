import subprocess
import time
import os, sys

deadTreshold = 3 #seconds
delay = 1 #seconds
state = "slave"
counter = 0
scriptPath = os.path.abspath(os.path.dirname(__file__)) + "\phoenix.py"
print("New process started - state set to slave")
print("Script path: "+scriptPath)

def readCounterValueFromBackup():
	f = open("backup.txt", 'r')
	counter = int(f.readline().strip("\n").split(" ")[1])
	f.close()
	return counter

def fileWrittenToRecently():
	f = open("backup.txt", 'r')
	backupTimestamp = int(f.readline().strip("\n").split(" ")[0])
	f.close()
	if state is "slave":
		print("[SLAVE] File last written to " + str(int(time.time()) - backupTimestamp) + " seconds ago")
	else:
		print("[MASTER] File last written to " + str(int(time.time()) - backupTimestamp) + " seconds ago")
	# check timestamp in file against current time, return true or false
	return (deadTreshold >= int(time.time()) - backupTimestamp)

def storeBackup(counter):
	f = open("backup.txt", 'w')
	f.seek(0)
	f.truncate()
	f.write(str(int(time.time())) + " " + str(counter))
	f.close()
	
if not os.path.isfile("backup.txt"):
	f = open("backup.txt", 'w')
	storeBackup(counter)
	f.close()

# check if file has been written to recently
while True:
	if not fileWrittenToRecently() and state is "slave":
		print("[SLAVE] Master timed out, assumed dead - state set to master")
		subprocess.Popen("start cmd /C py \"" + scriptPath +"\"", shell=True)
		print("[MASTER] Tried to spawn new backup process")
		state = "master"
		counter = readCounterValueFromBackup()
	if state is "master":
		print("[MASTER] Counter value: "+str(counter))
		counter = counter + 1
		storeBackup(counter)
	time.sleep(1)
