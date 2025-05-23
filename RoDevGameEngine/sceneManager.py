import os, zipfile, mouse, time, glfw, ast, PIL.Image, glm, numpy as np, importlib
from RoDevGameEngine import gameObjects
from RoDevGameEngine import transform
from RoDevGameEngine import material
from RoDevGameEngine import shaders
from RoDevGameEngine import input
from RoDevGameEngine import light
from RoDevGameEngine import mesh
from json import load

sceneManager = None

class SceneManager:
    def __init__(self, window, starting_scene_index : int = 0, compiled : bool = True):
        self.window = window
        self.scene = starting_scene_index
        self.sceneData = {}
        self.scenes = []
        self.scene_objects : list[gameObjects.gameObject3D] = []

        self.materials : dict[str,material.Material] = {}

        self.editor_freecam_active = False

        if not compiled:
            materials = self.get_materials("assets")
            for mat in materials:
                with open(mat) as materialFile:
                    materialData = load(materialFile)
                    self.materials[mat] = material.Material(glm.vec4(materialData["color"]),PIL.Image.open(materialData["texture_path"]), materialData["tiling_data"],shaders.BaseShaderProgram())

            scenes = self.get_scenes("assets")
            self.scenes = scenes.copy()
            for scene in scenes:
                with open(scene) as sceneFile:
                    sceneData = load(sceneFile)
                    self.scenes[sceneData["scene_index"]] = scene
                    sceneFile.close()

        elif compiled:
            zipFile = zipfile.ZipFile("./assets.zip")
            textures = {}
            inflist = zipFile.infolist()

            for f in inflist:
                if f.filename.endswith(".png"):
                    ifile = zipFile.open(f)
                    img = PIL.Image.open(ifile)
                    textures[ifile.name] = img

            materials = []
            for mat in zipFile.infolist():
                if mat.filename.endswith(".romat"):
                    materials.append(mat.filename)

            for mat in materials:
                with zipFile.open(mat) as materialFile:
                    materialData = ast.literal_eval(materialFile.read().decode())
                    self.materials["assets\\"+mat.replace("/","\\")] = material.Material(glm.vec4(materialData["color"]), textures[materialData["texture_path"].removeprefix(".\\assets\\").replace("\\","/")], materialData["tiling_data"],shaders.BaseShaderProgram())

            scenes = []
            for scene in zipFile.infolist():
                if scene.filename.endswith(".roscene"):
                    scenes.append(scene.filename)
            
            self.scenes = scenes.copy()
            for scene in scenes:
                with zipFile.open(scene) as sceneFile:
                    sceneData = ast.literal_eval(sceneFile.read().decode())
                    self.scenes[sceneData["scene_index"]] = scene
                    sceneFile.close()

        self.compiled = compiled

        self.load_scene()

        self.last_time = 0

    def get_components(self, gameObject, component_dict : dict[dict[str:list]]):
        components = []
        for component in component_dict.keys():
            component_code = importlib.import_module(component)

            if isinstance(component_dict[component], dict):
                components.append(getattr(component_code, component_dict[component]["class_name"])(gameObject,*component_dict[component].get("vars", [])))
            else:
                for sub_component in range(len(component_dict[component])):
                    components.append(getattr(component_code, component_dict[component][sub_component]["class_name"])(gameObject,*component_dict[component][sub_component].get("vars", [])))
        
        return components
    
    def get_gameobjects(self):
        return self.scene_objects

    def load_scene(self):
        if not self.compiled:
            with open(self.scenes[self.scene]) as sceneFile:
                self.sceneData : dict = load(sceneFile)
            
                self.camera = gameObjects.camera()
                
                for object3d in self.sceneData["3d"].keys():
                    if isinstance(self.sceneData["3d"][object3d], dict):
                        if self.sceneData["3d"][object3d]["mesh_obj"] == "cube":
                            gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                mesh.Mesh.cube_verts, self.materials[self.sceneData["3d"][object3d]["material"]]),
                                my_transform=transform.transform(
                                    glm.vec3(*self.sceneData["3d"][object3d]["pos"]),
                                    glm.vec3(*self.sceneData["3d"][object3d]["rot"]),
                                    glm.vec3(*self.sceneData["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.sceneData["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

                        elif self.sceneData["3d"][object3d]["mesh_obj"] == "none":
                            gameObject = gameObjects.gameObject3D(None,
                                my_transform=transform.transform(
                                    glm.vec3(*self.sceneData["3d"][object3d]["pos"]),
                                    glm.vec3(*self.sceneData["3d"][object3d]["rot"]),
                                    glm.vec3(*self.sceneData["3d"][object3d]["scale"])
                                )
                            )
                            gameObject.set_components(self.get_components(gameObject, self.sceneData["3d"][object3d]['components']))

                            self.scene_objects.append(gameObject)

        else:
            with zipfile.ZipFile("./assets.zip") as zipFile:
                with zipFile.open(self.scenes[self.scene]) as sceneFile:
                    self.sceneData : dict = ast.literal_eval(sceneFile.read().decode().replace("\n", "").replace("\r", ""))

                    self.camera = gameObjects.camera()
                
                    for object3d in self.sceneData["3d"].keys():
                        if isinstance(self.sceneData["3d"][object3d], dict):
                            if self.sceneData["3d"][object3d]["mesh_obj"] == "cube":
                                gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                    mesh.Mesh.cube_verts, self.materials[self.sceneData["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.sceneData["3d"][object3d]["pos"]),
                                        glm.vec3(*self.sceneData["3d"][object3d]["rot"]),
                                        glm.vec3(*self.sceneData["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.sceneData["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                            else:
                                gameObject = gameObjects.gameObject3D(mesh.Mesh(
                                    np.array([],dtype=np.float32), self.materials[self.sceneData["3d"][object3d]["material"]]),
                                    my_transform=transform.transform(
                                        glm.vec3(*self.sceneData["3d"][object3d]["pos"]),
                                        glm.vec3(*self.sceneData["3d"][object3d]["rot"]),
                                        glm.vec3(*self.sceneData["3d"][object3d]["scale"])
                                    )
                                )
                                gameObject.set_components(self.get_components(gameObject, self.sceneData["3d"][object3d]['components']))

                                self.scene_objects.append(gameObject)

                    sceneFile.close()

    def update_scene(self, res : tuple):
        if self.last_time == 0:
            self.last_time = time.time()

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

        for mat in self.materials.values():
            mat.shader_prog.set_lights([light_ for gameobject in get_all_objects() for light_ in gameobject.get_components(light.Light)])

        for object in self.scene_objects:
            objects = self.scene_objects.copy()
            objects.remove(object)
            object.update(view, projection, deltatime, objects)

    def update_scene_editor(self, res : tuple):
        if self.last_time == 0:
            self.last_time = time.time()

        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        if self.editor_freecam_active:
            mx, my = glfw.get_cursor_pos(self.window.window)
            self.camera.process_keyboard(deltatime)
            window_size = glfw.get_window_size(self.window.window)
            self.camera.process_mouse_movement(mx-window_size[0]/2, -my+window_size[1]/2)
            glfw.set_cursor_pos(self.window.window, window_size[0]/2, window_size[1]/2)

        
        if input.get_key_pressed(input.keyCodes.KEY_Z):
            self.editor_freecam_active = not self.editor_freecam_active
            window_size = glfw.get_window_size(self.window.window)
            glfw.set_cursor_pos(self.window.window, window_size[0]/2, window_size[1]/2)

        view = glm.lookAt(self.camera.position, self.camera.position + self.camera.front, self.camera.up)
        projection = glm.perspective(glm.radians(self.camera.zoom), res[0] / res[1], 0.1, 16384.0)

        for mat in self.materials.values():
            mat.shader_prog.set_lights([light_ for gameobject in get_all_objects() for light_ in gameobject.get_components(light.Light)])

        for object in self.scene_objects:
            objects = self.scene_objects.copy()
            objects.remove(object)
            object.update_without_components(view, projection, deltatime, objects)


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
    
def create_scene_manager(starting_scene : int, window, compiled = False):
    global sceneManager
    sceneManager = SceneManager(window, starting_scene, compiled=compiled)
    return sceneManager

def get_all_objects():
    if sceneManager:
        return sceneManager.get_gameobjects()