#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import socket
import struct

continue_reading = True

read_one = True

rfid1_online = False
rfid2_online = False
rfid1_id = None
rfid2_id = None

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()
    
# Create socket for sending ID to server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#clientSocket.connect(('10.0.0.4', 8081))
clientSocket.connect(('192.168.1.15', 8081))
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522


# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    if read_one:
        MIFAREReader1 = MFRC522.MFRC522('/dev/spidev0.0')
        # Scan for cards    
        (status1,TagType1) = MIFAREReader1.MFRC522_Request(MIFAREReader1.PICC_REQIDL)

        # If a card is found
        if status1 == MIFAREReader1.MI_OK:
            print "Card 1 detected"
            
        # Get the UID of the card
        (status1,uid1) = MIFAREReader1.MFRC522_Anticoll()

        # If we have the UID, continue
        if status1 == MIFAREReader1.MI_OK:
		if rfid1_online == False:
			# Print UID
			print "Card read UID: %s,%s,%s,%s" % (uid1[0], uid1[1], uid1[2], uid1[3])
			
			
			# This is the default key for authentication
			key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
			
			# Select the scanned tag
			MIFAREReader1.MFRC522_SelectTag(uid1)
			
			# Authenticate
			status1 = MIFAREReader1.MFRC522_Auth(MIFAREReader1.PICC_AUTHENT1A, 8, key, uid1)
			
			# Check if authenticated
			if status1 == MIFAREReader1.MI_OK:
				rfid1_id = MIFAREReader1.MFRC522_ReadData(8)
				MIFAREReader1.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
			
			print "Sending " + str(rfid1_id) + " to socket at port 10.0.0.4:8081"
	                packetData = struct.pack('b' * 16, *rfid1_id)
	                clientSocket.send(packetData)
			rfid1_online = True
	else:
		if rfid1_online == True:
			print "Sending " + str(rfid1_id) + " to socket at port 10.0.0.4:8081"
	                packetData = struct.pack('b' * 16, *rfid1_id)
	                clientSocket.send(packetData)
			rfid1_online = False
	
                
        read_one = False
                
    else:         
        MIFAREReader2 = MFRC522.MFRC522('/dev/spidev0.1')   
        # Scan for cards    
        (status2,TagType2) = MIFAREReader2.MFRC522_Request(MIFAREReader2.PICC_REQIDL)    
        # If a card is found
        #if status1 == MIFAREReader1.MI_OK:
        #    print "Card 1 detected"
        
        if status2 == MIFAREReader2.MI_OK:
            print "Card 2 detected"
            
        # Get the UID of the card
        #(status1,uid1) = MIFAREReader1.MFRC522_Anticoll()
        (status2,uid2) = MIFAREReader2.MFRC522_Anticoll()

        # If we have the UID, continue
        if status2 == MIFAREReader2.MI_OK:
	
		if rfid2_online == False:
			# Print UID
			print "Card read UID: %s,%s,%s,%s" % (uid2[0], uid2[1], uid2[2], uid2[3])
			
			# This is the default key for authentication
			key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
			
			# Select the scanned tag
			MIFAREReader2.MFRC522_SelectTag(uid2)
			
			# Authenticate
			status2 = MIFAREReader2.MFRC522_Auth(MIFAREReader2.PICC_AUTHENT1A, 8, key, uid2)
			
			# Check if authenticated
			if status2 == MIFAREReader2.MI_OK:
				rfid2_id = MIFAREReader2.MFRC522_ReadData(8)
				MIFAREReader2.MFRC522_StopCrypto1()
			else:
                		print "Authentication error"

			print "Sending " + str(rfid2_id) + " to socket at port 10.0.0.4:8081"
			packetData = struct.pack('b' * 16, *rfid2_id);
			clientSocket.send(packetData)

			rfid2_online = True
	else:
		if rfid2_online == True:
			print "Sending " + str(rfid2_id) + " to socket at port 10.0.0.4:8081"
			packetData = struct.pack('b' * 16, *rfid2_id);
			clientSocket.send(packetData)
			rfid2_online = False;
                
        read_one = True