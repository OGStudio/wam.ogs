
import pymjin2

MAIN_DEPENDENCY_BUTTON   = "scripts/Button.py"
MAIN_DEPENDENCY_CRANE    = "scripts/Crane.py"
MAIN_DEPENDENCY_EXCHANGE = "scripts/Exchange.py"
MAIN_DEPENDENCY_LINE     = "scripts/Line.py"
                        
# WARNING: Duplicates Control.py.
MAIN_CRANE_NAME          = "crane_base"
MAIN_CRANE_PISTON_NAME   = "crane_arms_piston"
MAIN_EXCHANGE_NAMES      = ["exchange11",
                            "exchange12",
                            "exchange21",
                            "exchange22",
                            "exchange31",
                            "exchange32"]
# WARNING: Duplicates LineControl.py.
MAIN_EXCHANGE_LINES      = ["lineBelt1", "lineBelt2", "lineBelt3"]
MAIN_EXCHANGE_SUBJECT    = "subject"

class MainImpl(object):
    def __init__(self, scene, senv):
        # Refer.
        self.scene = scene
        self.senv  = senv
    def __del__(self):
        # Derefer.
        self.scene = None
        self.senv  = None
    def onCraneLow(self, sceneName):
        print "onCraneLow", sceneName
        # Get crane piston X and Y values.
        key = "node.{0}.{1}.positionAbs".format(sceneName,
                                                MAIN_CRANE_PISTON_NAME)
        st = self.scene.state([key])
        pos = st.value(key)[0].split(" ")
        # Locate exchange instance.
        st = pymjin2.State()
        key = "exchangeLocator.{0}.position".format(sceneName)
        value = "{0} {1}".format(pos[0], pos[1])
        st.set(key, value)
        self.senv.setState(st)
    def onLocatedExchange(self, sceneName, exchange):
        st = pymjin2.State()
        key = "exchange.{0}.{1}.exchange".format(sceneName, exchange)
        st.set(key, "1")
        self.senv.setState(st)

class MainListenerScriptEnvironment(pymjin2.ComponentListener):
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
            value     = st.value(k)[0]
            if ((type == "crane") and
                (value == "1")):
                self.impl.onCraneLow(sceneName)
            elif ((type == "exchangeLocator") and
                  len(value)):
                self.impl.onLocatedExchange(sceneName, value)

class Main:
    def __init__(self,
                 sceneName,
                 nodeName,
                 scene,
                 action,
                 scriptEnvironment,
                 dependencies):
        # Refer.
        self.sceneName    = sceneName
        self.scene        = scene
        self.action       = action
        self.senv         = scriptEnvironment
        self.dependencies = dependencies
        # Create.
        moduleB = self.dependencies[MAIN_DEPENDENCY_BUTTON]
        self.button = moduleB.Button(scene, action, scriptEnvironment)
        moduleC = self.dependencies[MAIN_DEPENDENCY_CRANE]
        self.crane = moduleC.Crane(scene, action, scriptEnvironment)
        moduleE = self.dependencies[MAIN_DEPENDENCY_EXCHANGE]
        self.exchange = moduleE.Exchange(scene, action, scriptEnvironment)
        moduleL = self.dependencies[MAIN_DEPENDENCY_LINE]
        self.line = moduleL.Line(scene, action, scriptEnvironment)
        self.impl = MainImpl(self.scene, self.senv)
        self.listenerSEnv = MainListenerScriptEnvironment(self.impl)
        # Prepare.
        # Enable exchange points and set their subject.
        st = pymjin2.State()
        for name in MAIN_EXCHANGE_NAMES:
            prefix = "exchange.{0}.{1}".format(sceneName, name)
            key = "{0}.enabled".format(prefix)
            st.set(key, "1")
            key = "{0}.subject".format(prefix)
            st.set(key, MAIN_EXCHANGE_SUBJECT)
            key = "{0}.owner".format(prefix)
            st.add(key, MAIN_CRANE_PISTON_NAME)
            if (name.endswith("11") or
                name.endswith("12")):
                st.add(key, MAIN_EXCHANGE_LINES[0])
            elif (name.endswith("21") or
                name.endswith("22")):
                st.add(key, MAIN_EXCHANGE_LINES[1])
            elif (name.endswith("31") or
                name.endswith("32")):
                st.add(key, MAIN_EXCHANGE_LINES[2])
        self.senv.setState(st)
        keys = [
            # Listen to crane lowering.
            "crane.{0}.{1}.stepd".format(sceneName, MAIN_CRANE_NAME),
            # Listen to exchange location.
            "exchangeLocator.{0}.locatedExchange".format(sceneName)
            ]
        self.senv.addListener(keys, self.listenerSEnv)
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.senv.removeListener(self.listenerSEnv)
        # Derefer.
        self.scene        = None
        self.action       = None
        self.senv         = None
        self.dependencies = None
        # Destroy
        del self.button
        del self.crane
        del self.exchange
        del self.line
        del self.listenerSEnv
        del self.impl
        print "{0} Main.__del__".format(id(self))

def SCRIPT_CREATE(sceneName,
                  nodeName,
                  scene,
                  action,
                  scriptEnvironment,
                  dependencies):
    return Main(sceneName,
                nodeName,
                scene,
                action,
                scriptEnvironment,
                dependencies)

def SCRIPT_DEPENDENCIES():
    return [MAIN_DEPENDENCY_BUTTON,
            MAIN_DEPENDENCY_CRANE,
            MAIN_DEPENDENCY_EXCHANGE,
            MAIN_DEPENDENCY_LINE]

def SCRIPT_DESTROY(instance):
    del instance

