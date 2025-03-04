from typing_extensions import deprecated

class script:
    def __init__(self, parent):
        self.parent = parent
    
    @deprecated("Use __init__ instead")
    def on_scene_init(self):
        pass
    
    def on_scene_unload(self):
        pass

    def update(self, deltatime):
        pass
