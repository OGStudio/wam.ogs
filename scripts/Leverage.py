
import pymjin2

LEVERAGE_ACTION_GROUP      = "default"
LEVERAGE_ACTION_TYPE_UP    = "rotateBy"
LEVERAGE_ACTION_TYPE_CATCH = "sequence"
LEVERAGE_ACTION_NAME_UP    = "liftLeverage"
LEVERAGE_ACTION_NAME_CATCH = "catchTarget"

class LeverageState(object):
    def __init__(self):
        self.up     = None
        self.catch  = None
        self.moving = None
    def setActionGroup(self, groupName):
        self.up = "{0}.{1}.{2}".format(LEVERAGE_ACTION_TYPE_UP,
                                       groupName,
                                       LEVERAGE_ACTION_NAME_UP)
        self.catch = "{0}.{1}.{2}".format(LEVERAGE_ACTION_TYPE_CATCH,
                                          groupName,
                                          LEVERAGE_ACTION_NAME_CATCH)

class LeverageImpl(object):
    def __init__(self, scene, action, senv):
        # Refer.
        self.scene  = scene
        self.action = action
        self.senv   = senv
        # Create.
        self.movable = {}
        self.actions = {}
    def __del__(self):
        # Derefer.
        self.scene  = None
        self.action = None
        self.senv   = None
    def onActionState(self, key, values):
        state = (values[0] == "1")
        # Ignore activation.
        if (state):
            return
        # Ignore other actions.
        actionName = key.replace(".active", "")
        if (actionName not in self.actions):
            return
        node = self.actions[actionName]
        s = self.movable[node]
        s.moving = False
        self.report(node, "moving", "0")
    def report(self, node, property, value):
        st = pymjin2.State()
        key = "leverage.{0}.{1}".format(node, property)
        st.set(key, value)
        self.senv.reportStateChange(st)
    def setMovable(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        state     = (values[0] == "1")
        node = sceneName + "." + nodeName
        if (state):
            # Clone sequence action and its children.
            key = "{0}.{1}.{2}.clone".format(LEVERAGE_ACTION_TYPE_CATCH,
                                             LEVERAGE_ACTION_GROUP,
                                             LEVERAGE_ACTION_NAME_CATCH)
            st = self.action.state([key])
            newGroupName = st.value(key)[0]
            s = LeverageState()
            s.setActionGroup(newGroupName)
            self.movable[node] = s
            self.actions[s.up]    = node
            self.actions[s.catch] = node
        # Remove disabled.
        elif (node in self.movable):
            s = self.movable[node]
            del self.actions[s.up]
            del self.actions[s.catch]
            del self.movable[node]
    def setMoving(self, key, values):
        print "setMoving", key, values
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        node = sceneName + "." + nodeName
        if (node not in self.movable):
            return
        s = self.movable[node]
        s.moving = True
        st = pymjin2.State()
        st.set("{0}.node".format(s.catch), node)
        st.set("{0}.active".format(s.catch), "1")
        self.action.setState(st)

class Leverage:
    def __init__(self, scene, action, scriptEnvironment):
        # Create.
        self.impl = LeverageImpl(scene, action, scriptEnvironment)
        self.subs = pymjin2.Subscriber()
        self.prov = pymjin2.Provider(scriptEnvironment,
                                     "Leverage",
                                     "Turn any node into WAM Leverage")
        # Prepare.
        # Listen to leverage state.
        key = "{0}..{1}.active".format(LEVERAGE_ACTION_TYPE_CATCH,
                                       LEVERAGE_ACTION_NAME_CATCH)
        self.subs.subscribe(action, key, self.impl, "onActionState")
        # Provide "Leverage" API.
        self.prov.provide("leverage...movable", self.impl, "setMovable")
        self.prov.provide("leverage...moving",  self.impl, "setMoving")
        print "{0} Leverage.__init__".format(id(self))
    def __del__(self):
        # Destroy.
        del self.subs
        del self.prov
        del self.impl
        print "{0} Leverage.__del__".format(id(self))

