
import pymjin2

LIFT_CONTROL_BUTTON_POSTFIX_DOWN = "Down"
LIFT_CONTROL_BUTTON_POSTFIX_UP   = "Up"

LIFT_CONTROL_CRANE_NAME          = "crane_base"

LIFT_CONTROL_SIGNAL_MATERIAL_OFF = "control_signal_off"
LIFT_CONTROL_SIGNAL_MATERIAL_ON  = "control_signal_on"
LIFT_CONTROL_SIGNAL_POSTFIX      = "Signal"

class LiftControlState(object):
    def __init__(self):
        self.up     = None
        self.down   = None
        self.signal = None

class LiftControlImpl(object):
    def __init__(self, scene, senv):
        # Refer.
        self.scene = scene
        self.senv  = senv
        # Create.
        self.cs = LiftControlState()
    def __del__(self):
        # Derefer.
        self.scene = None
        self.senv  = None
    def enableButtons(self, sceneName):
        st = pymjin2.State()
        buttons = [self.cs.up, self.cs.down]
        for b in buttons:
            key = "button.{0}.{1}.selectable".format(sceneName, b)
            st.set(key, "1")
        self.senv.setState(st)
    def onButtonPress(self, sceneName, nodeName):
        craneStepD = 0
        if (nodeName == self.cs.down):
            craneStepD = 1
        elif (nodeName == self.cs.up):
            craneStepD = -1
        if (craneStepD):
            st = pymjin2.State()
            key = "crane.{0}.{1}.stepdd".format(sceneName, LIFT_CONTROL_CRANE_NAME)
            st.set(key, str(craneStepD))
            self.senv.setState(st)
    def onCraneMotion(self, sceneName, state):
        mat = LIFT_CONTROL_SIGNAL_MATERIAL_OFF
        if (state):
            mat = LIFT_CONTROL_SIGNAL_MATERIAL_ON
        key = "node.{0}.{1}.material".format(sceneName, self.cs.signal)
        st = pymjin2.State()
        st.set(key, mat)
        self.scene.setState(st)
    def resolveButtons(self, sceneName, nodeName):
        key = "node.{0}.{1}.children".format(sceneName, nodeName)
        st = self.scene.state([key])
        if (not len(st.keys)):
            print "Could not resolve buttons"
            return
        children = st.value(key)
        for c in children:
            if (c.endswith(LIFT_CONTROL_BUTTON_POSTFIX_DOWN)):
                self.cs.down = c
            elif (c.endswith(LIFT_CONTROL_BUTTON_POSTFIX_UP)):
                self.cs.up = c
            elif (c.endswith(LIFT_CONTROL_SIGNAL_POSTFIX)):
                self.cs.signal = c

class LiftControlListenerScriptEnvironment(pymjin2.ComponentListener):
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
            if (type == "button"):
                if (value == "1"):
                    self.impl.onButtonPress(sceneName, nodeName)
            elif (type == "crane"):
                self.impl.onCraneMotion(sceneName, value == "1")

class LiftControl:
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
        self.impl         = LiftControlImpl(scene, scriptEnvironment)
        self.listenerSEnv = LiftControlListenerScriptEnvironment(self.impl)
        # Prepare.
        self.impl.resolveButtons(sceneName, nodeName)
        self.impl.enableButtons(sceneName)
        # Listen to buttons' down state.
        keys = []
        buttons = [self.impl.cs.up,
                   self.impl.cs.down]
        for b in buttons:
            key = "button.{0}.{1}.selected".format(sceneName, b)
            keys.append(key)
        # Listen to crane motion.
        key = "crane.{0}.{1}.moving".format(sceneName, LIFT_CONTROL_CRANE_NAME)
        keys.append(key)
        self.senv.addListener(keys, self.listenerSEnv)
        print "{0} LiftControl.__init__".format(id(self))
    def __del__(self):
        # Tear down.
        self.senv.removeListener(self.listenerSEnv)
        # Destroy.
        del self.listenerSEnv
        del self.impl
        # Derefer.
        self.senv = None
        print "{0} LiftControl.__del__".format(id(self))

def SCRIPT_CREATE(sceneName,
                  nodeName,
                  scene,
                  action,
                  scriptEnvironment,
                  dependencies):
    return LiftControl(sceneName,
                       nodeName,
                       scene,
                       action,
                       scriptEnvironment,
                       dependencies)

def SCRIPT_DEPENDENCIES():
    return []

def SCRIPT_DESTROY(instance):
    del instance
