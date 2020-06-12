#!/usr/bin/env python3
import hashlib, os, serial, time, traceback

#todo add Argparser. Temporary setup below
#	-d <dev>			Specify serial device
ArgSerialDevice = '/dev/ttyUSB0'
#	--baud <num>		Baud rate. Default = 57600
ArgBaudrate = 57600
#	--file				File to upload. Must be less than 32KB (32768 bytes). Default = a.out
ArgFile = 'a.out'
#	--only-bytes <num>	Specify how many bytes of file to upload. Default = all
#	--skip-check		Skip EEPROM uploaded data check
#	--bytes-delay		Manually specify delay between sending bytes of file. Default = automatically calculate
#   --verbose			Print debug information

s = serial.Serial(ArgSerialDevice, baudrate=ArgBaudrate) #s.open is not needed - it is opened automatically by serial.Serial
time.sleep(5) #Let arduino send its startup message before flushing the serial port. todo remove this once arduino code is re-written to accept R, W, E (read, write, erase) commands on boot

s.flushInput() #Flush the serial port
s.flushOutput()

serialByteDelayFactor = 0.01;

# todo add if __name__ == '__main__':

try:
	with open(ArgFile, 'rb') as f:
		#Calculate hash of the file to be uploaded to the EEPROM
		print('Calculating md5 hash of ' + ArgFile)
		md5_a_out = hashlib.md5(f.read()).hexdigest()
		print('MD5: ' + str(md5_a_out))

		#Check file isn't too large
		print('Filesize of ' + ArgFile + ' is: ' + str(os.path.getsize(ArgFile)))
		if (os.path.getsize(ArgFile) > 32768):
			raise Exception('File is too large. Maximum size is 32768 bytes')

		#Send file byte-by-byte and slow down more as Arduino serial buffer fills
		print('Sending ' + ArgFile + ' over serial port: ' + ArgSerialDevice)

		f.seek(0) # Go back to the start of the file
		for i in range(0, os.path.getsize(ArgFile)): #Get the size of the file and write that many bytes
			#print(s.inWaiting())
			#print(str(i) + '/' + str(os.path.getsize(ArgFile)))
			#todo calculate speed in bytes per second

			s.write(f.read(1))

			time.sleep(0.005) #Deliberately slow for testing. Flashing takes 5 minutes
			if s.inWaiting() > 0:
				receivedSerial = s.readline() #Read how full the Ardunino's serial buffer is from the Arduino

				#todo if receivedSerial >=63 that means Arduino serial buffer is full and data has been lost. Raise exception here

				print(str(i) + '/' + str(os.path.getsize(ArgFile)) + '    ' + str(receivedSerial)) #todo less frequent status updates
				time.sleep(int(receivedSerial)**2 * serialByteDelayFactor + 0.005) #Sleep for an appropriate amount of time
				#print(int(receivedSerial)**2 * serialByteDelayFactor + 0.005)


				
					

		#todo reset arduino then request and receive bytes to put into variable eeprom_out
		#print('Receiving the next 32768 bytes on the serial port.')

		s.close() #This will reset the Arduino. todo Check that this is not a problem as WE (write enable) pin will go low. Ideally the WE pin shouldn't be on pin 13 - it would be better on A0 which does not change state upon reset.

		#print('Calculating md5 hash of eeprom contents')
		#md5_eeprom_out = hashlib.md5(eeprom_out).hexdigest()

		#print('Comparing hashes')
		#if md5_a_out == md5_eeprom_out:
		#	print('a.out and eeprom contents match. Success!')
		#else:
		#	print('a.out and eeprom contents do not match. Please try again.')
			#Todo: Say how many bytes differ and offer to show comparison / byte diff
except Exception:
	traceback.print_exc()
except:
	print("Unknown error")

