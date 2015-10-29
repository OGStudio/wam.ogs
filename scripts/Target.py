
import pymjin2

TARGET_ACTION_GROUP    = "default"
TARGET_ACTION_TYPE_UP  = "moveBy"
TARGET_ACTION_TYPE_POP = "sequence"
TARGET_ACTION_NAME_UP  = "liftTarget"
TARGET_ACTION_NAME_POP = "popTarget"

class TargetState(object):
    def __init__(self):
        self.up  = None
        self.pop = None
    def setActionGroup(self, groupName):
        self.up = "{0}.{1}.{2}".format(TARGET_ACTION_TYPE_UP,
                                       groupName,
                                       TARGET_ACTION_NAME_UP)
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
        print "onActionState", key, values
        state = (values[0] == "1")
        # Ignore activation.
        if (state):
            return
        # Ignore other actions.
        actionName = key.replace(".active", "")
        if (actionName not in self.actions):
            return
        node = self.actions[actionName]
        self.report(node, "moving", "0")
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
        self.report(node, "selected", "1")
        self.report(node, "selected", "0")
    def report(self, node, property, value):
        st = pymjin2.State()
        key = "target.{0}.{1}".format(node, property)
        st.set(key, value)
        self.senv.reportStateChange(st)
    def setMoving(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        node = sceneName + "." + nodeName
        if (node not in self.selectable):
            return
        print "setMoving", node
        s = self.selectable[node]
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
            self.actions[s.up]  = node
            self.actions[s.pop] = node
        # Remove disabled.
        elif (node in self.selectable):
            s = self.selectable[node]
            del self.actions[s.up]
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
        # Provide "Target" API.
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

