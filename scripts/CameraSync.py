
import pymjin2

class CameraSyncImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
    def __del__(self):
        # Derefer.
        self.c = None
    def nodeToCamera(self):
        print "nodeToCamera"
        pos = self.c.get("node.$SCENE.$NODE.position")[0]
        rot = self.c.get("node.$SCENE.$NODE.rotation")[0]
        self.c.set("camera.position", pos)
        self.c.set("camera.rotation", rot)

class CameraSync(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c = pymjin2.EnvironmentClient(env, "CameraSync")
        self.impl = CameraSyncImpl(self.c)
        # Prepare.
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.impl.nodeToCamera()
        print "{0} CameraSync.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        print "{0} CameraSync.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return CameraSync(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

