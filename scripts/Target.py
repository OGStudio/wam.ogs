
import pymjin2

TARGET_ACTION_GROUP     = "default"
TARGET_ACTION_TYPE_WAIT = "delay"
TARGET_ACTION_TYPE_POP  = "sequence"
TARGET_ACTION_NAME_WAIT = "waitForLeverage"
TARGET_ACTION_NAME_POP  = "popTarget"

class TargetState(object):
    def __init__(self):
        self.wait   = None
        self.pop    = None
        self.moving = False
    def setActionGroup(self, groupName):
        self.wait = "{0}.{1}.{2}".format(TARGET_ACTION_TYPE_WAIT,
                                         groupName,
                                         TARGET_ACTION_NAME_WAIT)
        self.pop = "{0}.{1}.{2}".format(TARGET_ACTION_TYPE_POP,
                                        groupName,
                                        TARGET_ACTION_NAME_POP)

class TargetImpl(object):
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
        # Ignore other actions.
        actionName = key.replace(".active", "")
        if (actionName not in self.actions):
            return
        node = self.actions[actionName]
        s = self.selectable[node]
        if (actionName == s.pop):
            # Ignore activation.
            if (state):
                return
            s.moving = False
            self.report(node, "moving", "0")
        elif (actionName == s.wait):
            self.report(node, "catch", values[0])
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
        s = self.selectable[node]
        # Ignore non-moving.
        if (not s.moving):
            return
        self.report(node, "selected", "1")
        self.report(node, "selected", "0")
    def report(self, node, property, value):
        st = pymjin2.State()
        key = "target.{0}.{1}".format(node, property)
        st.set(key, value)
        self.senv.reportStateChange(st)
    def setCatch(self, key, values):
        print "setCatch", key, values
    def setMoving(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        node = sceneName + "." + nodeName
        if (node not in self.selectable):
            return
        s = self.selectable[node]
        s.moving = True
        st = pymjin2.State()
        st.set("{0}.node".format(s.pop), node)
        st.set("{0}.active".format(s.pop), "1")
        self.action.setState(st)
    def setSelectable(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        state     = (values[0] == "1")
        node = sceneName + "." + nodeName
        if (state):
            # Clone sequence action and its children.
            key = "{0}.{1}.{2}.clone".format(TARGET_ACTION_TYPE_POP,
                                             TARGET_ACTION_GROUP,
                                             TARGET_ACTION_NAME_POP)
            st = self.action.state([key])
            newGroupName = st.value(key)[0]
            s = TargetState()
            s.setActionGroup(newGroupName)
            self.selectable[node] = s
            self.actions[s.wait] = node
            self.actions[s.pop]  = node
        # Remove disabled.
        elif (node in self.selectable):
            s = self.selectable[node]
            del self.actions[s.wait]
            del self.actions[s.pop]
            del self.selectable[node]
    def setSelected(self, key, values):
        print "setSelected", key, values

class Target:
    def __init__(self, scene, action, scriptEnvironment):
        # Create.
        self.impl = TargetImpl(scene, action, scriptEnvironment)
        self.subs = pymjin2.Subscriber()
        self.prov = pymjin2.Provider(scriptEnvironment,
                                     "Target",
                                     "Turn any node into WAM target")
        # Prepare.
        # Listen to node selection.
        key = "selector..selectedNode"
        self.subs.subscribe(scene, key, self.impl, "onSelection")
        # Listen to target pop state.
        key = "{0}..{1}.active".format(TARGET_ACTION_TYPE_POP,
                                       TARGET_ACTION_NAME_POP)
        self.subs.subscribe(action, key, self.impl, "onActionState")
        # Listen to target delay state.
        key = "{0}..{1}.active".format(TARGET_ACTION_TYPE_WAIT,
                                       TARGET_ACTION_NAME_WAIT)
        self.subs.subscribe(action, key, self.impl, "onActionState")
        # Provide "Target" API.
        self.prov.provide("target...catch",      self.impl, "setCatch")
        self.prov.provide("target...moving",     self.impl, "setMoving")
        self.prov.provide("target...selectable", self.impl, "setSelectable")
        self.prov.provide("target...selected",   self.impl, "setSelected")
        print "{0} Target.__init__".format(id(self))
    def __del__(self):
        # Destroy.
        del self.subs
        del self.prov
        del self.impl
        print "{0} Target.__del__".format(id(self))

