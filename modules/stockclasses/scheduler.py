"""The Scheduler is a class designed to keep a set of timers to keep track of when things should happen in game logic."""

class Scheduler:
    def __init__( self, timerDict ):
        self.timers = {}
        self.targetTimes = {}
        self.hitEvent = {}
        for eachKey, eachVal in timerDict.items():
            self.timers[eachKey] = None
            self.targetTimes[eachKey] = eachVal
            self.hitEvent[eachKey] = False

    def tick( self, dt ):
        for eachKey in self.timers.keys():
            if self.timers[eachKey] is not None:
                self.timers[eachKey] += dt
                if self.timers[eachKey] >= self.targetTimes[eachKey]:
                    self.hitEvent[eachKey] = True
                    self.timers[eachKey] = None

    def checkEvent( self, timerName ):
        tmp = self.hitEvent[timerName]
        self.hitEvent[timerName] = False
        return tmp

    def checkTimerGoing( self, timeName ):
        return self.timers[timeName] != None

    def start( self, timeName ):
        self.timers[timeName] = 0.0
        
