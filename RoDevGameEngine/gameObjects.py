from RoDevGameEngine.physics.collider import OBB, colliderTypes
from RoDevGameEngine.physics.rigidbody import Rigidbody
from RoDevGameEngine.transform import transform
from RoDevGameEngine.mesh import Mesh
import glm, numpy as np, keyboard
import OpenGL.GL as GL
    
class gameObject3D:
    def __init__(self, name:str, mesh : Mesh, my_transform : transform = transform(glm.vec3(0,0,0),glm.vec3(0,0,0),glm.vec3(1,1,1))):   
        self.name = name
        
        # Transform data 
        self.transform = my_transform
        if mesh:
            mesh.transform = my_transform
        
        from RoDevGameEngine.script import script

        self.components : list[script] = []

        self.mesh = mesh
        self.__active = True

    def get_active(self):
        return self.__active
    
    def set_active(self, state:bool):
        if isinstance(state, bool):
            self.__active=state

    def set_components(self, my_components : list):
        self.components.extend(my_components)

    def update(self, view_mat : glm.mat4x4, proj_mat : glm.mat4x4, deltatime : float, gameObjects : list):
        if self.__active:
            self.gameObjects = gameObjects

            if self.components:
                for component in self.components:
                    if component.get_active:
                        component.update(deltatime)

            if self.mesh:
                self.mesh.update(view_mat, proj_mat)

    def update_without_components(self, view_mat : glm.mat4x4, proj_mat : glm.mat4x4, deltatime : float, gameObjects : list):
        if self.__active:
            self.gameObjects = gameObjects

            if self.mesh:
                self.mesh.update(view_mat, proj_mat)

            if self.components:
                for component in self.components:
                    if component._always_run:
                        if component.get_active:
                            component.update(deltatime)

    def get_transform(self):
        return self.transform
    
    def get_components(self, component_class):
        components = []
        for component in self.components:
            if isinstance(component, component_class):
                components.append(component)

        return components

