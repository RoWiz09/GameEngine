from RoDevGameEngine import script

import glm, numpy as np

class editor_camera(script.script):
    """
        A non-physical object in the game's scene. 
    """
    def __init__(self, parent, script_path):
        super().__init__(parent, script_path)
        
        self.offset = glm.vec3(0.0, 0.0, 0.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.vec3()
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90
        self.pitch = 0
        self.speed = 5 
        self.sensitivity = 0.5
        self.zoom = 45.0
        self.update_vectors()

    def update_vectors(self):
        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
    
    def update(self, deltatime):
        self.update_vectors()

        return super().update(deltatime)

