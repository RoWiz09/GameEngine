from RoDevGameEngine import script
from RoDevGameEngine import input

import glm, numpy as np, glfw

class editor_camera(script.script):
    """
        A free moving camera for the editor.

        It is a script, and it technically can be used in game, but it is not recommended.
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
        """ Update the camera's vectors. Do not call this function manually, instead use update(). """
        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def process_keyboard(self, delta_time):
        """ Process keyboard input. """
        velocity = self.speed * delta_time
        if input.get_key_down(input.keyCodes.KEY_W):
            self.position += self.front * velocity
        if input.get_key_down(input.keyCodes.KEY_S):
            self.position -= self.front * velocity
        if input.get_key_down(input.keyCodes.KEY_A):
            self.position -= self.right * velocity
        if input.get_key_down(input.keyCodes.KEY_D):
            self.position += self.right * velocity

    def process_mouse_movement(self, constrain_pitch=True):
        """ Process mouse movement input. """
        from RoDevGameEngine.window import window_
        x_offset, y_offset = input.get_mouse_movement(window_)

        x_offset *= self.sensitivity
        y_offset *= self.sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_vectors()

    def update(self, deltatime):
        """ Update the camera's vectors. """
        self.process_keyboard(deltatime)
        self.process_mouse_movement()

        self.update_vectors()

        return super().update(deltatime)
    
class camera(script.script):
    def __init__(self, parent, script_path):
        """
            A camera that can be used in game.
            
            Most of the time, you will want to use this camera instead of the editor camera.

            Args:
                parent (gameobject): The gameobject that this script is attached to.
                script_path (str): The path to the script file.
        """
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
        """ Update the camera's vectors. Do not call this function manually, instead use update(). """
        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def update(self, deltatime):
        """ Update the camera's vectors. """
        self.update_vectors()

        return super().update(deltatime)
    
    def get_view_matrix(self):
        """ Returns the view matrix calculated using Euler Angles and the LookAt Matrix """
        return glm.lookAt(self.position, self.position + self.front, self.up)
    
    def get_projection_matrix(self):
        """ Returns the projection matrix using perspective projection. """
        from RoDevGameEngine.window import window_
        aspect_ratio = glfw.get_window_size(window_)[0] / glfw.get_window_size(window_)[1]

        return glm.perspective(glm.radians(self.zoom), aspect_ratio, 0.1, 100.0)
    


