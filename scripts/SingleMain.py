
import pymjin2
import random

#SINGLE_MAIN_FOLLOW_ACTION = "move.default.followTarget"
#SINGLE_MAIN_NODE_FOLLOW   = "follower"

MAIN_FOLLOWER_ACTION    = "move.default.followTarget"
MAIN_FOLLOWER_NAME      = "follower"
MAIN_FOLLOWER_SYNC_TIME = 1000
MAIN_TARGETS_LEVERAGES  = { "target1" : "leverage1",
                            "target2" : "leverage2",
                            "target3" : "leverage3",
                            "target4" : "leverage4",
                            "target5" : "leverage5" }
MAIN_TIMER_LIGHT_PREFIX  = "time"
MAIN_TIMER_LIGHTS        = 20
MAIN_TIMER_LIGHT_ON      = "time_on"
MAIN_TIMER_LIGHT_OFF     = "time_off"
MAIN_TIMER_TICKER_ACTION = "rotate.default.tickLeverage"
MAIN_SCORE_LIGHT_PREFIX  = "score"
MAIN_SCORE_LIGHTS        = 20
MAIN_SCORE_LIGHT_ON      = "score_on"
MAIN_SCORE_LIGHT_OFF     = "score_off"

class MainImpl(object):
    def __init__(self, scene, senv, action):
        # Refer.
        self.scene  = scene
        self.senv   = senv
        self.action = action
        # Create.
        self.activeTarget            = None
        self.score                   = 0
        self.timeLeft                = MAIN_TIMER_LIGHTS * 2
        self.followerInitialPosition = None
    def __del__(self):
        # Derefer.
        self.scene  = None
        self.senv   = None
        self.action = None
    def moveLeverage(self, sceneName, nodeName):
        st = pymjin2.State()
        key = "leverage.{0}.{1}.moving".format(sceneName, nodeName)
        st.set(key, "1")
        self.senv.setState(st)
    def onFollowerPosition(self, key, values):
        pass
        #print "onFollowerPosition", key, values
    def onLeverageHit(self, key, values):
        # Ignore dehitting.
        if (values[0] == "0"):
            return
        # Nothing to hit.
        if (not self.activeTarget):
            return
        v = key.split(".")
        sceneName = v[1]
        targetLeverage = MAIN_TARGETS_LEVERAGES[self.activeTarget]
        v = key.split(".")
        if (targetLeverage == v[2]):
            self.score = self.score + 1
            self.setScore(sceneName, self.score)
    def onLeverageMotion(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        property = v[3]
        state = values[0]
        # Ignore activation.
        if (state != "0"):
            return
        print "onLeverageMotion", key, values
    def onTargetCatching(self, key, values):
        if (values[0] == "0"):
            self.activeTarget = None
            return
        v = key.split(".")
        self.activeTarget = v[2]
    def onTargetMotion(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        property = v[3]
        state = values[0]
        # Ignore activation.
        if (state != "0"):
            return
        # Motion finished. Proceed with the game.
        if (property == "moving"):
            self.step(sceneName)
    def onTargetSelection(self, key, values):
        # Ignore deselection.
        if (values[0] != "1"):
            return
        v = key.split(".")
        sceneName = v[1]
        targetName = v[2]
        nodeName  = MAIN_TARGETS_LEVERAGES[targetName]
        self.moveLeverage(sceneName, nodeName)
        self.syncFollower(sceneName, targetName)
    def popRandomTarget(self, sceneName):
        random.seed(pymjin2.rand(True))
        id = random.randint(0, len(MAIN_TARGETS_LEVERAGES) - 1)
        targetName = MAIN_TARGETS_LEVERAGES.keys()[id]
        key = "target.{0}.{1}.moving".format(sceneName, targetName)
        st = pymjin2.State()
        st.set(key, "1")
        self.senv.setState(st)
    def setScore(self, sceneName, value):
        print "setScore", value
        st = pymjin2.State()
        for i in range(0, MAIN_SCORE_LIGHTS):
            mat = MAIN_SCORE_LIGHT_OFF
            if (i < value):
                mat = MAIN_SCORE_LIGHT_ON
            key = "node.{0}.{1}{2}.material".format(sceneName,
                                                    MAIN_SCORE_LIGHT_PREFIX,
                                                    i + 1)

            st.set(key, mat)
        self.scene.setState(st)
    def setTimer(self, sceneName, value):
        st = pymjin2.State()
        for i in range(1, MAIN_TIMER_LIGHTS + 1):
            mat = MAIN_TIMER_LIGHT_ON
            if (i > value):
                mat = MAIN_TIMER_LIGHT_OFF
            key = "node.{0}.{1}{2}.material".format(sceneName,
                                                    MAIN_TIMER_LIGHT_PREFIX,
                                                    i)

            st.set(key, mat)
        self.scene.setState(st)
    def setupFollower(self, sceneName, nodeName):
        key = "node.{0}.{1}.position".format(sceneName, nodeName)
        st = self.scene.state([key])
        self.followerInitialPosition = st.value(key)[0].split(" ")
    def step(self, sceneName):
        # Do not proceed if time is off.
        if (self.timeLeft < 0):
            print "Game over"
            return
        self.popRandomTarget(sceneName)
        # Tick the timer each target pop cycle iteration.
        self.tickTimer(sceneName)
    def syncFollower(self, sceneName, targetName):
        key = "node.{0}.{1}.position".format(sceneName, targetName)
        st = self.scene.state([key])
        if (not len(st.keys)):
            print "Could not get target position"
            return
        tpos = st.value(key)[0].split(" ")
        key = "{0}.point".format(MAIN_FOLLOWER_ACTION)
        st = pymjin2.State()
        pos1 = "{0} {1} {2} {3}".format(MAIN_FOLLOWER_SYNC_TIME,
                                        tpos[0],
                                        tpos[1],
                                        self.followerInitialPosition[2])
        pos2 = "{0} {1} {2} {3}".format(MAIN_FOLLOWER_SYNC_TIME,
                                        self.followerInitialPosition[0],
                                        self.followerInitialPosition[1],
                                        self.followerInitialPosition[2])
        poss = [pos1, pos2]
        st.set(key, poss)
        key = "{0}.active".format(MAIN_FOLLOWER_ACTION)
        st.set(key, "1")
        self.action.setState(st)
    def tickTimer(self, sceneName):
        self.timeLeft = self.timeLeft - 1
        self.setTimer(sceneName, self.timeLeft / 2 + 1)
        self.tickTimerTicker()
    def tickTimerTicker(self):
        st = pymjin2.State()
        key = "{0}.active".format(MAIN_TIMER_TICKER_ACTION)
        st.set(key, "1")
        self.action.setState(st)

class SingleMain:
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env = env
        # Create.
        self.u = EnvironmentUser("SingleMain", "Whac-a-mole main script")
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


        CONTINUE


        self.impl.setupFollower(sceneName, MAIN_FOLLOWER_NAME)
        self.impl.step(sceneName)
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

