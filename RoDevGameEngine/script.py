from typing_extensions import deprecated

class script:
    def __init__(self, parent, script_path:str):
        self._path = script_path

        self._always_run = False 
        from RoDevGameEngine.gameObjects import gameObject3D
        if isinstance(parent, gameObject3D):
            self.parent = parent
        else:
            raise self.InvalidParentError("The parent value must be of type GameObject3D. This is most likely our fault, but possibly yours if you edited the scenefile manually.")
        
        self.__enabled = True

    class InvalidParentError(Exception):
        def __init__(self, *args):
            super().__init__(*args)
    
    @deprecated("Use __init__ instead")
    def on_scene_init(self):
        pass

    @type
    def OBB(self):
        from RoDevGameEngine.physics.collider import OBB
        return OBB
    
    @property
    def get_active(self):
        return self.__enabled
    
    def set_active(self, state:bool):
        if isinstance(state, bool):
            self.__enabled = state
    
    def on_scene_unload(self):
        pass

    def update(self, deltatime):
        pass

    def on_collision_enter(self, my_obb:OBB, other:OBB, collision_info:dict):
        pass

    def on_trigger_enter(self, my_obb:OBB, other:OBB):
        pass

    def while_trigger(self, my_obb:OBB, other:OBB):
        pass

    def on_trigger_exit(self, my_obb:OBB, other:OBB):
        pass

class dataContainer:
    def __init__(self, **kwargs):
        pass
