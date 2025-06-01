from RoDevGameEngine.physics import rigidbody
from RoDevGameEngine.physics import collider
from RoDevGameEngine.physics import raycast

from RoDevGameEngine import gameObjects
from RoDevGameEngine import script
from RoDevGameEngine import input

from RoDevGameEngine import sceneManager

from glm import vec3

class BasicMovement(script.script):
    def __init__(self, parent : gameObjects.gameObject3D, script_path):
        super().__init__(parent, script_path)

        self.__rigidbody = None

        self.speed = 4

    def update(self, deltatime):
        super().update(deltatime)

        if input.get_key_pressed(input.keyCodes.KEY_1):
            sceneManager.sceneManager.swap_scene_idx(1)
        elif input.get_key_pressed(input.keyCodes.KEY_2):
            sceneManager.sceneManager.swap_scene_idx(2)
        elif input.get_key_pressed(input.keyCodes.KEY_0):
            sceneManager.sceneManager.swap_scene_idx(0)

        vel = [0, 0, 0]

        if input.get_key_down(input.keyCodes.KEY_L):
            vel[0] += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_J):
            vel[0]-= self.speed*deltatime
        if input.get_key_down(input.keyCodes.KEY_I):
            vel[2] += self.speed*deltatime
        elif input.get_key_down(input.keyCodes.KEY_K):
            vel[2] -= self.speed*deltatime

        if not self.__rigidbody:
            self.__rigidbody:rigidbody.Rigidbody = self.parent.get_components(rigidbody.Rigidbody)[0]

        if input.get_key_pressed(input.keyCodes.KEY_SPACE):
            self.__rigidbody.apply_force(vec3(0, 100, 0))

        if input.get_key_pressed(input.keyCodes.KEY_LEFT_BRACKET):
            fin_pos = vec3(self.parent.get_transform().pos)
            fin_pos.x -= self.parent.get_transform().scale.x/2
            fin_pos.y += self.parent.get_transform().scale.y/2
            fin_pos.z += self.parent.get_transform().scale.z/2
            raycast.raycast(fin_pos,500,vec3(0,-90,0), self.parent.get_components(collider.OBB)).pos

        self.__rigidbody.move(vel)
        