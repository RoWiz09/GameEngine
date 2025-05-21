from RoDevGameEngine import gameObjects
from RoDevGameEngine.physics import rigidbody
from RoDevGameEngine import script
from RoDevGameEngine import input

from glm import vec3

class BasicMovement(script.script):
    def __init__(self, parent : gameObjects.gameObject3D):
        super().__init__(parent)   
        self.parent = parent 
        self.parent_transform = self.parent.get_transform()

        self.rigidbody = None

        self.speed = 4

    def update(self, deltatime):
        super().update(deltatime)

        vel = [0, 0, 0]

        if input.get_key_down(input.keyCodes.KEY_L):
            vel[0] += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_J):
            vel[0]-= self.speed*deltatime
        if input.get_key_down(input.keyCodes.KEY_I):
            vel[2] += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_K):
            vel[2] -= self.speed*deltatime

        if not self.rigidbody:
            self.rigidbody:rigidbody.Rigidbody = self.parent.get_components(rigidbody.Rigidbody)[0]

        if input.get_key_pressed(input.keyCodes.KEY_SPACE):
            self.rigidbody.apply_force(vec3(0, 999, 0))

        self.rigidbody.move(vel)
