
import pymjin2

#Target_ACTION_GROUP      = "default"
#Target_ACTION_DOWN_TYPE  = "moveBy"
#Target_ACTION_DOWN_NAME  = "moveButtonDown"
#Target_ACTION_PRESS_TYPE = "sequence"
#Target_ACTION_PRESS_NAME = "pressButton"

class TargetState(object):
    def __init__(self):
        self.up   = None
        self.down = None
#        self.press = None
#    def setActionGroup(self, groupName):
#        self.down = "{0}.{1}.{2}".format(Target_ACTION_DOWN_TYPE,
#                                         groupName,
#                                         Target_ACTION_DOWN_NAME)
#        self.press = "{0}.{1}.{2}".format(Target_ACTION_PRESS_TYPE,
#                                          groupName,
#                                          Target_ACTION_PRESS_NAME)

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
#        key = "Target.{0}.selected".format(self.actions[actionName])
#        st.set(key, "1")
#        self.senv.reportStateChange(st)
#        st.set(key, "0")
#        self.senv.reportStateChange(st)
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
        print "onSelection", nodeName
        s = self.selectable[node]
#        st = pymjin2.State()
#        st.set("{0}.node".format(bs.press), node)
#        st.set("{0}.active".format(bs.press), "1")
#        self.action.setState(st)
    def setSelectable(self, key, values):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        state     = (values[0] == "1")
        node = sceneName + "." + nodeName
        if (state):
#            key = "{0}.{1}.{2}.clone".format(Target_ACTION_PRESS_TYPE,
#                                             Target_ACTION_GROUP,
#                                             Target_ACTION_PRESS_NAME)
#            st = self.action.state([key])
#            newGroupName = st.value(key)[0]
            s = TargetState()
            self.selectable[node] = s
            #s.setActionGroup(newGroupName)
            #self.actions[bs.down] = node
        # Remove disabled.
        elif (node in self.selectable):
            s = self.selectable[node]
            #del self.actions[bs.down]
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
        # Listen to Target down state.
#        key = "{0}..{1}.active".format(Target_ACTION_DOWN_TYPE,
#                                       Target_ACTION_DOWN_NAME)
#        self.subs.subscribe(action, key, self.impl, "onActionState")
        # Provide "Target" API.
        self.prov.provide("target...selectable", self.impl, "setSelectable")
        self.prov.provide("target...selected",   self.impl, "setSelected")
        print "{0} Target.__init__".format(id(self))
    def __del__(self):
        # Destroy.
        del self.subs
        del self.prov
        del self.impl
        print "{0} Target.__del__".format(id(self))

