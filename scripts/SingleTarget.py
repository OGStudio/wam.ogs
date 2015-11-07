
import pymjin2

TARGET_ACTION_POP  = "sequence.default.popTarget"
TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class Target:
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env = env
        # Create.
        self.u = EnvironmentUser("Target", "Turn specific node into WAM target")
        self.isMoving = False
        # Listen to node selection.
        key = ["selector", sceneName, "selectedNode"]
        self.u.listen(key, nodeName, self, "onSelection")
        # Listen to pop action finish.
        key = [TARGET_ACTION_POP, sceneName, nodeName, "active"]
        self.u.listen(key, "0", self, "onPopFinished")
        # Listen to wait action.
        key = [TARGET_ACTION_WAIT, sceneName, nodeName, "active"]
        self.u.listen(key, None, self, "onWait")
        # Provide "catch" ability.
        key = ["target", sceneName, nodeName, "catch"]
        # Since no class and methods are specified, this property is only reported.
        self.u.provide(key)
        # Provide "moving" ability. Only setter.
        key = ["target", sceneName, nodeName, "moving"]
        self.u.provide(key, self, "setMoving")
        # Provide "selected" ability. Only reporting.
        key = ["target", sceneName, nodeName, "selected"]
        self.u.provide(key)
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
        key = ["target", sceneName, nodeName, "moving"]
        self.u.set(key, "0")
    def onSelection(self, key, value):
        # Ignore non-moving.
        if (not self.isMoving):
            return
        sceneName = key[1]
        nodeName  = value[0]
        key = ["target", sceneName, nodeName, "selected"]
        self.u.set(key, "1")
        self.u.set(key, "0")
    def onWait(self, key, value):
        key = ["target", sceneName, nodeName, "catch"]
        self.u.set(key, value[0])
    def setMoving(self, key, value):
        sceneName = key[1]
        nodeName  = key[2]
        # Assume setMoving is only called with value = 1.
        self.isMoving = True
        key = [TARGET_ACTION_POP, sceneName, nodeName, "active"]
        self.u.set(key, "1")

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Target(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance
