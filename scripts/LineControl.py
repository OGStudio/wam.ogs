
import pymjin2

LINE_CONTROL_BUTTON_POSTFIX_DOWN  = "Down"
LINE_CONTROL_BUTTON_POSTFIX_LEFT  = "Left"
LINE_CONTROL_BUTTON_POSTFIX_RIGHT = "Right"
LINE_CONTROL_BUTTON_POSTFIX_UP    = "Up"

LINE_CONTROL_DEFAULT_LINE_ID      = 0
LINE_CONTROL_LINES                = ["lineBelt1", "lineBelt2", "lineBelt3"]

LINE_CONTROL_LIGHTS               = ["lineLight1", "lineLight2", "lineLight3"]
LINE_CONTROL_LIGHT_MATERIAL_ON    = "line_segment_light_on"
LINE_CONTROL_LIGHT_MATERIAL_OFF   = "line_segment_light_off"

LINE_CONTROL_SIGNAL_MATERIAL_OFF  = "control_signal_off"
LINE_CONTROL_SIGNAL_MATERIAL_ON   = "control_signal_on"
LINE_CONTROL_SIGNAL_POSTFIX       = "Signal"

class LineControlImpl(object):
    def __init__(self, scene, senv):
        # Refer.
        self.scene = scene
        self.senv  = senv
        # Create.
        self.buttons  = {    "up" : None,
                           "down" : None,
                           "left" : None,
                          "right" : None }
        self.signal   = None
        self.lineID   = LINE_CONTROL_DEFAULT_LINE_ID
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.scene = None
        self.senv  = None
    def enableButtons(self, sceneName):
        st = pymjin2.State()
        for type, name in self.buttons.items():
            key = "button.{0}.{1}.selectable".format(sceneName, name)
            st.set(key, "1")
        self.senv.setState(st)
    def enableLines(self, sceneName):
        st = pymjin2.State()
        for name in LINE_CONTROL_LINES:
            key = "line.{0}.{1}.enabled".format(sceneName, name)
            st.set(key, "1")
        self.senv.setState(st)
    def onButtonPress(self, sceneName, nodeName):
        lineStep = 0
        lineID = 0
        if (nodeName == self.buttons["left"]):
            lineStep = -1
        elif (nodeName == self.buttons["right"]):
            lineStep = 1
        elif (nodeName == self.buttons["up"]):
            lineID = -1
        elif (nodeName == self.buttons["down"]):
            lineID = 1
        if (lineStep):
            st = pymjin2.State()
            lineName = LINE_CONTROL_LINES[self.lineID]
            key = "line.{0}.{1}.stepd".format(sceneName, lineName)
            st.set(key, str(lineStep))
            self.senv.setState(st)
        elif (lineID):
            self.setLineIDD(sceneName, lineID)
    def onLineMotion(self, sceneName, state):
        mat = LINE_CONTROL_SIGNAL_MATERIAL_OFF
        if (state):
            mat = LINE_CONTROL_SIGNAL_MATERIAL_ON
        key = "node.{0}.{1}.material".format(sceneName, self.signal)
        st = pymjin2.State()
        st.set(key, mat)
        self.scene.setState(st)
        self.isMoving = state
    def resolveButtons(self, sceneName, nodeName):
        key = "node.{0}.{1}.children".format(sceneName, nodeName)
        st = self.scene.state([key])
        if (not len(st.keys)):
            print "Could not resolve buttons"
            return
        children = st.value(key)
        for c in children:
            if (c.endswith(LINE_CONTROL_BUTTON_POSTFIX_DOWN)):
                self.buttons["down"] = c
            elif (c.endswith(LINE_CONTROL_BUTTON_POSTFIX_LEFT)):
                self.buttons["left"] = c
            elif (c.endswith(LINE_CONTROL_BUTTON_POSTFIX_RIGHT)):
                self.buttons["right"] = c
            elif (c.endswith(LINE_CONTROL_BUTTON_POSTFIX_UP)):
                self.buttons["up"] = c
            elif (c.endswith(LINE_CONTROL_SIGNAL_POSTFIX)):
                self.signal = c
    def setLineIDD(self, sceneName, value):
        if (self.isMoving):
            return
        oldID = self.lineID
        if (not self.validateNewLineID(value)):
            return
        self.setLineLightState(sceneName,
                               LINE_CONTROL_LIGHTS[oldID],
                               False)
        self.setLineLightState(sceneName,
                               LINE_CONTROL_LIGHTS[self.lineID],
                               True)
    def setLineLightState(self, sceneName, nodeName, state):
        key = "node.{0}.{1}.children".format(sceneName, nodeName)
        st = self.scene.state([key])
        mat = LINE_CONTROL_LIGHT_MATERIAL_OFF
        if (state):
            mat = LINE_CONTROL_LIGHT_MATERIAL_ON
        st2 = pymjin2.State()
        children = st.value(key)
        for c in children:
            key = "node.{0}.{1}.material".format(sceneName, c)
            st2.set(key, mat)
        self.scene.setState(st2)
    def validateNewLineID(self, value):
        newID = self.lineID + value
        ok = (newID >= 0) and (newID < len(LINE_CONTROL_LINES))
        if (ok):
            self.lineID = newID
        return ok

class LineControlListenerScriptEnvironment(pymjin2.ComponentListener):
    def __init__(self, impl):
        pymjin2.ComponentListener.__init__(self)
        # Refer.
        self.impl = impl
    def __del__(self):
        # Derefer.
        self.impl = None
    def onComponentStateChange(self, st):
        for k in st.keys:
            v = k.split(".")
            type      = v[0]
            sceneName = v[1]
            nodeName  = v[2]
            #property = v[3]
            value     = st.value(k)[0]
            if ((type == "button") and
                (value == "1")):
                self.impl.onButtonPress(sceneName, nodeName)
            elif (type == "line"):
                self.impl.onLineMotion(sceneName, value == "1")

class LineControl:
    def __init__(self,
                 sceneName,
                 nodeName,
                 scene,
                 action,
                 scriptEnvironment,
                 dependencies):
        # Refer.
        self.senv = scriptEnvironment
        # Create.
        self.impl         = LineControlImpl(scene, scriptEnvironment)
        self.listenerSEnv = LineControlListenerScriptEnvironment(self.impl)
        # Prepare.
        self.impl.resolveButtons(sceneName, nodeName)
        self.impl.enableButtons(sceneName)
        self.impl.enableLines(sceneName)
        # Listen to button presses.
        keys = []
        for type, name in self.impl.buttons.items():
            key = "button.{0}.{1}.selected".format(sceneName, name)
            keys.append(key)
        # Listen to line motion.
        for name in LINE_CONTROL_LINES:
            key = "line.{0}.{1}.moving".format(sceneName, name)
            keys.append(key)
        self.senv.addListener(keys, self.listenerSEnv)
        print "{0} LineControl.__init__".format(id(self))
    def __del__(self):
        # Tear down.
        self.senv.removeListener(self.listenerSEnv)
        # Destroy.
        del self.listenerSEnv
        del self.impl
        # Derefer.
        self.senv = None
        print "{0} LineControl.__del__".format(id(self))

def SCRIPT_CREATE(sceneName,
                  nodeName,
                  scene,
                  action,
                  scriptEnvironment,
                  dependencies):
    return LineControl(sceneName,
                   nodeName,
                   scene,
                   action,
                   scriptEnvironment,
                   dependencies)

def SCRIPT_DEPENDENCIES():
    return []

def SCRIPT_DESTROY(instance):
    del instance
