
import pymjin2

#Timer_ACTION_GROUP      = "default"
#Timer_ACTION_DOWN_TYPE  = "moveBy"
#Timer_ACTION_DOWN_NAME  = "moveTimerDown"
#Timer_ACTION_PRESS_TYPE = "sequence"
#Timer_ACTION_PRESS_NAME = "pressTimer"

class TimerState(object):
    def __init__(self):
        self.down  = None
        self.press = None
    def setActionGroup(self, groupName):
        self.down = "{0}.{1}.{2}".format(Timer_ACTION_DOWN_TYPE,
                                         groupName,
                                         Timer_ACTION_DOWN_NAME)
        self.press = "{0}.{1}.{2}".format(Timer_ACTION_PRESS_TYPE,
                                          groupName,
                                          Timer_ACTION_PRESS_NAME)

class TimerImpl(object):
    def __init__(self, scene, action, senv):
        # Refer.
        self.scene  = scene
        self.action = action
        self.senv   = senv
        # Create.
        self.selectable = {}
        self.actions    = {}
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
        # Report.
        st = pymjin2.State()
        key = "Timer.{0}.selected".format(self.actions[actionName])
        st.set(key, "1")
        self.senv.reportStateChange(st)
        st.set(key, "0")
        self.senv.reportStateChange(st)
    def onSelection(self, key, values):
        nodeName = values[0]
        # Ignore deselection.
        if (not len(nodeName)):
            return
        v = key.split(".")
        sceneName = v[1]
        node = sceneName + "." + nodeName
        if (node not in self.selectable):
            return
        bs = self.selectable[node]
        st = pymjin2.State()
        st.set("{0}.node".format(bs.press), node)
        st.set("{0}.active".format(bs.press), "1")
        self.action.setState(st)
    def setSelectable(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        state     = (values[0] == "1")
        node = sceneName + "." + nodeName
        if (state):
            key = "{0}.{1}.{2}.clone".format(Timer_ACTION_PRESS_TYPE,
                                             Timer_ACTION_GROUP,
                                             Timer_ACTION_PRESS_NAME)
            st = self.action.state([key])
            newGroupName = st.value(key)[0]
            bs = TimerState()
            self.selectable[node] = bs
            bs.setActionGroup(newGroupName)
            self.actions[bs.down] = node
        # Remove disabled.
        elif (node in self.selectable):
            bs = self.selectable[node]
            del self.actions[bs.down]
            del self.selectable[node]
    def setSelected(self, key, values):
        print "setSelected", key, values

class Timer:
    def __init__(self, scene, action, scriptEnvironment):
        # Create.
        self.impl = TimerImpl(scene, action, scriptEnvironment)
        self.subs = pymjin2.Subscriber()
        self.prov = pymjin2.Provider(scriptEnvironment,
                                     "Timer",
                                     "Turn any node into Timer")
        # Prepare.
        # Listen to node selection.
        key = "selector..selectedNode"
        self.subs.subscribe(scene, key, self.impl, "onSelection")
        # Listen to Timer down state.
        key = "{0}..{1}.active".format(Timer_ACTION_DOWN_TYPE,
                                       Timer_ACTION_DOWN_NAME)
        self.subs.subscribe(action, key, self.impl, "onActionState")
        # Provide "Timer" API.
        self.prov.provide("Timer...selectable", self.impl, "setSelectable")
        self.prov.provide("Timer...selected",   self.impl, "setSelected")
        print "{0} Timer.__init__".format(id(self))
    def __del__(self):
        # Destroy.
        del self.subs
        del self.prov
        del self.impl
        print "{0} Timer.__del__".format(id(self))

