#!/usr/bin/python

#A prgram that allows for serial communication with a yamaha rx-v1900. 
#
#

#need to make sure /deb/ttyUSB0 is has write permissions. 
#easiest to add user to dialup group:
#sudo adduser user dialout

import serial
import sys
import time
import re

#NOTE: this is an incomplete list of commands gathered from various sources online. 
#mostly stuff that i need
commands={"input cd":"07A15"
,"power on":"07E7E"
,"power off":"07E7F"
,"input tuner":"07A16" 
,"input tv":"07A54"
,"input cd":"07A15"
,"input dvd":"07AC1"
,"input bd":"07AC8"
,"input cable":"07ac0"
,"volume up":"07A1A"
,"volume up":"07A1A"
,"volume down":"07A1B"
,"volume -20":"2309F"
,"volume -25":"23095"
,"volume -30":"2308B"
,"volume -35":"23081"
,"volume -40":"23077"
,"volume -45":"2306D"
,"volume -50":"23063"
,"volume -55":"23059"
,"volume -60":"2304F"
,"volume -65":"23045"
,"volume -70":"2303B"
,"volume -75":"23031"
,"volume -80":"23027"
,"mute on":"07EA2"
,"mute off":"07EA3"
,"sleep off":"07EB3"
,"sleep 120":"07EB4"
,"sleep 90":"07EB5"
,"sleep 60":"07EB6"
,"sleep 30":"07EB7"
,"dsp 7ch":"07EFF"
,"dsp 2ch":"07EC0"
,"dsp cinema":"07EFD"
,"dsp straight":"07EE0"
,"dsp drama":"07EFC"
,"get volume":"22001"
}

def execCommand(cmnd, init=False, beforeSleep=None, readResponse=False):

    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=serial.EIGHTBITS, 
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1, 
            xonxoff=False, rtscts=False, writeTimeout=1, dsrdtr=False, interCharTimeout=None)

    ser.open()

    response=""

    #DO WE NEED THIS?!
    #prepare the receiver for the command
    if init:
        ser.write('\x11')
        #ser.write("001") #from lyc
        ser.write("000")
        ser.write('\x03')

        time.sleep(0.20)

    if beforeSleep is not None:
        time.sleep(beforeSleep)

    #write the command
    ser.write('\x02')
    ser.write(cmnd)
    ser.write('\x03')

    if readResponse:
        response=ser.readline()
        #print(response)

    ser.close()

    return response


if __name__=="__main__":


    response=""

    cmndText=" ".join(sys.argv[1:]).lower()
    try:
        if cmndText=="volume +":
            cmnd=commands["volume up"]
            response=execCommand(cmnd)
            for i in range(7):
                execCommand(cmnd, beforeSleep=0.05)
        elif cmndText=="volume -":
            cmnd=commands["volume down"]
            response=execCommand(cmnd)
            for i in range(7):
                execCommand(cmnd, beforeSleep=0.05)
        elif cmndText=="power on":
            cmnd=commands[cmndText]
            response=execCommand(cmnd, init=True)
        elif cmndText.startswith("raw"):
            cmnd=cmndText[3:].strip()
            response=execCommand(cmnd)
        elif cmndText=="get volume":
            cmnd=commands[cmndText]
            execCommand(cmnd)
            response=execCommand(cmnd, init=True, readResponse=True)
            #print(response)
            volRe = re.compile(r"[+-]?\d+(?:\.\d+)?dB")
            vol=volRe.search(response)
            if vol is not None:
                vol=(volRe.search(response).group(0))[:-4]+"dB"
            else: 
                vol=""
            response=vol
        else:
            cmnd=commands[cmndText]
            execCommand(cmnd)
            response=execCommand(cmnd)

    except KeyError:
        sys.stderr.write("Command not found...\n")
        sys.exit(-1)
    except OSError:
        sys.stderr.write("Can't access Yamaha serial port... maybe busy.\n")
        sys.exit(-1)

    print(response)

