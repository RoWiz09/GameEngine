from RoDevGameEngine import script
from RoDevGameEngine import input
from RoDevGameEngine import gameObjects

class BasicMovement(script.script):
    def __init__(self, parent : gameObjects.gameObject3D):
        super().__init__(parent)   
        self.parent = parent 
        self.parent_transform = self.parent.get_transform()

        self.speed = 4

    def update(self, deltatime):
        super().update(deltatime)

        if input.get_key_down(input.keyCodes.KEY_L):
            self.parent_transform.pos.x += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_J):
            self.parent_transform.pos.x -= self.speed*deltatime
        if input.get_key_down(input.keyCodes.KEY_I):
            self.parent_transform.pos.z += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_K):
            self.parent_transform.pos.z -= self.speed*deltatime
        if input.get_key_down(input.keyCodes.KEY_SPACE):
            self.parent_transform.pos.y += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_RIGHT_CONTROL):
            self.parent_transform.pos.y -= self.speed*deltatime
