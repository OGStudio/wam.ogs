
import pymjin2

#Leverage_ACTION_GROUP      = "default"
#Leverage_ACTION_DOWN_TYPE  = "moveBy"
#Leverage_ACTION_DOWN_NAME  = "moveButtonDown"
#Leverage_ACTION_PRESS_TYPE = "sequence"
#Leverage_ACTION_PRESS_NAME = "pressButton"

class LeverageState(object):
    def __init__(self):
        self.up   = None
        self.down = None
#        self.press = None
#    def setActionGroup(self, groupName):
#        self.down = "{0}.{1}.{2}".format(Leverage_ACTION_DOWN_TYPE,
#                                         groupName,
#                                         Leverage_ACTION_DOWN_NAME)
#        self.press = "{0}.{1}.{2}".format(Leverage_ACTION_PRESS_TYPE,
#                                          groupName,
#                                          Leverage_ACTION_PRESS_NAME)

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
#    def onActionState(self, key, values):
#        state = (values[0] == "1")
#        # Ignore activation.
#        if (state):
#            return
#        # Ignore other actions.
#        actionName = key.replace(".active", "")
#        if (actionName not in self.actions):
#            return
#        # Report.
#        st = pymjin2.State()
#        key = "Leverage.{0}.selected".format(self.actions[actionName])
#        st.set(key, "1")
#        self.senv.reportStateChange(st)
#        st.set(key, "0")
#        self.senv.reportStateChange(st)
#    def onSelection(self, key, values):
#        nodeName = values[0]
#        # Ignore deselection.
#        if (not len(nodeName)):
#            return
#        v = key.split(".")
#        sceneName = v[1]
#        node = sceneName + "." + nodeName
#        if (node not in self.selectable):
#            return
#        print "onSelection", nodeName
#        s = self.selectable[node]
#        st = pymjin2.State()
#        st.set("{0}.node".format(bs.press), node)
#        st.set("{0}.active".format(bs.press), "1")
#        self.action.setState(st)
    def setMovable(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        state     = (values[0] == "1")
        node = sceneName + "." + nodeName
        print "setMovable", state
        if (state):
#            key = "{0}.{1}.{2}.clone".format(Leverage_ACTION_PRESS_TYPE,
#                                             Leverage_ACTION_GROUP,
#                                             Leverage_ACTION_PRESS_NAME)
#            st = self.action.state([key])
#            newGroupName = st.value(key)[0]
            s = LeverageState()
            self.movable[node] = s
            #s.setActionGroup(newGroupName)
            #self.actions[bs.down] = node
        # Remove disabled.
        elif (node in self.movable):
            s = self.movable[node]
            #del self.actions[bs.down]
            del self.movable[node]
    def setMoving(self, key, values):
        print "setMoving", key, values

class Leverage:
    def __init__(self, scene, action, scriptEnvironment):
        # Create.
        self.impl = LeverageImpl(scene, action, scriptEnvironment)
        self.subs = pymjin2.Subscriber()
        self.prov = pymjin2.Provider(scriptEnvironment,
                                     "Leverage",
                                     "Turn any node into WAM Leverage")
        # Prepare.
        # Listen to node selection.
#        key = "selector..selectedNode"
#        self.subs.subscribe(scene, key, self.impl, "onSelection")
        # Listen to Leverage down state.
#        key = "{0}..{1}.active".format(Leverage_ACTION_DOWN_TYPE,
#                                       Leverage_ACTION_DOWN_NAME)
#        self.subs.subscribe(action, key, self.impl, "onActionState")
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

