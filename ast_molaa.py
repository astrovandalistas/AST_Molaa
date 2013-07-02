# -*- coding: utf-8 -*-

import sys, time, subprocess
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype

## import wiringpi lib if available
HAS_WIRINGPI = True
try:
    import wiringpi
except ImportError:
    HAS_WIRINGPI = False

class ArmaSonora(PrototypeInterface):
    """ ArmaSonora prototype class
        all prototypes must define setup() and loop() functions
        self.messageQ will have all messages coming in from LocalNet """
    (STATE_WAIT, STATE_BANG) = range(2)
    MOTOR_ON_TIME = 8
    MOTOR_OFF_TIME = 5
    MOTOR_PINS = [22,23,24]

    def _setupGpio(self):
        ## setup GPIO object (real or fake)
        if (HAS_WIRINGPI):
            self.gpio = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
            for m in ArmaSonora.MOTOR_PINS:
                subprocess.call("gpio export "+str(m)+" out 2> /dev/null", shell=True)
                self.gpio.pinMode(m,self.gpio.OUTPUT)
                self.gpio.digitalWrite(m,self.gpio.LOW)
        else:
            # define fake gpio class with gpio.LOW, gpio.HIGH, gpio.digitalWrite, etc
            class Gpio(object):
                def __init__(self):
                    self.LOW = False
                    self.HIGH = True
                    self.OUTPUT = 0
                def digitalWrite(self,pin=0, val=False):
                    print "turning fake pin %s to %s" % (pin,val)
                def pinMode(self,pin=0, val=False):
                    print "setting fake pin %s to %s" % (pin,val)
            self.gpio = Gpio()

    def setup(self):
        ## subscribe to all receivers
        self.subscribeToAll()
        """
        ## or pick which ones
        for k in self.allReceivers.keys():
            self.subscribeTo(k)
        ## or subscribe to osc
            self.subscribeTo('osc')
        """
        ## some state variables
        self.currentState = ArmaSonora.STATE_WAIT
        self.lastOnTime = time.time()
        self.lastOffTime = time.time()
        self._setupGpio()
    def loop(self):
        ## check state
        if ((self.currentState == ArmaSonora.STATE_WAIT) and
            (time.time()-self.lastOffTime > ArmaSonora.MOTOR_OFF_TIME) and
            (not self.messageQ.empty())):
            (locale,type,txt) = self.messageQ.get()
            ## turn gpio(s) on
            print "you make me HIGH"
            for m in ArmaSonora.MOTOR_PINS:
                self.gpio.digitalWrite(m,self.gpio.HIGH)
            self.currentState = ArmaSonora.STATE_BANG
            self.lastOnTime = time.time()
        elif ((self.currentState == ArmaSonora.STATE_BANG) and
              (time.time()-self.lastOnTime > ArmaSonora.MOTOR_ON_TIME)):
            ## turn off gpio(s)
            print "you make me LOW"
            for m in ArmaSonora.MOTOR_PINS:
                self.gpio.digitalWrite(m,self.gpio.LOW)
            self.currentState = ArmaSonora.STATE_WAIT
            self.lastOffTime = time.time()

if __name__=="__main__":
    ## TODO: get ip and ports from command line
    mAST = ArmaSonora(8989,"127.0.0.1",8888)
    runPrototype(mAST)
