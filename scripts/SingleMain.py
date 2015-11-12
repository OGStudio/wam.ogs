
import pymjin2
import random

SINGLE_MAIN_TARGETS_NB         = 5
SINGLE_MAIN_TARGET_NAME        = "target"
SINGLE_MAIN_LEVERAGE_NAME      = "leverage"
SINGLE_MAIN_SCORE_LIGHT_PREFIX = "score"
SINGLE_MAIN_SCORE_LIGHTS       = 20
SINGLE_MAIN_SCORE_LIGHT_ON     = "score_on"
SINGLE_MAIN_TIMER_LIGHT_PREFIX = "time"
SINGLE_MAIN_TIMER_LIGHTS       = SINGLE_MAIN_SCORE_LIGHTS
SINGLE_MAIN_TIMER_LIGHT_OFF    = "time_off"
SINGLE_MAIN_INITIAL_TIME       = SINGLE_MAIN_TIMER_LIGHTS * 2

class SingleMainImpl(object):
    def __init__(self, user):
        # Refer.
        self.u = user
        # Create.
        self.activeTarget = None
        self.score        = 0
        self.timeLeft     = SINGLE_MAIN_INITIAL_TIME
    def __del__(self):
        # Derefer.
        self.u = None
    def onLeverageHit(self, key, value):
        # No active target to hit.
        if (not self.activeTarget):
            return
        activeTargetLeverage = self.targetToLeverage(self.activeTarget)
        leverage = key[2]
        # Successful hit of the expected leverage.
        if (activeTargetLeverage == leverage):
            self.score = self.score + 1
            self.setScore(self.score)
    def onTargetCatching(self, key, value):
        if (value[0] == "0"):
            self.activeTarget = None
            return
        self.activeTarget = key[2]
    def onTargetMotionFinish(self, key, value):
        # Continue the game loop.
        self.step()
    def onTargetSelection(self, key, value):
        target = key[2]
        leverage = self.targetToLeverage(target)
        self.u.d["LEVERAGE"] = leverage
        self.u.set("leverage.$SCENE.$LEVERAGE.moving", "1")
    def popRandomTarget(self):
        random.seed(pymjin2.rand(True))
        id = random.randint(1, SINGLE_MAIN_TARGETS_NB)
        self.u.d["TARGET"] = SINGLE_MAIN_TARGET_NAME + str(id)
        self.u.set("target.$SCENE.$TARGET.moving", "1")
    def setScore(self, value):
        print "setScore", value
        self.u.d["SCORE"] = SINGLE_MAIN_SCORE_LIGHT_PREFIX + value
        self.u.set("node.$SCENE.$SCORE.material", SINGLE_MAIN_SCORE_LIGHT_ON)
    def setTimer(self, value):
        print "setTimer", value
        id = value
        # Nothing to do yet.
        if (id == SINGLE_MAIN_TIMER_LIGHTS):
            return
        id = id + 1
        self.u.d["TIMER"] = SINGLE_MAIN_TIMER_LIGHT_PREFIX + str(id)
        self.u.set("node.$SCENE.$TIMER.material", SINGLE_MAIN_TIMER_LIGHT_OFF)
    def step(self):
        # Do not proceed the game if time is off.
        if (self.timeLeft < 0):
            print "Game over"
            return
        self.popRandomTarget()
        self.tickTimer()
    def targetToLeverage(self, target):
        v = target.split(SINGLE_MAIN_TARGET_NAME)
        return "{0}{1}".format(SINGLE_MAIN_LEVERAGE_NAME, v[1])
    def tickTimer(self):
        self.timeLeft = self.timeLeft - 1
        # Only decrease once in two pops.
        self.setTimer(self.timeLeft / 2 + 1)

class SingleMain:
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env = env
        # Create.
        self.u = pymjin2.EnvironmentUser("SingleMain",
                                         "Whac-a-mole main script")
        self.impl = SingleMainImpl(self.u)
        # Prepare.
        # Constants.
        self.u.d["SCENE"] = sceneName
        # Listen to target selection.
        self.u.listen("target.$SCENE..selected",
                      "1",
                      self.impl.onTargetSelection)
        # Listen to target catching availability.
        self.u.listen("target.$SCENE..catch",
                      None,
                      self.impl.onTargetCatching)
        # Listen to target motion finish.
        self.u.listen("target.$SCENE..moving",
                      "0",
                      self.impl.onTargetMotionFinish)
        # Listen to leverage hit.
        self.u.listen("leverage.$SCENE..hit", "1", self.impl.onLeverageHit)
        self.env.registerUser(self.u)
        # Start the game loop.
        self.impl.step()
    def __del__(self):
        # Tear down.
        self.env.deregisterUser(self.u)
        # Destroy.
        del self.impl
        del self.u
        # Derefer.
        self.env = None

def SCRIPT_CREATE(sceneName, nodeName, env):
    return SingleMain(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

