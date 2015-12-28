
from pymjin2 import *

TARGET_ACTION_POP  = "sequence.default.popTarget"
TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class TargetImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinish(self, key, value):
        self.isMoving = False
        self.c.report("target.$SCENE.$NODE.moving", "0")
    def onSelection(self, key, value):
        print "onSelection", key, value
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
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("POP",    TARGET_ACTION_POP)
        self.c.setConst("WAIT",   TARGET_ACTION_WAIT)
        # Listen to target selection.
        self.c.listen("node.$SCENE.$NODE.selected", "1", self.impl.onSelection)
        self.c.provide("target.$SCENE.$NODE.moving", self.impl.setMoving)
        self.c.listen("$POP.$SCENE.$NODE.active", "0", self.impl.onFinish)
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

