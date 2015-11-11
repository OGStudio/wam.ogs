
import pymjin2

SINGLE_LEVERAGE_ACTION_CATCH = "sequence.default.catchTarget"
SINGLE_LEVERAGE_ACTION_DOWN  = "rotate.default.lowerLeverage"

class SingleLeverageImpl(object):
    def __init__(self, user):
        # Refer.
        self.u = user
    def __del__(self):
        # Derefer.
        self.u = None
    def onCatchFinished(self, key, value):
        self.u.set(self.property("moving"), "0")
    def onDownFinished(self, key, value):
        self.u.set(self.property("hit"), "1")
        self.u.set(self.property("hit"), "0")
    def property(self, name):
        return "leverage.$SCENE.$NODE." + name
    def setMoving(self, key, value):
        self.u.set("$CATCH.$SCENE.$NODE.active", "1")

class SingleLeverage:
    def __init__(self, sceneName, nodeName, env):
        # Refer.
        self.env = env
        # Create.
        self.u = EnvironmentUser("SingleLeverage/" + nodeName,
                                 "Turn specific node into WAM leverage")
        self.impl = SingleLeverageImpl(self.u)
        # Prepare.
        # Constants.
        self.u.d["SCENE"] = sceneName
        self.u.d["NODE"]  = nodeName
        self.u.d["CATCH"] = SINGLE_LEVERAGE_ACTION_CATCH
        self.u.d["DOWN"]  = SINGLE_LEVERAGE_ACTION_DOWN
        # Leverage API.
        self.u.provide(self.impl.property("hit"))
        self.u.provide(self.impl.property("moving"), self.impl.setMoving)
        # Listen to catch action finish.
        self.u.listen("$CATCH.$SCENE.$NODE.active",
                      "0",
                      self.impl.onCatchFinished)
        # Listen to down action finish.
        self.u.listen("$DOWN.$SCENE.$NODE.active",
                      "0",
                      self.impl.onDownFinished)
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
    return SingleLeverage(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

