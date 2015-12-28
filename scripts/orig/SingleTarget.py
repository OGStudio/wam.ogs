
import pymjin2

SINGLE_TARGET_ACTION_POP  = "sequence.default.popTarget"
SINGLE_TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class SingleTargetImpl(object):
    def __init__(self, user):
        # Refer.
        self.u = user
        # Create.
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.u = None
    def onPopFinished(self, key, value):
        self.isMoving = False
        self.u.report(self.property("moving"), "0")
    def onSelection(self, key, value):
        # Ignore selection if we're not moving.
        if (not self.isMoving):
            return
        self.u.report(self.property("selected"), "1")
        self.u.report(self.property("selected"), "0")
    def onWait(self, key, value):
        self.u.report(self.property("catch"), value[0])
    def property(self, name):
        return "target.$SCENE.$NODE." + name
    def setMoving(self, key, value):
        self.isMoving = True
        self.u.set("$POP.$SCENE.$NODE.active", "1")

class SingleTarget(object):
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env       = env
        self.sceneName = sceneName
        self.nodeName  = nodeName
        # Create.
        self.u = pymjin2.EnvironmentUser("SingleTarget/" + nodeName,
                                         "Turn specific node into WAM target")
        self.impl = SingleTargetImpl(self.u)
        # Constants.
        self.u.d["SCENE"] = sceneName
        self.u.d["NODE"]  = nodeName
        self.u.d["POP"]   = SINGLE_TARGET_ACTION_POP
        self.u.d["WAIT"]  = SINGLE_TARGET_ACTION_WAIT
        # Listen to node selection.
        self.u.listen("selector.$SCENE.selectedNode",
                      nodeName,
                      self.impl.onSelection)
        # Listen to pop action finish.
        self.u.listen("$POP.$SCENE.$NODE.active", "0", self.impl.onPopFinished)
        # Listen to wait action.
        self.u.listen("$WAIT.$SCENE.$NODE.active", None, self.impl.onWait)
        # Report "catch".
        self.u.provide(self.impl.property("catch"))
        # Accept "moving".
        self.u.provide(self.impl.property("moving"), self.impl.setMoving)
        # Report "selected".
        self.u.provide(self.impl.property("selected"))
        # Prepare.
        self.env.registerUser(self.u)
    def __del__(self):
        # Tear down.
        self.env.deregisterUser(self.u)
        # Destroy.
        del self.impl
        del self.u
        # Derefer.
        self.env = None

def SCRIPT_CREATE(sceneName, nodeName, env):
    return SingleTarget(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

