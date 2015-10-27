
import pymjin2

class TrackNodePositionListenerScene(pymjin2.ComponentListener):
    def __init__(self, impl):
        pymjin2.ComponentListener.__init__(self)
        self.impl = impl
    def __del__(self):
        self.impl = None
    def onComponentStateChange(self, st):
        for k in st.keys:
            print "TrackNodePosition", k, st.value(k)

class TrackNodePosition:
    def __init__(self, sceneName, nodeName, scene, action):
        print "TrackNodePosition({0}). START. scene: {1} node: {2}".format(
            id(self),
            sceneName,
            nodeName)
        # Refer.
        self.sceneName = sceneName
        self.nodeName  = nodeName
        self.scene     = scene
        # Create.
        self.listenerScene = TrackNodePositionListenerScene(None)
        # Prepare.
        key = "node.{0}.{1}.position".format(sceneName, nodeName)
        self.scene.addListener([key], self.listenerScene)
    def __del__(self):
        # Tear down.
        self.scene.removeListener(self.listenerScene)
        # Destroy.
        del self.listenerScene
        # Derefer.
        self.scene = None
        print "TrackNodePosition({0}). FINISH. scene: {1} node: {2}".format(
            id(self),
            self.sceneName,
            self.nodeName)

def SCRIPT_CREATE(sceneName, nodeName, scene, action):
    return TrackNodePosition(sceneName, nodeName, scene, action)

def SCRIPT_DESTROY(instance):
    del instance

