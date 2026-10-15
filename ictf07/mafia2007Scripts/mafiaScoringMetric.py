from Common import scoring
from Common import botGlobals
import math

class MafiaScoringMetric(scoring.BaseScoringMetric):
    
    def __init__(self):
        self.weight = 0.5
        self.duration_in_seconds = 15*60
    
    def getDefensivePoints(self, team, service, challengeInfo):
        if not team.getName() in challengeInfo:
            print "Challenge results do not contain team: %s" % team.getName()
            return 1
        else:
            results = challengeInfo[team.getName()]
            challengeLevel = int(results[service.getName()])
            if(challengeLevel >= 1):
                return 1
            else:
                print "Team %s must unlock level 1 for service %s!" % (team.getName(),service.getName())
                return 0
    
    def getOffensivePoints(self, hacker, flag, otherTeams, challengeInfo):
        if not hacker.getName() in challengeInfo:
            print "Challenge results do not contain team: %s" % hacker.getName()
            return 0
        else:
            results = challengeInfo[hacker.getName()]
            challengeLevel = int(results[service.getName()])
            
            if(challengeLevel >= 2):
                offensiveScore = hacker.getOffensiveScore()
                totalScore = botGlobals.instance().getTotalPoints()
                service = botGlobals.instance().getServiceById(flag.getServiceId()) 
                return math.ceil(service.getValue()*self.calculateOffensiveFactor(offensiveScore,totalScore))
            
            else:
                print "Team %s must unlock level 2 for service %s!" % (hacker.getName(),service.getName())
                return 0
    
    def isFlagActive(self, timeCreated, timeSubmitted):
        diff = timeCreated - timeSubmitted
        print "Simple flag scoring - diff: " + str(diff)
        if(diff.seconds > self.duration_in_seconds):
            print "Flag is older then 5 minutes!"
            return False
        else:
            return True
        
    def calculateOffensiveFactor(self, teamPoints, totalPoints):
        return (self.weight* (1.0 - (teamPoints/(totalPoints+1.0))) + (1.0 - self.weight))
  
def getScoringMetric():
    """
    this must be defined in every ScoringMetric module.
    """
    return MafiaScoringMetric