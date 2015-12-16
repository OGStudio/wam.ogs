
import pymjin2

class MainImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.mousePos = None
    def __del__(self):
        # Derefer.
        self.c = None
    def onMousePosition(self, key, value):
        self.mousePos = value[0]
    def onNodeSelection(self, key, value):
        print "onNodeSelection", key, value
    def onNodeSelectionShortcut(self, key, value):
        self.c.set("selector.$SCENE.position", self.mousePos)

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c    = pymjin2.EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        # Prepare.
        self.c.setConst("SCENE", sceneName)
        # Listen to node selection shortcut.
        self.c.listen("shortcut.node.select.active",
                      "1",
                      self.impl.onNodeSelectionShortcut)
        # Listen to mouse position.
        self.c.listen("mouse.positionOrig", None, self.impl.onMousePosition)
        # Listen to target selection.
        self.c.listen("node.$SCENE..selected", "1", self.impl.onNodeSelection)
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        print "{0} Main.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

