
import pymjin2

LINE_ACTION_GROUP      = "default"
LINE_ACTION_TYPE       = "moveBy"
LINE_ACTION_LEFT_NAME  = "moveBeltLeft"
LINE_ACTION_RIGHT_NAME = "moveBeltRight"
LINE_DEFAULT_STEP      = 0
LINE_STEPS             = 3

class LineState(object):
    def __init__(self):
        self.left     = None
        self.right    = None
        self.step     = LINE_DEFAULT_STEP
        self.isMoving = False
    def validateNewStep(self, value):
        newStep = self.step + value
        ok = (newStep >= 0) and (newStep < LINE_STEPS)
        if (ok):
            self.step = newStep
        return ok

class LineImpl(object):
    def __init__(self, scene, action, senv):
        # Refer.
        self.scene  = scene
        self.action = action
        self.senv   = senv
        # Create.
        self.enabled = {}
        self.actions = {}
    def __del__(self):
        # Derefer.
        self.scene  = None
        self.action = None
        self.senv   = None
    def cloneAction(self, actionName):
        key = "{0}.{1}.{2}.clone".format(LINE_ACTION_TYPE,
                                         LINE_ACTION_GROUP,
                                         actionName)
        st = self.action.state([key])
        newGroupName = st.value(key)[0]
        return "{0}.{1}.{2}".format(LINE_ACTION_TYPE,
                                    newGroupName,
                                    actionName)
    def onActionState(self, actionName, state):
        # Ignore activation.
        if (state):
            return
        # Ignore other actions.
        if (actionName not in self.actions):
            return
        # Report.
        node = self.actions[actionName]
        ls = self.enabled[node]
        ls.isMoving = False
        self.reportMoving(node, "0")
    def reportMoving(self, node, value):
        st = pymjin2.State()
        key = "line.{0}.moving".format(node)
        st.set(key, value)
        self.senv.reportStateChange(st)
    def setEnabled(self, sceneName, nodeName, state):
        node = sceneName + "." + nodeName
        if (state):
            ls = LineState()
            self.enabled[node] = ls
            # Clone actions.
            ls.left  = self.cloneAction(LINE_ACTION_LEFT_NAME)
            ls.right = self.cloneAction(LINE_ACTION_RIGHT_NAME)
            self.actions[ls.left]  = node
            self.actions[ls.right] = node
            # Resolve actions' node.
            st = pymjin2.State()
            st.set("{0}.node".format(ls.left),  node)
            st.set("{0}.node".format(ls.right), node)
            self.action.setState(st)
        # Remove disabled.
        elif (node in self.enabled):
            ls = self.enabled[node]
            del self.actions[ls.left]
            del self.actions[ls.right]
            del self.enabled[node]
    def setStepD(self, sceneName, nodeName, value):
        node = sceneName + "." + nodeName
        ls = self.enabled[node]
        if (ls.isMoving):
            return
        if (not ls.validateNewStep(value)):
            return
        ls.isMoving = True
        # Start the action.
        st = pymjin2.State()
        key = "{0}.active".format(ls.left if value < 0 else ls.right)
        st.set(key, "1")
        self.action.setState(st)
        self.reportMoving(node, "1")

class LineListenerAction(pymjin2.ComponentListener):
    def __init__(self, impl):
        pymjin2.ComponentListener.__init__(self)
        # Refer.
        self.impl = impl
    def __del__(self):
        # Derefer.
        self.impl = None
    def onComponentStateChange(self, st):
        for k in st.keys:
            actionName = k.replace(".active", "")
            state = (st.value(k)[0] == "1")
            self.impl.onActionState(actionName, state)

class LineExtensionScriptEnvironment(pymjin2.Extension):
    def __init__(self, impl):
        pymjin2.Extension.__init__(self)
        # Refer.
        self.impl = impl
    def deinit(self):
        # Derefer.
        self.impl = None
        print "LineExt.deinit"
    def description(self):
        return "Turn any node into a simple line"
    def keys(self):
        return ["line...enabled",
                "line...moving",
                "line...stepd"]
    def name(self):
        return "LineExtensionScriptEnvironment"
    def set(self, key, value):
        v = key.split(".")
        sceneName = v[1]
        nodeName  = v[2]
        property  = v[3]
        if (property == "enabled"):
            self.impl.setEnabled(sceneName, nodeName, value == "1")
        elif (property == "stepd"):
            self.impl.setStepD(sceneName, nodeName, int(value))

class Line:
    def __init__(self, scene, action, scriptEnvironment):
        # Refer.
        self.scene  = scene
        self.action = action
        self.senv   = scriptEnvironment
        # Create.
        self.impl              = LineImpl(scene, action, scriptEnvironment)
        self.listenerAction    = LineListenerAction(self.impl)
        self.extension         = LineExtensionScriptEnvironment(self.impl)
        # Prepare.
        # Listen to line motion.
        keys = ["{0}..{1}.active".format(LINE_ACTION_TYPE,
                                         LINE_ACTION_LEFT_NAME),
                "{0}..{1}.active".format(LINE_ACTION_TYPE,
                                         LINE_ACTION_RIGHT_NAME)]
        self.action.addListener(keys, self.listenerAction)
        self.senv.addExtension(self.extension)
        print "{0} Line.__init__".format(id(self))
    def __del__(self):
        # Tear down.
        self.action.removeListener(self.listenerAction)
        self.senv.removeExtension(self.extension)
        # Destroy.
        del self.listenerAction
        del self.extension
        del self.impl
        # Derefer.
        self.scene  = None
        self.action = None
        self.senv   = None
        print "{0} Line.__del__".format(id(self))

