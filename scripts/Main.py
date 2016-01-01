
from pymjin2 import *
import random

SINGLE_MAIN_TARGETS_NB         = 5
SINGLE_MAIN_TARGET_NAME        = "target"
SINGLE_MAIN_LEVERAGE_NAME      = "leverage"

class MainImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinishedLoading(self, key, value):
        print "Starting the game"
        self.step()
    def onFinishedPopping(self, key, value):
        self.step()
    def onSelection(self, key, value):
        print "Main.onSelection", key, value
    def popRandomTarget(self):
        random.seed(rand(True))
        id = random.randint(1, SINGLE_MAIN_TARGETS_NB)
        print "pop target", id
        self.c.setConst("NODE", SINGLE_MAIN_TARGET_NAME + str(id))
        self.c.set("target.$SCENE.$NODE.moving", "1")
    def step(self):
        self.popRandomTarget()

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c    = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        # Prepare.
        self.c.setConst("SCENE", sceneName)
        # Listen to scene loading finish.
        self.c.listen("scene.opened", None, self.impl.onFinishedLoading)
        # Listen to target popping finish.
        self.c.listen("target.$SCENE..moving", "0", self.impl.onFinishedPopping)
        # Listen to target selection while it's ready for it.
        self.c.listen("target.$SCENE..selected", "1", self.impl.onSelection)
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        print "{0} Main.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

