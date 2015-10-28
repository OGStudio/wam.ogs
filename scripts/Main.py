
import pymjin2

#MAIN_DEPENDENCY_LEVERAGE = "scripts/Leverage.py"
MAIN_DEPENDENCY_TARGET   = "scripts/Target.py"
                        
MAIN_TARGETS = ["target1",
                "target2",
                "target3",
                "target4",
                "target5",
                "target6"]

class MainImpl(object):
    def __init__(self, scene, senv):
        # Refer.
        self.scene = scene
        self.senv  = senv
    def __del__(self):
        # Derefer.
        self.scene = None
        self.senv  = None

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
        #moduleB = self.dependencies[MAIN_DEPENDENCY_BUTTON]
        #self.button = moduleB.Button(scene, action, scriptEnvironment)
        self.impl = MainImpl(self.scene, self.senv)
        #self.listenerSEnv = MainListenerScriptEnvironment(self.impl)
        # Prepare.
        # Enable exchange points and set their subject.
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        #self.senv.removeListener(self.listenerSEnv)
        # Derefer.
        self.scene        = None
        self.action       = None
        self.senv         = None
        self.dependencies = None
        # Destroy
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
    return []#MAIN_DEPENDENCY_TARGET]

def SCRIPT_DESTROY(instance):
    del instance

