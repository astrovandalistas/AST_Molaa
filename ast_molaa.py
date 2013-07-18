# -*- coding: utf-8 -*-

import sys, time, getopt
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
    MOTOR_ON_TIME = 5
    MOTOR_OFF_TIME = 5
    MOTOR_PINS = [17,27,22]

    def _setupGpio(self):
        ## setup GPIO object (real or fake)
        if (HAS_WIRINGPI):
            self.gpio = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_SYS)
            for m in ArmaSonora.MOTOR_PINS:
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
            for m in ArmaSonora.MOTOR_PINS:
                self.gpio.digitalWrite(m,self.gpio.HIGH)
            self.currentState = ArmaSonora.STATE_BANG
            self.lastOnTime = time.time()
        elif ((self.currentState == ArmaSonora.STATE_BANG) and
              (time.time()-self.lastOnTime > ArmaSonora.MOTOR_ON_TIME)):
            ## turn off gpio(s)
            for m in ArmaSonora.MOTOR_PINS:
                self.gpio.digitalWrite(m,self.gpio.LOW)
            self.currentState = ArmaSonora.STATE_WAIT
            self.lastOffTime = time.time()

if __name__=="__main__":
    (inIp, inPort, localNetAddress, localNetPort) = ("127.0.0.1", 8989, "127.0.0.1", 8900)
    opts, args = getopt.getopt(sys.argv[1:],"i:p:n:o:",["inip=", "inport=","localnet=","localnetport="])
    for opt, arg in opts:
        if(opt in ("--inip","-i")):
            inIp = str(arg)
        elif(opt in ("--inport","-p")):
            inPort = int(arg)
        elif(opt in ("--localnet","-n")):
            localNetAddress = str(arg)
        elif(opt in ("--localnetport","-o")):
            localNetPort = int(arg)

    mAST = ArmaSonora(inIp, inPort,localNetAddress,localNetPort)
    runPrototype(mAST)
