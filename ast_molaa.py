# -*- coding: utf-8 -*-

import sys, time, subprocess
sys.path.append("../LocalNet")
from interfaces import PrototypeInterface, runPrototype

## TODO: add GPIO stuff

class ArmaSonora(PrototypeInterface):
    """ ArmaSonora prototype class
        all prototypes must define setup() and loop() functions
        self.messageQ will have all messages coming in from LocalNet """
    (STATE_WAIT, STATE_BANG) = range(2)
    MOTOR_ON_TIME = 20

    def setup(self):
        ## pick what to subscribe to
        self.subscribeToAll()
        ## or....
        for k in self.allReceivers.keys():
            self.subscribeTo(k)
        ## some state variables
        self.currentState = ArmaSonora.STATE_WAIT
        self.lastOnTime = time.time()
    def loop(self):
        ## check state
        if ((self.currentState == ArmaSonora.STATE_WAIT) and
            (not self.messageQ.empty())):
            (locale,type,txt) = self.messageQ.get()
            ## TODO: turn gpio(s) on
            self.currentState = ArmaSonora.STATE_BANG
            self.lastOnTime = time.time()
        elif ((self.currentState == ArmaSonora.STATE_BANG) and
              (time.time()-self.lastOnTime > ArmaSonora.MOTOR_ON_TIME)):
            ## TODO: turn off gpio(s)
            self.currentState = ArmaSonora.STATE_WAIT

if __name__=="__main__":
    ## TODO: get ip and ports from command line
    mAST = ArmaSonora(8989,"127.0.0.1",8888)
    runPrototype(mAST)
