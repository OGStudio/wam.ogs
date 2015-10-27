
import pymjin2

class TrackNodeLifeTime:
    def __init__(self, sceneName, nodeName, scene, action):
        print "TrackNodeLifeTime({0}). START. scene: {1} node: {2}".format(
            id(self),
            sceneName,
            nodeName)
        # Refer.
        self.sceneName = sceneName
        self.nodeName  = nodeName
    def __del__(self):
        print "TrackNodeLifeTime({0}). FINISH. scene: {1} node: {2}".format(
            id(self),
            self.sceneName,
            self.nodeName)

def SCRIPT_CREATE(sceneName, nodeName, scene, action):
    return TrackNodeLifeTime(sceneName, nodeName, scene, action)

def SCRIPT_DESTROY(instance):
    del instance

