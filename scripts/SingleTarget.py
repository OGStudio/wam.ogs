
import pymjin2

TARGET_ACTION_POP  = "sequence.default.popTarget"
TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class Target:
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env       = env
        self.sceneName = sceneName
        self.nodeName  = nodeName
        # Create.
        self.u = EnvironmentUser("Target", "Turn specific node into WAM target")
        self.isMoving = False
        # Listen to node selection.
        self.u.listen(["selector", sceneName, "selectedNode"]
                      nodeName,
                      self.onSelection)
        # Listen to pop action finish.
        self.u.listen([TARGET_ACTION_POP, sceneName, nodeName, "active"],
                      "0",
                      self.onPopFinished)
        # Listen to wait action.
        self.u.listen([TARGET_ACTION_WAIT, sceneName, nodeName, "active"],
                      None,
                      self.onWait)
        # Report "catch".
        self.u.provide(self.property("catch"))
        # Accept "moving".
        self.u.provide(self.property("moving"), self.setMoving)
        # Report "selected".
        self.u.provide(self.property("selected"))
        # Prepare.
        self.env.registerUser(self.u)
    def __del__(self):
        # Tear down.
        self.env.deregisterUser(self.u)
        # Destroy.
        del self.u
        # Derefer.
        self.env = None
    def onPopFinished(self, key, value):
        self.isMoving = False
        self.u.set(self.property("moving"), "0")
    def onSelection(self, key, value):
        # Ignore selection if we're not moving.
        if (not self.isMoving):
            return
        self.u.set(self.property("selected"), "1")
        self.u.set(self.property("selected"), "0")
    def onWait(self, key, value):
        self.u.set(self.property("catch"), value[0])
    def property(self, name):
        return ["target", self.sceneName, self.nodeName, name]
    def setMoving(self, key, value):
        # Assume setMoving is only called with value = 1.
        self.isMoving = True
        key = [TARGET_ACTION_POP, self.sceneName, self.nodeName, "active"]
        self.u.set(key, "1")

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Target(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

