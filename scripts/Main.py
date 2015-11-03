
import pymjin2
import random

MAIN_DEPENDENCY_LEVERAGE = "scripts/Leverage.py"
MAIN_DEPENDENCY_TARGET   = "scripts/Target.py"

MAIN_TARGETS_LEVERAGES = { "target1" : "leverage1",
                           "target2" : "leverage2",
                           "target3" : "leverage3",
                           "target4" : "leverage4",
                           "target5" : "leverage5" }
MAIN_TIMER_LIGHT_PREFIX = "time"
MAIN_TIMER_LIGHTS       = 21
MAIN_TIMER_LIGHT_ON     = "time_on"
MAIN_TIMER_LIGHT_OFF    = "time_off"

class MainImpl(object):
    def __init__(self, scene, senv):
        # Refer.
        self.scene = scene
        self.senv  = senv
        # Create.
        self.activeTarget = None
        self.hitCount     = 0
        self.timeLeft     = MAIN_TIMER_LIGHTS * 2
    def __del__(self):
        # Derefer.
        self.scene = None
        self.senv  = None
    def onLeverageHit(self, key, values):
        # Ignore dehitting.
        if (values[0] == "0"):
            return
        # Nothing to hit.
        if (not self.activeTarget):
            return
        targetLeverage = MAIN_TARGETS_LEVERAGES[self.activeTarget]
        v = key.split(".")
        if (targetLeverage == v[2]):
            self.hitCount = self.hitCount + 1
            print "{0} did a successful hit of {1}. Total: {2}".format(
                targetLeverage,
                self.activeTarget,
                self.hitCount)
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
        nodeName  = MAIN_TARGETS_LEVERAGES[v[2]]
        st = pymjin2.State()
        key = "leverage.{0}.{1}.moving".format(sceneName, nodeName)
        st.set(key, "1")
        self.senv.setState(st)
    def popRandomTarget(self, sceneName):
        random.seed(pymjin2.rand(True))
        id = random.randint(0, len(MAIN_TARGETS_LEVERAGES) - 1)
        targetName = MAIN_TARGETS_LEVERAGES.keys()[id]
        key = "target.{0}.{1}.moving".format(sceneName, targetName)
        st = pymjin2.State()
        st.set(key, "1")
        self.senv.setState(st)
    def setTimer(self, sceneName, value):
        print "setTimer", value
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
    def step(self, sceneName):
        # Do not proceed if time is off.
        if (self.timeLeft < 0):
            print "Game over"
            return
        self.popRandomTarget(sceneName)
        # Tick the timer each target pop cycle iteration.
        self.tickTimer(sceneName)
    def tickTimer(self, sceneName):
        self.timeLeft = self.timeLeft - 1
        print "tickTimer. left:", self.timeLeft
        self.setTimer(sceneName, self.timeLeft / 2 + 1)

class Main:
    def __init__(self,
                 sceneName,
                 nodeName,
                 scene,
                 action,
                 scriptEnvironment,
                 dependencies):
        # Refer.
        self.sceneName    = sceneName
        self.scene        = scene
        self.action       = action
        self.senv         = scriptEnvironment
        self.dependencies = dependencies
        # Create.
        mLeverage = self.dependencies[MAIN_DEPENDENCY_LEVERAGE]
        self.leverage = mLeverage.Leverage(scene, action, scriptEnvironment)
        mTarget = self.dependencies[MAIN_DEPENDENCY_TARGET]
        self.target = mTarget.Target(scene, action, scriptEnvironment)
        self.impl = MainImpl(self.scene, self.senv)
        self.subs = pymjin2.Subscriber()
        #self.listenerSEnv = MainListenerScriptEnvironment(self.impl)
        # Prepare.
        # Enable targets and leverages.
        st = pymjin2.State()
        for k, v in MAIN_TARGETS_LEVERAGES.items():
            key = "target.{0}.{1}.selectable".format(sceneName, k)
            st.set(key, "1")
            key = "leverage.{0}.{1}.movable".format(sceneName, v)
            st.set(key, "1")
        self.senv.setState(st)
        # Listen to target selection.
        key = "target.{0}..selected".format(sceneName)
        self.subs.subscribe(scriptEnvironment, key, self.impl, "onTargetSelection")
        # Listen to target catching availability.
        key = "target.{0}..catch".format(sceneName)
        self.subs.subscribe(scriptEnvironment, key, self.impl, "onTargetCatching")
        # Listen to target motion.
        key = "target.{0}..moving".format(sceneName)
        self.subs.subscribe(scriptEnvironment, key, self.impl, "onTargetMotion")
        # Listen to leverage motion.
#        key = "leverage.{0}..moving".format(sceneName)
#        self.subs.subscribe(scriptEnvironment, key, self.impl, "onLeverageMotion")
        # Listen to leverage hitting.
        key = "leverage.{0}..hit".format(sceneName)
        self.subs.subscribe(scriptEnvironment, key, self.impl, "onLeverageHit")
        # Start the game.
        self.impl.step(sceneName)
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        #self.senv.removeListener(self.listenerSEnv)
        # Derefer.
        self.scene        = None
        self.action       = None
        self.senv         = None
        self.dependencies = None
        # Destroy
        del self.impl
        del self.leverage
        del self.target
        del self.subs
        print "{0} Main.__del__".format(id(self))

def SCRIPT_CREATE(sceneName,
                  nodeName,
                  scene,
                  action,
                  scriptEnvironment,
                  dependencies):
    return Main(sceneName,
                nodeName,
                scene,
                action,
                scriptEnvironment,
                dependencies)

def SCRIPT_DEPENDENCIES():
    return [MAIN_DEPENDENCY_LEVERAGE,
            MAIN_DEPENDENCY_TARGET]

def SCRIPT_DESTROY(instance):
    del instance

