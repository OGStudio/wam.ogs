
from pymjin2 import *

TARGET_ACTION_POP  = "sequence.default.popTarget"
TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class TargetImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving  = False
        self.isWaiting = False
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinish(self, key, value):
        self.isMoving = False
        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def onSelection(self, key, value):
        if (not self.isWaiting):
            return
        self.c.report("$TYPE.$SCENE.$NODE.selected", "1")
        self.c.report("$TYPE.$SCENE.$NODE.selected", "0")
    def onWait(self, key, value):
        self.isWaiting = (value[0] == "1")
    def setMoving(self, key, value):
        self.isMoving = True
        self.c.set("$POP.$SCENE.$NODE.active", "1")

class Target(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        name      = "Target/{0}/{1}".format(sceneName, nodeName)
        self.c    = EnvironmentClient(env, name)
        self.impl = TargetImpl(self.c)
        # Prepare.
        self.c.setConst("TYPE",  "target")
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("POP",    TARGET_ACTION_POP)
        self.c.setConst("WAIT",   TARGET_ACTION_WAIT)
        # Listen to target selection.
        self.c.listen("node.$SCENE.$NODE.selected", "1", self.impl.onSelection)
        # Provide 'moving'.
        self.c.provide("target.$SCENE.$NODE.moving", self.impl.setMoving)
        # Provide 'selected'.
        self.c.provide("target.$SCENE.$NODE.selected")
        # Listen to pop action to report 'moving' finish.
        self.c.listen("$POP.$SCENE.$NODE.active", "0", self.impl.onFinish)
        # Listen to delay action to know when 'selected' can be reported.
        self.c.listen("$WAIT.$SCENE.$NODE.active", None, self.impl.onWait)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Target(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

