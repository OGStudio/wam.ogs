
import pymjin2

TARGET_ACTION_POP  = "sequence.default.popTarget"
TARGET_ACTION_WAIT = "delay.default.waitForLeverage"

class TargetImpl(object):
    def __init__(self, env):
        # Refer.
        self.env = env
        # Create.
        self.selectable = {}
        self.actions    = {}
    def __del__(self):
        # Derefer.
        self.env = None
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

        sequence.default.popTarget.default.target1.active = 1

        sequence.default.popTarget = { "default.target1" : { "active" : "1" }
                
                
                "active" : "1",
                                         "node" : "default.target1",
        .active = 1

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

class Target:
    def __init__(self, node, env, deps):
        # Refer.
        self.env = env
        # Create.
        self.impl = TargetImpl(env)
        self.proxy = EnvironmentProxy("Target", "Turn any node into WAM target")
        #                   Key.                             Class.     Method.
        self.proxy.listen("selector..selectedNode",        self.impl, "onSelection")
        self.proxy.listen(TARGET_ACTION_POP, 
        self.proxy.listen("..active".format(TARGET_ACTION_POP),    self.impl, "onActionTarget")
        self.proxy.listen("delay..waitForLeverage.active", self.impl, "onActionWait")
#        self.proxy.listen(self.impl,
#                          { "selector..selectedNode" : "onSelection",
#                        "sequence..popTarget.active" : "onTargetPop",
#                     "delay..waitForLeverage.active" : "onLeverageWait" })
        #                  Key.                   Class.     Set method.      Get method.
        self.proxy.provide("target...catch",      None,      None,            None)
        self.proxy.provide("target...moving",     self.impl, "setMoving",     None)
        self.proxy.provide("target...selectable", self.impl, "setSelectable", None)
        self.proxy.provide("target...selected",   self.impl, None,            None)
        # Prepare.
        self.env.registerProxy(self.proxy)
    def __del__(self):
        # Tear down.
        self.env.deregisterProxy(self.proxy)
        # Destroy.
        del self.proxy
        del self.impl
        # Derefer.
        self.env = None

def SCRIPT_CREATE(node, env, deps):
    return Target(node, env, deps)

def SCRIPT_DEPENDENCIES():
    return []

def SCRIPT_DESTROY(instance):
    del instance
