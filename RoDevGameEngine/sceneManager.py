import os, zipfile, mouse, time, glfw, ast, PIL.Image, glm
from RoDevGameEngine import gameObjects
from RoDevGameEngine import transform
from RoDevGameEngine import material
from RoDevGameEngine import shaders
from RoDevGameEngine import mesh
from json import load

sceneManager = None

class SceneManager:
    def __init__(self, window, starting_scene_index : int = 0, compiled : bool = False):
        self.window = window
        self.scene = starting_scene_index
        self.sceneData = {}
        self.scenes = []
        self.scene_objects : list[gameObjects.gameObject3D] = []

        self.materials = {}

        if not compiled:
            materials = self.get_materials("assets")
            for mat in materials:
                with open(mat) as materialFile:
                    materialData = load(materialFile)
                    self.materials[mat] = material.Material(glm.vec4(materialData["color"]),PIL.Image.open(materialData["texture_path"]),shaders.BaseShaderProgram())

            scenes = self.get_scenes("assets")
            self.scenes = scenes.copy()
            for scene in scenes:
                with open(scene) as sceneFile:
                    sceneData = load(sceneFile)
                    self.scenes.insert(sceneData["scene_index"], scene)
                    self.scenes = self.scenes[:len(self.scenes)-1]
                    sceneFile.close()

        self.load_scene()

        self.last_time = 0

    def load_scene(self):
        with open(self.scenes[self.scene]) as sceneFile:
            self.sceneData : dict = load(sceneFile)
        
            self.camera = gameObjects.camera()
            
            for object3d in self.sceneData["3d"].keys():
                if isinstance(self.sceneData["3d"][object3d], dict):
                    if self.sceneData["3d"][object3d]["mesh_obj"] == "cube":
                        print("cube")
                        self.scene_objects.append(gameObjects.gameObject3D(mesh.Mesh(
                            mesh.Mesh.cube_verts, self.materials[self.sceneData["3d"][object3d]["material"]]),
                            my_transform=transform.transform(
                                glm.vec3(*self.sceneData["3d"][object3d]["pos"]),
                                glm.vec3(*self.sceneData["3d"][object3d]["rot"]),
                                glm.vec3(*self.sceneData["3d"][object3d]["scale"])
                            )
                        ))

    def update_scene(self, res : tuple):
        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        mx, my = glfw.get_cursor_pos(self.window.window)
        self.camera.process_keyboard(deltatime)
        window_size = glfw.get_window_size(self.window.window)
        self.camera.process_mouse_movement(mx-window_size[0]/2, -my+window_size[1]/2)
        glfw.set_cursor_pos(self.window.window, window_size[0]/2, window_size[1]/2)

        view = glm.lookAt(self.camera.position, self.camera.position + self.camera.front, self.camera.up)
        projection = glm.perspective(glm.radians(self.camera.zoom), res[0] / res[1], 0.1, 16384.0)

        for object in self.scene_objects:
            object.update(view, projection)

    def get_scenes(self, path):
        files = []
        for file in os.listdir(path):
            if os.path.isdir(path+"\\"+file):
                subfiles = self.get_scenes(path+"\\"+file)
                files.extend(subfiles)
            elif file.endswith('.roscene'):
                files.append(path+"\\"+file)

        return files
    
    def get_materials(self, path):
        files = []
        for file in os.listdir(path):
            if os.path.isdir(path+"\\"+file):
                subfiles = self.get_materials(path+"\\"+file)
                files.extend(subfiles)
            elif file.endswith('.romat'):
                files.append(path+"\\"+file)
        return files
    
def create_scene_manager(starting_scene : int, window):
    global sceneManager
    sceneManager = SceneManager(window, starting_scene)
    return sceneManager